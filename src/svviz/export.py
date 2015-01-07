import collections
import logging
import subprocess
import tempfile


class TrackCompositor(object):
    def __init__(self, width, title=None):
        self.sections = collections.OrderedDict()
        # self.height = height
        self.width = width
        self.title = title

        self.marginTopBottom = 20
        self.sectionLabelHeight = 32
        self.betweenSectionHeight = 30
        self.trackLabelHeight = 20

    def addTracks(self, section, names, tracks):
        for track in tracks:
            track.render()
        xmin = [track.xmin for track in tracks if track.xmin is not None]
        xmin = min(xmin) if len(xmin) > 0 else 0
        xmax = [track.xmax for track in tracks if track.xmax is not None]
        xmax = max(xmax) if len(xmax) > 0 else 500

        width = 500
        if xmin is not None:
            width = xmax - xmin + 10

        for track, name in zip(tracks, names):
            if len(track.alignmentSets) == 0:
                height = 20
                viewbox = "0 0 {width} {height}".format(width=track.width, height=track.height)
            else:
                height = track.height/6.0
                viewbox = "{xmin} 0 {width} {height}".format(xmin=xmin, width=width, height=height)
            self.addTrackSVG(section, name, track.svg.asString("export"), height=height, viewbox=viewbox)

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

    def _svgText(self, x, y, text, height, bold=False):
        extras = ""
        if bold:
            extras += ' font-weight="bold"'
        svg = '<svg x="{x}" y="{y}"><text x="0" y="{padded}" font-size="{textHeight}" font-family="Helvetica" {extras}>{text}</text></svg>'.format(x=x, y=y, 
            padded=height, textHeight=(height-2), text=text, extras=extras)
        return svg

    def render(self):
        modTracks = []
        curX = 0
        curY = self.marginTopBottom

        if self.title is not None:
            header = self._svgText(curX+10, curY, self.title, self.sectionLabelHeight+5, bold=True)
            modTracks.append(header)
            curY += self.sectionLabelHeight+5

        for i, sectionName in enumerate(self.sections):
            section = self.sections[sectionName]

            if i > 0:
                curY += self.betweenSectionHeight

            # label = '<svg x="{}" y="{}"><text x="0" y="30" font-size="28" font-family="Helvetica">{}</text></svg>'.format(curX+10, curY, sectionName)
            label = self._svgText(curX+10, curY, sectionName, self.sectionLabelHeight)
            modTracks.append(label)
            curY += self.sectionLabelHeight

            for trackName in section:
                trackInfo = section[trackName]

                label = self._svgText(curX+10, curY, trackName, self.trackLabelHeight)
                # label = '<svg x="{}" y="{}"><text x="0" y="{}" font-family="Helvetica">{}</text></svg>'.format(curX+20, curY, curY+self.sectionLabelHeight, trackName)
                modTracks.append(label)
                curY += self.sectionLabelHeight

                extra = 'svg x="{}" y="{}" width="{}" height="{}"'.format(curX, curY, self.width, trackInfo["height"])
                if trackInfo["viewbox"] is not None:
                    extra += ' viewBox="{}" preserveAspectRatio="xMinYMin"'.format(trackInfo["viewbox"])
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
    subprocess.check_call("rsvg-convert -f {} {} -o {} {}".format(outformat, options, outpath, inpath), shell=True)

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