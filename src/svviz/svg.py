def _arrowhead_marker():
    return """<marker id="arrowhead"
      viewBox="0 0 10 10" refX="10" refY="5" 
      markerUnits="strokeWidth"
      markerWidth="4" markerHeight="3"
      orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" />
    </marker>"""


class SVG(object):
    def __init__(self, width, height, headerExtras="", markers=None):
        self.width = width
        self.height = height

        # self.header = []
        self.svg = []
        self.footer = ["""</g></svg>"""]
        self.headerExtras = headerExtras
        if markers is None:
            markers = {}
        self.markers = markers
        # self._addHeader()

    def getDefaultZIndex(self, zindex):
        """ allows insertion at the beginning of the svg list (ie before all the other items, therfore below them) """
        if zindex is None:
            zindex = len(self.svg)
        return zindex

    def header(self):
        header = []
        # """<?xml version="1.0" encoding="utf-8" ?>"""
        header.append("""<svg baseProfile="full" version="1.1" """
            """xmlns="http://www.w3.org/2000/svg" {extras} """
            """xmlns:ev="http://www.w3.org/2001/xml-events" xmlns:xlink="http://www.w3.org/1999/xlink"><defs>{markers}</defs>""".format(extras=self.headerExtras,
                markers="\n".join(self.markers.values())))

        header.append("<g class=\"svg_viewport\">")
        return header

    def _addOptions(self, **kwdargs):
        options = []
        for key, arg in kwdargs.iteritems():
            if arg is not None and arg != "":
                options.append("""{key}="{arg}" """.format(key=key, arg=arg))
        return " ".join(options)

    def line(self, x1, x2, y1, y2, stroke="", fill="", arrowhead=None, **kwdargs):
        more = self._addOptions(stroke=stroke, fill=fill, **kwdargs)

        if arrowhead is not None:
            if not "arrowhead" in self.markers:
                self.markers["arrowhead"] = _arrowhead_marker()
            if arrowhead in ["end", "both"]:
                more += """ marker-end="url(#arrowhead)" """
            if arrowhead in ["start", "both"]:
                more += """ marker-start="url(#arrowhead)" """

        self.svg.append("""<line x1="{x1}" x2="{x2}" y1="{y1}" y2="{y2}" {more} />""".format(x1=x1, x2=x2, y1=self.height-y1, y2=self.height-y2, more=more))

    def arrow(self, x, y, direction, color="black", scale=1.0, **kwdargs):
        more = self._addOptions(**kwdargs)

        if direction == "right":
            a = """<path d="M {x0} {y0} L {x1} {y1} L {x2} {y2} z" fill="{color}" xcenter="{xcenter}" {more}/>""".format(
                x0=(x-5*scale), y0=(y-5*scale), 
                x1=(x+5*scale), y1=y, 
                x2=(x-5*scale), y2=(y+5*scale),
                color=color,
                xcenter=x,
                more=more)
        elif direction == "left":
            a = """<path d="M {x0} {y0} L {x1} {y1} L {x2} {y2} z" fill="{color}" xcenter="{xcenter}" {more}/>""".format(
                x0=(x+5*scale), y0=(y-5*scale), 
                x1=(x-5*scale), y1=y, 
                x2=(x+5*scale), y2=(y+5*scale),
                color=color,
                xcenter=x,
                more=more)
        self.svg.append(a)

        # a = """<path d="M 0 0 L 10 5 L 0 10 z" fill={color}/>"""


    def lineWithInternalArrows(self, x1, x2, y1, y2, stroke="", fill="", n=5, direction="right", arrowKwdArgs=None, **kwdargs):
        self.line(x1, x2, y1, y2, stroke, fill, **kwdargs)
        if arrowKwdArgs is None: arrowKwdArgs = {}

        for i in range(1, n+1):
            x_arrow = x1+float(x2-x1)*i/n
            y_arrow = self.height-(y1+float(y2-y1)*i/n)
            self.arrow(x_arrow, y_arrow, direction, color=stroke, scale=kwdargs.get("stroke-width", 1), **arrowKwdArgs)

    def rect(self, x, y, width, height, stroke="", fill="", zindex=None, **kwdargs):
        zindex = self.getDefaultZIndex(zindex)
        more = self._addOptions(stroke=stroke, fill=fill, **kwdargs)
        self.svg.insert(zindex, """<rect x="{x}" y="{y}" width="{w}" height="{h}" {more}/>""".format(x=x, y=self.height-y, w=width, h=height, more=more))

    def text(self, x, y, text, size=10, anchor="middle", fill="", family="Helvetica", **kwdargs):
        kwdargs["font-family"] = family
        more = self._addOptions(fill=fill, **kwdargs)
        self.svg.append("""<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" {more}>{text}</text>""".format(x=x, y=self.height-y, size=size, anchor=anchor, more=more, text=text))


    def __str__(self):
        return self.asString()

    def asString(self, headerSet=None):
        oldHeaderExtras = self.headerExtras

        if headerSet is None:
            self.headerExtras += """viewBox="0 0 {w} {h}" """.format(w=self.width, h=self.height)
            header = self.header()
        elif headerSet == "export":
            self.headerExtras = ""
            header = self.header()
        elif headerSet == "web":
            xmlHeader = """<?xml version="1.0" encoding="utf-8" ?>"""
            self.headerExtras += """preserveAspectRatio="none" height="100%" width="100%" """
            header = [xmlHeader] + self.header()

        self.headerExtras = oldHeaderExtras

        return "\n".join(header + self.svg + self.footer)

    def write(self, path, headerSet=None):
        output = open(path, "w")
        output.write(self.asString(headerSet))
