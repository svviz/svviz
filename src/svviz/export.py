import collections
import subprocess
import tempfile


class TrackCompositor(object):
    def __init__(self, width, height):
        self.tracks = collections.OrderedDict()
        self.height = height
        self.width = width

    def addTrack(self, tracksvg, name, viewbox=None):
        self.tracks[name] = {"svg":tracksvg,
                             "viewbox":viewbox}

    def render(self):
        n = len(self.tracks)
        eachHeight = (self.height-20*n)/float(n)
        eachWidth = self.width#/float(n)

        modTracks = []
        curX = 0
        curY = 0

        for name, trackInfo in self.tracks.iteritems():
            label = '<svg x="{}" y="{}"><text x="0" y="20">{}</text></svg>'.format(curX, curY, name)
            modTracks.append(label)
            curY += 20

            extra = 'svg x="{}" y="{}" width="{}" height="{}"'.format(curX, curY, eachWidth, eachHeight)
            if trackInfo["viewbox"] is not None:
                extra += ' viewBox="{}" preserveAspectRatio="xMinYMin"'.format(trackInfo["viewbox"])
            mod = trackInfo["svg"].replace("svg", extra, 1)
            modTracks.append(mod)

            curY += eachHeight

        composite = ['<svg  xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{}" height="{}">'.format(self.width, self.height)] \
                    + modTracks + ["</svg>"]
        return "\n".join(composite)

def canConvertSVGToPDF():
    try:
        subprocess.check_call("rsvg-convert -v", shell=True)
    except subprocess.CalledProcessError:
        return False
    else:
        return True

def convertSVGToPDF(inpath):
    if not canConvertSVGToPDF():
        print "Can't find rsvg-convert; make sure you have librsvg installed"
        return None

    outdir = tempfile.mkdtemp()
    outpath = "{}/converted.pdf".format(outdir)
    subprocess.check_call("rsvg-convert -f pdf -o {} {}".format(outpath, inpath), shell=True)

    return outpath


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