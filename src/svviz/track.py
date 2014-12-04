import collections
import itertools
import re
from svg import SVG


class Chromosome(object):
    def __init__(self, length):
        self.length = length
    def getSeq(self, start, end):
        pass

class ChromosomePart(Chromosome):
    def __init__(self, seq):
        self.length = len(seq)
        self.seq = seq.upper()
    def getSeq(self, start, end):
        return self.seq[start:end+1]

class Scale(object):
    def __init__(self, start, end, pixelWidth):
        self.start = start
        self.end = end
        self.pixelWidth = pixelWidth
        self.basesPerPixel = (end - start + 1) / float(pixelWidth)

    def topixels(self, g, clip=False):
        pos = (g-self.start) /float(self.basesPerPixel)
        if clip:
            if pos < 0:
                return 0
            elif pos > self.pixelWidth:
                return self.pixelWidth
        return pos

class ReadRenderer(object):
    def __init__(self, rowHeight, scale, chrom):
        self.rowHeight = rowHeight
        self.svg = None
        self.scale = scale
        self.chrom = chrom

        self._nucColors = {"A":"blue", "C":"orange", "G":"green", "T":"black", "N":"gray"}

    def render(self, alignmentSet):
        yoffset = alignmentSet.yoffset
        pstart = self.scale.topixels(alignmentSet.start)
        pend = self.scale.topixels(alignmentSet.end)
        self.svg.rect(pstart, yoffset-(self.rowHeight/2.0), pend-pstart, 0.25, fill="gray")

        positionCounts = collections.Counter()

        for alignment in alignmentSet.getAlignments():
            for position in range(alignment.start, alignment.end+1):
                positionCounts[position] += 1

            pstart = self.scale.topixels(alignment.start)
            pend = self.scale.topixels(alignment.end)

            color = "purple"
            if alignment.strand == "-":
                color = "red"

            # color = alignmentSet.color
            # color = "gray"

            self.svg.rect(pstart, yoffset, pend-pstart, self.rowHeight, fill=color, **{"class":"read", "data-cigar":alignment.cigar,
                "data-readid":alignment.name#, "opacity":0.75
                })

            colorCigar = False
            eachNuc = False
            if colorCigar:

                # print "\n"*3
                # print alignment.cigar
                # print alignment.seq
                # out = []
                # out2 = []

                pattern = re.compile('([0-9]*)([MIDNSHP=X])')

                genomePosition = alignment.start
                sequencePosition = 0

                # print alignment.name
                # print alignment.seq
                # print self.chrom.seq[genomePosition:genomePosition+len(alignment.seq)]
                # print ""

                for length, code in pattern.findall(alignment.cigar):
                    length = int(length)
                    if code == "M":
                        for i in range(length):
                            curstart = self.scale.topixels(genomePosition+i)
                            curend = self.scale.topixels(genomePosition+i+1)

                            color = self._nucColors[alignment.seq[sequencePosition+i]]

                            alt = alignment.seq[sequencePosition+i]
                            ref = self.chrom.seq[genomePosition+i]
                            if eachNuc or alt!=ref:
                                self.svg.rect(curstart, yoffset, curend-curstart, self.rowHeight, fill=color)

                                # out.append()
                                # out2.append(self.chrom.seq[genomePosition+i])
                        sequencePosition += length
                        genomePosition += length
                    elif code in "D":
                        curstart = self.scale.topixels(genomePosition)
                        curend = self.scale.topixels(genomePosition+length+1)
                        color = "white"
                        self.svg.rect(curstart, yoffset, curend-curstart, self.rowHeight, fill=color)

                        genomePosition += length
                    elif code in "IHS":
                        curstart = self.scale.topixels(genomePosition-0.5)
                        curend = self.scale.topixels(genomePosition+0.5)
                        color = "red"
                        self.svg.rect(curstart, yoffset, curend-curstart, self.rowHeight, fill=color)

                        sequencePosition += length
                        # out.append("-"*length)

                # print "".join(out)
                # print "".join(out2)

        highlightOverlaps = True
        if highlightOverlaps:
            overlapSegments = [list(i[1]) for i in itertools.groupby(sorted(positionCounts), lambda x: positionCounts[x]) if i[0] > 1]

            for segment in overlapSegments:
                start = min(segment)
                end = max(segment)

                curstart = self.scale.topixels(start)
                curend = self.scale.topixels(end)

                self.svg.rect(curstart, yoffset, curend-curstart, self.rowHeight, fill="lime")

class Track(object):
    def __init__(self, chrom, alignmentSets, height, width, gstart, gend, vlines=None):
        self.chrom = chrom
        self.height = height
        self.width = width

        # self.gstart = 0
        # self.gend = chrom.length
        self.gstart = gstart
        self.gend = gend
        self.scale = Scale(self.gstart, self.gend, width)

        self.rowHeight = 5
        self.rowMargin = 1

        self.readRenderer = ReadRenderer(self.rowHeight, self.scale, self.chrom)

        self.alignmentSets = alignmentSets

        self.svg = None
        self.rendered = None

        if vlines is None:
            vlines = []
        self.vlines = vlines

        self.rows = []


    def findRow(self, start, end):
        for currow in range(len(self.rows)):
            if self.rows[currow] is None or self.scale.topixels(start) - self.scale.topixels(self.rows[currow]) >= 2:
                self.rows[currow] = end
                break
        else:
            self.rows.append(end)
            currow = len(self.rows)
        # could dynamically grow the number of rows here...

        return currow

    def getAlignments(self):
        # check which reads are overlapping (self.gstart, self.gend)
        return sorted(self.alignmentSets, key=lambda x: x.start)

    def dolayout(self):
        numRows = int(self.height/(self.rowHeight+self.rowMargin))
        self.rows = [None]#*numRows

        for alignmentSet in self.getAlignments():
            # if len(alignmentSet.getAlignments()) < 2:
                # continue
            currow = self.findRow(alignmentSet.start, alignmentSet.end)
            yoffset = (self.rowHeight+self.rowMargin) * currow
            alignmentSet.yoffset = yoffset

        self.height = (self.rowHeight+self.rowMargin) * len(self.rows)

        print "HEIGHT:", self.height


    def render(self):
        self.dolayout()

        self.svg = SVG(self.width, self.height)
        self.readRenderer.svg = self.svg

        for alignmentSet in self.getAlignments():
            # if len(alignmentSet.getAlignments()) < 2:
            #     continue
            self.readRenderer.render(alignmentSet)

        for vline in self.vlines:
            self.svg.rect(self.scale.topixels(vline), self.svg.height+20, 1, self.height+40, fill="black")

        self.rendered = str(self.svg)

        return self.rendered



