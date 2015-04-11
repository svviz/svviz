import collections
import itertools
import math
import re
from svviz.svg import SVG
from svviz import utilities
from svviz import variants

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

    def relpixels(self, g):
        dist = g / float(self.basesPerPixel)
        return dist


class Axis(object):
    def __init__(self, scale, variant, allele):
        self.scale = scale
        self.allele = allele
        self.variant = variant
        self.segments = variant.segments(allele)
        self.height = 75


    def baseHeight(self):
        return 75

    def render(self, scaleFactor=1.0, spacing=1.0, height=None, thickerLines=False):
        self.height = height
        if height == None:
            self.height = 75 * scaleFactor

        self.svg = SVG(self.scale.pixelWidth, self.height, yrelto="top", headerExtras="""preserveAspectRatio="none" """)
        self.svg.rect(0, 35*scaleFactor, self.scale.pixelWidth, 3*scaleFactor)

        for tick in self.getTicks():
            x = self.scale.topixels(tick)
            self.svg.rect(x, 35*scaleFactor, 1*scaleFactor, 15*scaleFactor, fill="black")
            label = tick
            if tick > 1e6:
                label = "{:.1f}MB".format(tick/1e6)
            elif tick > 1e3:
                label = "{:.1f}KB".format(tick/1e3)

            if x < 50:
                x = 50
            elif x > self.scale.pixelWidth - 50:
                x = self.scale.pixelWidth - 50
            extras = {}
            if thickerLines:
                extras["font-weight"] = "bold"
            self.svg.text(x, self.height-4*scaleFactor, label, size=18*scaleFactor, **extras)

        if self.segments is not None:
            curOffset = 0
            for segment in self.segments:
                start = curOffset
                end = self.scale.relpixels(len(segment)) + curOffset
                curOffset = end

                # print " :: ", start, end, segment.end-segment.start, curOffset
                arrowDirection = "right"

                if segment.strand == "-":
                    start, end = end, start
                    arrowDirection = "left"

                y = 35*scaleFactor

                self.svg.line(start, y, end, y, stroke=segment.color(), **{"stroke-width":8*scaleFactor})
                self.svg.lineWithInternalArrows(start, y, end, y, stroke=segment.color(), direction=arrowDirection,
                    arrowKwdArgs={"class":"scaleArrow"}, **{"stroke-width":3*scaleFactor})

        previousPosition = None
        for vline in self.variant.getRelativeBreakpoints(self.allele):
            thickness = 1*scaleFactor
            if thickerLines:
                thickness *= 2
            x = self.scale.topixels(vline)
            self.svg.line(x, 20*scaleFactor, x, 55*scaleFactor, 
                stroke="black", **{"stroke-width":thickness})
            
            if previousPosition is None or vline-previousPosition > 250:     
                self.svg.text(x-(scaleFactor/2.0), 18*scaleFactor, "breakpoint", size=18*scaleFactor, fill="black")
            previousPosition = vline

        return str(self.svg)

    def getTicks(self):
        start = self.scale.start
        end = self.scale.end
        width = end - start

        res = (10 ** round(math.log10(end - start))) / 10.0
        if width / res > 15:
            res *= 2.5
        elif width / res < 5:
            res /= 2.0

        roundStart = start - (start%res)
        ticks = []

        for i in range(int(roundStart), end, int(res)):
            ticks.append(i)

        return ticks

