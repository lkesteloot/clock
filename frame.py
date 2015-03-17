
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

import sys
import math

from vector import Vector
from config import DPI, TAU, TIGHT_LARGE_BOLT_RADIUS, WALL_ANCHOR_RADIUS, WALL_ANCHOR_OFFSET
import draw

PADDING = DPI*1
CORNER_RADIUS = DPI*0.25
CORNER_POINTS = 32
FOOT_WIDTH = PADDING - 2*CORNER_RADIUS
ADD_FEET = False
ADD_WALL_ANCHOR_HOLES = False

def generate(data, color):
    # Deduce size and position of frame, and its holes, from the existing data.
    minX = DPI*100
    minY = DPI*100
    maxX = -DPI*100
    maxY = -DPI*100
    floorY = -DPI*100

    holes = []
    for piece in data["pieces"]:
        cx = piece["cx"]
        cy = piece["cy"]
        minX = min(minX, cx)
        minY = min(minY, cy)
        maxX = max(maxX, cx)
        maxY = max(maxY, cy)
        for v in piece["points"]:
            floorY = max(floorY, cy + v.y)
        for hole in holes:
            if hole["cx"] == cx and hole["cy"] == cy:
                break
        else:
            holes.append({
                "cx": cx,
                "cy": cy,
                "r": TIGHT_LARGE_BOLT_RADIUS,
            })
    # Add hole in lower-left since there are no axles there.
    holes.append({
        "cx": minX,
        "cy": maxY,
        "r": TIGHT_LARGE_BOLT_RADIUS,
    })
    sys.stderr.write("The frame has %d holes.\n" % len(holes))

    # Expand margin.
    minX -= PADDING
    minY -= PADDING
    maxX += PADDING
    maxY += PADDING
    floorY += PADDING

    # Draw frame.
    P = []
    P.append(Vector(minX, minY))
    P.append(Vector(maxX, minY))
    if ADD_FEET:
        P.append(Vector(maxX, floorY))
        P.append(Vector(maxX - FOOT_WIDTH, floorY))
        P.append(Vector(maxX - FOOT_WIDTH, maxY))
        P.append(Vector(minX + FOOT_WIDTH, maxY))
        P.append(Vector(minX + FOOT_WIDTH, floorY))
        P.append(Vector(minX, floorY))
    else:
        P.append(Vector(maxX, maxY))
        P.append(Vector(minX, maxY))
    # Do not close this, the round_corners() function does it.

    P = draw.round_corners(P, CORNER_RADIUS, CORNER_POINTS)

    width = (maxX - minX)/DPI
    height = ((floorY if ADD_FEET else maxY) - minY)/DPI
    sys.stderr.write("Frame is %.1fx%.1f inches\n" % (width, height))
    if width > 24 or height > 18:
        sys.stderr.write("------------------ FRAME TOO LARGE -----------------------\n")

    # Front piece.
    piece = {
        "cx": 0,
        "cy": 0,
        "cz": 9,
        "type": "frame",
        "color": color,
        "speed": 0,
        "points": P,
        "holes": holes,
    }
    data["pieces"].append(piece)

    # Back piece.
    piece = piece.copy()

    # Add holes for hanging frame to wall.
    holes = holes[:]
    if ADD_WALL_ANCHOR_HOLES:
        # XXX Can probably delete this.
        piece["holes"] = holes
        holes.append({
            "cx": minX + WALL_ANCHOR_OFFSET + PADDING,
            "cy": minY + PADDING,
            "r": WALL_ANCHOR_RADIUS,
        })
        holes.append({
            "cx": maxX - WALL_ANCHOR_OFFSET - PADDING,
            "cy": minY + PADDING,
            "r": WALL_ANCHOR_RADIUS,
        })
        holes.append({
            "cx": minX + WALL_ANCHOR_OFFSET + PADDING,
            "cy": maxY - PADDING,
            "r": WALL_ANCHOR_RADIUS,
        })
        holes.append({
            "cx": maxX - WALL_ANCHOR_OFFSET - PADDING,
            "cy": maxY - PADDING,
            "r": WALL_ANCHOR_RADIUS,
        })

    piece["cz"] = -3
    data["pieces"].append(piece)

