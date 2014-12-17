
class SVG(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.svg = []
        self._addHeader()

    def _addHeader(self):
        self.svg.append("""<?xml version="1.0" encoding="utf-8" ?><svg baseProfile="full" height="100%" version="1.1" """
            """width="100%" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" """
            """xmlns:ev="http://www.w3.org/2001/xml-events" xmlns:xlink="http://www.w3.org/1999/xlink"><defs />""".format(h=self.height, w=self.width))
        self.svg.append("<g class=\"svg_viewport\">")

    def _addOptions(self, **kwdargs):
        options = []
        for key, arg in kwdargs.iteritems():
            if arg is not None and arg != "":
                options.append("""{key}="{arg}" """.format(key=key, arg=arg))
        return " ".join(options)

    def line(self, x1, x2, y1, y2, stroke="", fill="", **kwdargs):
        more = self._addOptions(stroke=stroke, fill=fill, **kwdargs)
        self.svg.append("""<line x1="{x1}" x2="{x2}" y1="{y1}" y2="{y2}" {more}/>""".format(x1=x1, x2=x2, y1=self.height-y1, y2=self.height-y2, more=more))

    def rect(self, x, y, width, height, stroke="", fill="", **kwdargs):
        more = self._addOptions(stroke=stroke, fill=fill, **kwdargs)
        self.svg.append("""<rect x="{x}" y="{y}" width="{w}" height="{h}" {more}/>\n""".format(x=x, y=self.height-y, w=width, h=height, more=more))

    def text(self, x, y, text, size=10, anchor="middle", fill="", family="Arial", **kwdargs):
        kwdargs["font-family"] = family
        more = self._addOptions(fill=fill, **kwdargs)
        self.svg.append("""<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" {more}>{text}</text>\n""".format(x=x, y=self.height-y, size=size, anchor=anchor, more=more, text=text))

    def __str__(self):
        return "".join(self.svg+["""</g></svg>"""])

    def write(self, path):
        output = open(path, "w")
        output.write("".join(self.svg+["""</g></svg>"""]))