class ReadRenderer(object):
    def __init__(self, rowHeight, scale, chrom, thickerLines=False):
        self.rowHeight = rowHeight
        self.svg = None
        self.scale = scale
        self.chrom = chrom
        self.thickerLines = thickerLines

        self.nucColors = {"A":"blue", "C":"orange", "G":"green", "T":"black", "N":"gray"}
        self.colorsByStrand = {"+":"purple", "-":"red"}
        self.insertionColor = "cyan"
        self.deletionColor = "gray"
        self.overlapColor = "lime"

    def render(self, alignmentSet):
        yoffset = alignmentSet.yoffset
        pstart = self.scale.topixels(alignmentSet.start)
        pend = self.scale.topixels(alignmentSet.end)

        thinLineWidth = 5
        self.svg.rect(pstart, yoffset-(self.rowHeight/2.0)+thinLineWidth/2.0, pend-pstart, thinLineWidth, fill="#DDDDDD")

        positionCounts = collections.Counter()

        for alignment in alignmentSet.getAlignments():
            for position in range(alignment.start, alignment.end+1):
                positionCounts[position] += 1

            pstart = self.scale.topixels(alignment.start)
            pend = self.scale.topixels(alignment.end)

            if self.thickerLines:
                # extra "bold":
                ystart = yoffset+3
                height = self.rowHeight+6
            else:
                ystart = yoffset
                height = self.rowHeight

            self.svg.rect(pstart, ystart, pend-pstart, height, fill=self.colorsByStrand[alignment.strand], 
                          **{"class":"read", "data-cigar":alignment.cigar,"data-readid":alignment.name})

            colorCigar = True
            if colorCigar:
                self._drawCigar(alignment, yoffset)
                
        highlightOverlaps = True
        if highlightOverlaps:
            self._highlightOverlaps(positionCounts, yoffset)


    def _drawCigar(self, alignment, yoffset):
        eachNuc = False # this gets to be computationally infeasible to display in the browser
        pattern = re.compile('([0-9]*)([MIDNSHP=X])')

        genomePosition = alignment.start
        sequencePosition = 0

        for length, code in pattern.findall(alignment.cigar):
            length = int(length)
            if code == "M":
                for i in range(length):
                    curstart = self.scale.topixels(genomePosition+i)
                    curend = self.scale.topixels(genomePosition+i+1)

                    color = self.nucColors[alignment.seq[sequencePosition+i]]

                    alt = alignment.seq[sequencePosition+i]
                    ref = self.chrom.seq[genomePosition+i]
                    if eachNuc or alt!=ref:
                        self.svg.rect(curstart, yoffset, curend-curstart, self.rowHeight, fill=color)

                sequencePosition += length
                genomePosition += length
            elif code in "D":
                curstart = self.scale.topixels(genomePosition)
                curend = self.scale.topixels(genomePosition+length+1)
                self.svg.rect(curstart, yoffset, curend-curstart, self.rowHeight, fill=self.deletionColor)

                genomePosition += length
            elif code in "IHS":
                curstart = self.scale.topixels(genomePosition-0.5)
                curend = self.scale.topixels(genomePosition+0.5)
                self.svg.rect(curstart, yoffset, curend-curstart, self.rowHeight, fill=self.insertionColor)

                sequencePosition += length

    def _highlightOverlaps(self, positionCounts, yoffset):
        overlapSegments = [list(i[1]) for i in itertools.groupby(sorted(positionCounts), lambda x: positionCounts[x]) if i[0] > 1]

        for segment in overlapSegments:
            start = min(segment)
            end = max(segment)

            curstart = self.scale.topixels(start)
            curend = self.scale.topixels(end)

            self.svg.rect(curstart, yoffset, curend-curstart, self.rowHeight, fill=self.overlapColor)


class Track(object):
    def __init__(self, chrom, alignmentSets, height, width, gstart, gend, variant, allele, thickerLines):
        self.chrom = chrom
        self.height = height
        self.width = width

        self.gstart = gstart
        self.gend = gend
        self.scale = Scale(self.gstart, self.gend, width)

        self.rowHeight = 5
        self.rowMargin = 1

        self.readRenderer = ReadRenderer(self.rowHeight, self.scale, self.chrom, thickerLines)

        self.alignmentSets = alignmentSets

        self.svg = None
        self.rendered = None

        self.variant = variant
        self.allele = allele

        self.rows = []
        self._axis = None

        self.xmin = None
        self.xmax = None

        self.thickerLines = thickerLines


    def findRow(self, start, end):
        for currow in range(len(self.rows)):
            if self.rows[currow] is None or (self.scale.topixels(start) - self.scale.topixels(self.rows[currow])) >= 2:
                self.rows[currow] = end
                break
        else:
            self.rows.append(end)
            currow = len(self.rows)-1

        return currow

    def getAlignments(self):
        # check which reads are overlapping (self.gstart, self.gend)
        return sorted(self.alignmentSets, key=lambda x: x.start)

    def dolayout(self):
        self.rows = [None]#*numRows

        self.xmin = 1e100
        self.xmax = 0

        for alignmentSet in self.getAlignments():
            # if len(alignmentSet.getAlignments()) < 2:
                # continue

            currow = self.findRow(alignmentSet.start, alignmentSet.end)
            yoffset = (self.rowHeight+self.rowMargin) * currow
            alignmentSet.yoffset = yoffset

            self.xmin = min(self.xmin, self.scale.topixels(alignmentSet.start))
            self.xmax = max(self.xmax, self.scale.topixels(alignmentSet.end))

        self.height = (self.rowHeight+self.rowMargin) * len(self.rows)

    def render(self):        
        if len(self.getAlignments()) == 0:
            xmiddle = (self.scale.topixels(self.gend)-self.scale.topixels(self.gstart))/2.0
            self.height = xmiddle/20.0

            self.svg = SVG(self.width, self.height)
            self.svg.text(xmiddle, self.height*0.05, "No reads found", size=self.height*0.9, fill="#999999")
            self.rendered = self.svg.asString()
            return self.rendered

        self.dolayout()

        self.svg = SVG(self.width, self.height)
        self.readRenderer.svg = self.svg

        for alignmentSet in self.getAlignments():
            self.readRenderer.render(alignmentSet)

        lineWidth = 1 if not self.thickerLines else 3
        lineWidth = lineWidth * ((self.xmax-self.xmin)/1200.0)
        for vline in self.variant.getRelativeBreakpoints(self.allele):
            x = self.scale.topixels(vline)
            y1 = -20
            y2 = self.height+20
            self.svg.line(x, y1, x, y2, stroke="black", **{"stroke-width":lineWidth})

        self.svg.rect(0, self.svg.height+20, self.scale.topixels(self.gend)-self.scale.topixels(self.gstart), 
            self.height+40, opacity=0.0, zindex=0)
        self.rendered = str(self.svg)

        return self.rendered


