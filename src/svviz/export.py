import collections
import logging
import subprocess
import tempfile


class TrackCompositor(object):
    def __init__(self, dataHub, title=None):
    # def __init__(self, width, title=None): 
        self.dataHub = dataHub
        self.sections = collections.OrderedDict()
        self.width = 1200
        self.title = title
        self.descriptions = []

        self.marginTopBottom = 20
        self.sectionLabelHeight = 32
        self.betweenSectionHeight = 30
        self.trackLabelHeight = 20

        self._fromDataHub()

    def _fromDataHub(self):
        if self.title is None:
            self.title = str(self.dataHub.variant)
        # counts = self.dataHub.getCounts()
        # for name, curcounts in counts.iteritems():
        #     self.descriptions.append("{}: {} {} {}".format(name, curcounts["alt"], curcounts["ref"], curcounts["amb"]))

        for longAlleleName in ["Alternate Allele", "Reference Allele"]:
            allele = longAlleleName[:3].lower()

            sampleNames = self.dataHub.samples.keys()
            tracks = [sample.tracks[allele] for sample in self.dataHub]

            self.addTracks(longAlleleName, sampleNames, tracks, allele)

    def addTracks(self, section, names, tracks, allele):
        alleleTracks = self.dataHub.alleleTracks[allele]
        segments = segments=self.dataHub.variant.segments(allele)
        alleleLength = self.dataHub.variant.getLength(allele)

        for track in tracks:
            track.render()
        xmin = [track.xmin for track in tracks if track.xmin is not None]
        xmin = min(xmin) if len(xmin) > 0 else 0
        # xmin = min(max(0, len(segments[0])-100), xmin)

        xmax = [track.xmax for track in tracks if track.xmax is not None]
        xmax = max(xmax) if len(xmax) > 0 else 500
        # xmax = max(alleleLength-len(segments[-1])+100, xmax)
        # xmax = min(xmax, alleleLength)

        print xmin, xmax

        hasTrackWithReads = False
        width = 500
        if xmin is not None:
            width = xmax - xmin
            xmin -= width * 0.05
            width *= 1.1

        for track, name in zip(tracks, names):
            if len(track.alignmentSets) == 0:
                height = 20
                viewbox = '0 0 {width} {height}" preserveAspectRatio="xMinYMin'.format(width=track.width, height=track.height)
            else:
                hasTrackWithReads = True
                # this is for proportional scaling                
                # height = float(track.height+40) * self.width / width
                # preserveAspectRatio="xMinYMin"
                height = float(track.height+40)/2.0
                preserveAspectRatio="none"

                viewbox = '{xmin} -20 {width} {height}" preserveAspectRatio="{par}'.format(xmin=xmin, 
                    width=width, height=track.height+40, par=preserveAspectRatio)

            self.addTrackSVG(section, name, track.svg.asString("export"), height=height, viewbox=viewbox)

        if hasTrackWithReads:
            scaleFactor = width * 0.0005
            for name, track in alleleTracks.iteritems():
                track.render(scaleFactor=scaleFactor)
                height = track.height/scaleFactor
                viewbox = '{xmin} 0 {width} {height}" preserveAspectRatio="xMinYMin'.format(xmin=xmin, width=width, height=height)
                svg = track.svg.asString("export")

                self.addTrackSVG(section, name, svg, height=height, viewbox=viewbox)

        # if includeAxis and hasTrackWithReads:
        #     scaleFactor = width * 0.0005

        #     axis = track.getAxis()
        #     baseHeight = axis.height
        #     axis.height = baseHeight*scaleFactor
        #     viewbox = "{xmin} 0 {width} {height}".format(xmin=xmin, width=width, height=baseHeight)
 
        #     axis.render(scaleFactor=scaleFactor)
        #     svg = axis.svg.asString("export")

        #     self.addTrackSVG(section, "xaxis", svg, height=75, viewbox=viewbox)
        #     axis.height = baseHeight

    def addTrackSVG(self, section, name, tracksvg, viewbox=None, height=100):
        # height = 100
        # if viewbox is not None:
        #     x, y, w, h = viewbox.split()
        #     height = float(h)
        if not section in self.sections:
            self.sections[section] = collections.OrderedDict()
        self.sections[section][name] = {"svg":tracksvg,
                                        "viewbox":viewbox,
                                        "height": height
                                       }

    def _svgText(self, x, y, text, height, bold=False, anchor=None):
        extras = ""
        if bold:
            extras += ' font-weight="bold"'
        if anchor:
            extras += ' anchor="{}"'.format(anchor)
        svg = '<svg x="{x}" y="{y}"><text x="0" y="{padded}" font-size="{textHeight}" font-family="Helvetica" {extras}>{text}</text></svg>'.format(x=x, y=y, 
            padded=height, textHeight=(height-2), text=text, extras=extras)
        return svg

    def renderCountsTable(self, modTracks, ystart, fontsize=18):
        charWidth = fontsize/2
        ystart += 5
        counts = self.dataHub.getCounts()
        columns = ["Sample", "Alt", "Ref", "Amb"]

        columnWidths = []
        longestRowHeader = max(max(counts, key=lambda x: len(x)), len(columns[0]))
        columnWidths.append(len(longestRowHeader)*charWidth)
        columnWidths.extend([7*charWidth]*3)

        rows = [columns]
        for sample, curcounts in counts.iteritems():
            rows.append([sample, curcounts["alt"], curcounts["ref"], curcounts["amb"]])

        for i, row in enumerate(rows):
            xstart = 10
            for j, value in enumerate(row):
                width = columnWidths[j]
                if j == 0:
                    # row header
                    modTracks.append(self._svgText(xstart, ystart, value, fontsize, bold=True, anchor="start"))
                    xstart += width
                else:
                    xstart += width
                    modTracks.append(self._svgText(xstart, ystart, value, fontsize, bold=i==0, anchor="end"))
            ystart += fontsize * 1.25

        return ystart + 10
            # self.descriptions.append("{}: {} {} {}".format(name, curcounts["alt"], curcounts["ref"], curcounts["amb"]))

    def render(self):
        modTracks = []
        curX = 0
        curY = self.marginTopBottom

        if self.title is not None:
            header = self._svgText(curX+10, curY, self.title, self.sectionLabelHeight+5, bold=True)
            modTracks.append(header)
            curY += self.sectionLabelHeight+10

        curY = self.renderCountsTable(modTracks, curY)

        # for description in self.descriptions:
        #     header = self._svgText(curX+20, curY, description, self.trackLabelHeight)
        #     modTracks.append(header)
        #     curY += self.trackLabelHeight+5

        for i, sectionName in enumerate(self.sections):
            section = self.sections[sectionName]

            if i > 0:
                curY += self.betweenSectionHeight

            label = self._svgText(curX+10, curY, sectionName, self.sectionLabelHeight)
            modTracks.append(label)
            curY += self.sectionLabelHeight

            for trackName in section:
                trackInfo = section[trackName]

                if trackName != "axis":
                    label = self._svgText(curX+10, curY, trackName, self.trackLabelHeight)
                    modTracks.append(label)
                    curY += self.sectionLabelHeight

                extra = 'svg x="{}" y="{}" width="{}" height="{}"'.format(curX, curY, self.width, trackInfo["height"])
                if trackInfo["viewbox"] is not None:
                    extra += ' viewBox="{}"'.format(trackInfo["viewbox"])
                mod = trackInfo["svg"].replace("svg", extra, 1)
                modTracks.append(mod)

                curY += trackInfo["height"]

        curY += self.marginTopBottom

        composite = ['<?xml version="1.0" encoding="utf-8" ?><svg  xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{}" height="{}">'.format(self.width, curY)] \
                    + modTracks + ["</svg>"]
        return "\n".join(composite)


