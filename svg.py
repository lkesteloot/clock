
#   Copyright 2015 Lawrence Kesteloot
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from config import SCALE

# "Hairline" in AI.
STROKE_WIDTH = 0.001

def header(out, width, height):
    out.write("""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN"    "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd" [
<!ENTITY ns_svg "http://www.w3.org/2000/svg">
]>
<!-- Width and height include stroke width. -->
<svg xmlns="&ns_svg;" width="%d" height="%d" overflow="visible" style="background: black">
<g id="Layer_1" transform="scale(%g,%g)">
    <!-- 72 DPI -->
    <!-- <rect x="0" y="0" width="%g" height="%g" fill="none" stroke="#000000"/> -->
""" % (width, height, SCALE, SCALE, width, height))

def start_group(out, name, dx=0, dy=0):
    out.write("""<g id="%s" transform="translate(%g,%g)">\n""" % (name, dx, dy))

def end_group(out):
    out.write("""</g>\n""")

def draw_line(out, x1, y1, x2, y2):
    out.write("""        <line x1="%g" y1="%g" x2="%g" y2="%g" fill="none" stroke="#000000" stroke-width="%g"/>\n""" % (x1, y1, x2, y2, STROKE_WIDTH))

def circle(out, cx, cy, r, color):
    out.write("""        <circle fill="none" stroke="%s" stroke-width="%g" cx="%s" cy="%s" r="%s"/>\n""" % (color, STROKE_WIDTH, cx, cy, r))

def polyline(out, p, color):
    out.write("""<polyline fill="none" stroke="%s" stroke-width="%g" points=" """ % (color, STROKE_WIDTH))
    for x, y in p:
        out.write(" %g,%g" % (x, y))
    out.write(""" "/>\n""")

def footer(out):
    out.write("""    </g>
</svg>
""")
