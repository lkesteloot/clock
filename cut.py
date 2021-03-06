
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

# Generate SVG for cutting.

import sys
import argparse
import json

from config import DPI, WIDTH, HEIGHT
import svg

# Generates an SVG from a JSON clock description.
def main():
    parser = argparse.ArgumentParser(description='Generate gears.')
    parser.add_argument("input", help="JSON filename to read")
    args = parser.parse_args()

    data = json.load(open(args.input))
    pieces = data["pieces"]

    out = sys.stdout
    x_multiplier = 1.0
    cz_vertical_offset = 5*DPI*0

    svg.header(out, WIDTH*x_multiplier, HEIGHT*7)

    # Make cuts.
    for piece_index, piece in enumerate(data["pieces"]):
        cx = piece["cx"]*x_multiplier
        cy = piece["cy"] + piece["cz"]*cz_vertical_offset
        color = piece["color"]

        # Always use black for cut, it makes it easier to see in AI.
        color = "black"

        name = "%s_%d" % (piece["type"], piece_index)
        svg.start_group(out, name, cx, cy)

        p = piece["points"]
        svg.start_group(out, name + "_body")
        svg.polyline(out, p, color)
        svg.end_group(out)

        if "hole_radius" in piece:
            svg.start_group(out, name + "_hole")
            svg.circle(out, 0, 0, piece["hole_radius"], color)
            svg.end_group(out)
        if "bind" in piece:
            bind = piece["bind"]
            bind_radius = bind["hole_radius"]
            svg.start_group(out, name + "_bind")
            for center in bind["centers"]:
                svg.circle(out, center[0], center[1], bind_radius, color)
            svg.end_group(out)
        if "holes" in piece:
            # Also cut holes from all the axles.
            svg.start_group(out, name + "_holes")
            for hole in piece["holes"]:
                svg.circle(out, hole["cx"], hole["cy"], hole["r"], color)
            svg.end_group(out)

        svg.end_group(out)

    svg.footer(out)

if __name__ == "__main__":
    main()