def canConvertSVGToPDF():
    try:
        subprocess.check_call("rsvg-convert -v", stdout=subprocess.PIPE, shell=True)
    except subprocess.CalledProcessError:
        return False
    else:
        return True

def convertSVG(insvg, outformat="pdf"):
    if not canConvertSVGToPDF():
        logging.error("Can't find rsvg-convert; make sure you have librsvg installed")
        return None

    outdir = tempfile.mkdtemp()
    inpath = "{}/original.svg".format(outdir)
    infile = open(inpath, "w")
    infile.write(insvg)
    infile.flush()
    infile.close()

    options = ""
    if outformat == "png":
        options = "-a -w 5000 --background-color white"

    outpath = "{}/converted.{}".format(outdir, outformat)

    try:
        subprocess.check_call("rsvg-convert -f {} {} -o {} {}".format(outformat, options, outpath, inpath), shell=True)
    except subprocess.CalledProcessError, e:
        print "EXPORT ERROR:", str(e)

    return open(outpath).read()

# def convertSVGToPDF2(insvg):
#     import cairosvg

#     pdf = cairosvg.svg2pdf(bytestring=insvg)
#     return pdf

# def convertSVGToPNG(insvg):
#     import cairosvg

#     png = cairosvg.svg2png(bytestring=insvg)
#     return png


def test():
    base = """  <svg><rect x="10" y="10" height="100" width="100" style="stroke:#ffff00; stroke-width:3; fill: #0000ff"/><text x="25" y="25" fill="blue">{}</text></svg>"""
    svgs = [base.format("track {}".format(i)) for i in range(5)]

    tc = TrackCompositor(200, 600)
    for i, svg in enumerate(svgs):
        tc.addTrack(svg, i, viewbox="0 0 110 110")

    outf = open("temp.svg", "w")
    outf.write(tc.render())
    outf.flush()
    outf.close()

    pdfPath = convertSVGToPDF("temp.svg")
    subprocess.check_call("open {}".format(pdfPath), shell=True)

if __name__ == '__main__':
    test()

    import sys
    print >>sys.stderr, canConvertSVGToPDF()