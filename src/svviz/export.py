import collections
import subprocess
import tempfile


class TrackCompositor(object):
    def __init__(self, width, height):
        self.tracks = collections.OrderedDict()
        self.height = height
        self.width = width

    @staticmethod
    def composite(tracks, names, viewboxes=None):
        tc = TrackCompositor(1200, 300)
        for track, name in zip(tracks, names):
            # viewbox = " ".join([0,0,])
            tc.addTrack(track.render(), name, height=track.height)
        return tc.render()

    def addTrack(self, tracksvg, name, viewbox=None, height=100):
        # height = 100
        # if viewbox is not None:
        #     x, y, w, h = viewbox.split()
        #     height = float(h)
        self.tracks[name] = {"svg":tracksvg,
                             "viewbox":viewbox,
                             "height": height
                            }

    def render(self):
        n = len(self.tracks)
        # eachHeight = (self.height-20*n)/float(n)
        heights = dict((name, self.tracks[name]["height"]) for name in self.tracks)
        totalHeight = float(sum(heights.values()))
        for name in self.tracks:
            heights[name] = heights[name]/totalHeight*(self.height-20*n)
        print heights
        eachWidth = self.width#/float(n)

        modTracks = []
        curX = 0
        curY = 0

        for name, trackInfo in self.tracks.iteritems():
            label = '<svg x="{}" y="{}"><text x="0" y="20">{}</text></svg>'.format(curX, curY, name)
            modTracks.append(label)
            curY += 20

            extra = 'svg x="{}" y="{}" width="{}" height="{}"'.format(curX, curY, eachWidth, heights[name])
            if trackInfo["viewbox"] is not None:
                extra += ' viewBox="{}" preserveAspectRatio="xMinYMin"'.format(trackInfo["viewbox"])
            mod = trackInfo["svg"].replace("svg", extra, 1)
            modTracks.append(mod)

            curY += heights[name]

        composite = ['<?xml version="1.0" encoding="utf-8" ?><svg  xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{}" height="{}">'.format(self.width, self.height)] \
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