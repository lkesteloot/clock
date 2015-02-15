
# Generate SVG for cutting.

import sys
import argparse
import json

from config import DPI, WIDTH, HEIGHT
import draw

def main():
    parser = argparse.ArgumentParser(description='Generate gears.')
    parser.add_argument("input", help="JSON filename to read")
    args = parser.parse_args()

    data = json.load(open(args.input))
    pieces = data["pieces"]

    out = sys.stdout
    x_multiplier = 1.1
    plane_offset = 5*DPI

    draw.header(out, WIDTH*x_multiplier, HEIGHT*7)

    # Make cuts.
    for piece_index, piece in enumerate(data["pieces"]):
        cx = piece["cx"]*x_multiplier
        cy = piece["cy"] + piece["plane"]*plane_offset
        color = piece["color"]

        # Always use black for cut, it makes it easier to see in AI.
        color = "black"

        name = "%s_%d" % (piece["type"], piece_index)
        draw.start_group(out, name, cx, cy)

        draw.start_group(out, name + "_body")
        draw.polyline(out, piece["points"], color)
        draw.end_group(out)

        if "hole_radius" in piece:
            draw.start_group(out, name + "_hole")
            draw.circle(out, 0, 0, piece["hole_radius"], color)
            draw.end_group(out)
        if "bind" in piece:
            bind = piece["bind"]
            bind_radius = bind["hole_radius"]
            draw.start_group(out, name + "_bind")
            for center in bind["centers"]:
                draw.circle(out, center[0], center[1], bind_radius, color)
            draw.end_group(out)
        if "holes" in piece:
            # Also cut holes from all the axles.
            draw.start_group(out, name + "_holes")
            for hole in piece["holes"]:
                draw.circle(out, hole["cx"], hole["cy"], hole["r"], color)
            draw.end_group(out)

        draw.end_group(out)

    draw.footer(out)

if __name__ == "__main__":
    main()