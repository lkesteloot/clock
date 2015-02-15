
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
from config import DPI, TAU, TIGHT_LARGE_BOLT_RADIUS

PADDING = DPI*1
FOOT_WIDTH = DPI*1
CORNER_RADIUS = DPI*0.25
CORNER_POINTS = 32

# Generate a new sequence of points with the corners rounded to "radius".
def round_corners(P, radius, point_count):
    newP = []

    # For each point in P (which is open), draw a line from P to the next point,
    # and the following quarter circle.
    for i in range(len(P)):
        # This and next point.
        p0 = Vector.from_pair(P[i])
        p1 = Vector.from_pair(P[(i + 1) % len(P)])
        p2 = Vector.from_pair(P[(i + 2) % len(P)])

        # Find direction to next point.
        dp0 = (p1 - p0).normalized()

        # And point after that.
        dp1 = (p2 - p1).normalized()

        # Straight line.
        newP.append(p0 + dp0*radius)
        newP.append(p1 - dp0*radius)

        # Quarter circle.
        c = p1 - dp0*radius + dp1*radius
        for j in range(point_count):
            t = (j + 1.0)/(point_count + 1)*TAU/4
            newP.append(c + (dp0*math.sin(t) - dp1*math.cos(t))*radius)

    # Convert to pairs.
    newP = [p.to_pair() for p in newP]

    return newP

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
        for x, y in piece["points"]:
            floorY = max(floorY, cy + y)
        for hole in holes:
            if hole["cx"] == cx and hole["cy"] == cy:
                break
        else:
            holes.append({
                "cx": cx,
                "cy": cy,
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
    P.append((minX, minY))
    P.append((maxX, minY))
    P.append((maxX, floorY))
    P.append((maxX - FOOT_WIDTH, floorY))
    P.append((maxX - FOOT_WIDTH, maxY))
    P.append((minX + FOOT_WIDTH, maxY))
    P.append((minX + FOOT_WIDTH, floorY))
    P.append((minX, floorY))

    P = round_corners(P, CORNER_RADIUS, CORNER_POINTS)

    width = (maxX - minX)/DPI
    height = (floorY - minY)/DPI
    sys.stderr.write("Frame is %.1fx%.1f inches\n" % (width, height))
    if width > 24:
        sys.stderr.write("------------------ FRAME TOO LARGE -----------------------\n")

    piece = {
        "cx": 0,
        "cy": 0,
        "plane": -3,
        "type": "frame",
        "color": color,
        "speed": 0,
        "points": P,
        "holes": holes,
    }
    data["pieces"].append(piece)

    piece = piece.copy()
    piece["plane"] = 9
    data["pieces"].append(piece)