class AnnotationTrack(object):
    def __init__(self, annotationSet, scale, variant, allele):
        self.annotationSet = annotationSet
        self.scale = scale
        self.height = None
        self.variant = variant
        self.allele = allele
        self.segments = variants.mergedSegments(variant.segments(allele))

        self._annos = None
        self.rows = [None]
        self.svg = None

        self.rowheight = 20

    def _topixels(self, gpos, segment, psegoffset):
        if segment.strand == "+":
            pos = self.scale.relpixels(gpos - segment.start) + psegoffset
        elif segment.strand == "-":
            pos = self.scale.relpixels(segment.end - gpos) + psegoffset
        return pos

    def findRow(self, start, end):
        for currow in range(len(self.rows)):
            if self.rows[currow] is None or (start - self.rows[currow]) >= 2:
                self.rows[currow] = end
                break
        else:
            self.rows.append(end)
            currow = len(self.rows)-1

        return currow

    def baseHeight(self):
        if self._annos is not None and len(self._annos) == 0:
            return 0
        return ((len(self.rows)+2) * self.rowheight) + 20

    def dolayout(self, scaleFactor, spacing):
        # coordinates are in pixels not base pairs
        self.rows = [None]

        segmentStart = 0

        self._annos = []
        for segment in self.segments:
            curWidth = len(segment)
            curAnnos = self.annotationSet.getAnnotations(segment.chrom, segment.start, segment.end, clip=True)
            if segment.strand == "-":
                curAnnos = sorted(curAnnos, key=lambda x:x.end, reverse=True)

            for anno in curAnnos:
                start = self._topixels(anno.start, segment, segmentStart)
                end = self._topixels(anno.end, segment, segmentStart)
                if end < start:
                    start, end = end, start
                textLength = len(anno.name)*self.rowheight/1.0*scaleFactor*spacing
                rowNum = self.findRow(start, end+textLength)

                anno.coords = {}
                anno.coords["row"] = rowNum
                anno.coords["start"] = start
                anno.coords["end"] = end
                anno.coords["strand"] = anno.strand if segment.strand=="+" else utilities.switchStrand(anno.strand)

                self._annos.append(anno)

            segmentStart += self.scale.relpixels(curWidth)

    def render(self, scaleFactor=1.0, spacing=1, height=None, thickerLines=False):
        self.dolayout(scaleFactor, spacing)

        self.height = self.baseHeight()*scaleFactor
        self.svg = SVG(self.scale.pixelWidth, self.height)

        for anno in self._annos:
            color = "blue" if anno.coords["strand"] == "+" else "darkorange"
            y = ((anno.coords["row"]+1) * self.rowheight + 20) * scaleFactor
            width = anno.coords["end"] - anno.coords["start"]

            self.svg.rect(anno.coords["start"], y, width, self.rowheight*scaleFactor, fill=color)
            self.svg.text(anno.coords["end"]+(self.rowheight/2.0), y-((self.rowheight-1)*scaleFactor), 
                anno.name, size=(self.rowheight-2)*scaleFactor, anchor="start", fill=color)

        for vline in self.variant.getRelativeBreakpoints(self.allele):
            x = self.scale.topixels(vline)-scaleFactor/2.0
            y1 = 0
            y2 = self.height
            thickness = 1*scaleFactor
            if thickerLines:
                thickness *= 2
            self.svg.line(x, y1, x, y2, stroke="black", **{"stroke-width":thickness})
            # self.svg.rect(self.scale.topixels(vline)-scaleFactor/2.0, self.height, scaleFactor, self.height+40, fill="black")


