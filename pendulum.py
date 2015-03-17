
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
from config import DPI, TAU, TIGHT_LARGE_BOLT_RADIUS, PENDULUM_HOLE_SEPARATION, PENDULUM_BAR_WIDTH, PENDULUM_BAR_HEIGHT, PENDULUM_WEIGHT_WIDTH, PENDULUM_WEIGHT_HEIGHT, LEFT_FULL_IN_ANGLE, RIGHT_FULL_IN_ANGLE
import draw

CORNER_RADIUS = DPI*0.25
CORNER_POINTS = 32

def add_holed_rectangle(data, origin, y_offset, cz, width, height, speed, color):
    P = []
    P.append(Vector(-width/2, y_offset))
    P.append(Vector(width/2, y_offset))
    P.append(Vector(width/2, y_offset + height))
    P.append(Vector(-width/2, y_offset + height))
    P = draw.round_corners(P, CORNER_RADIUS, CORNER_POINTS)

    holes = []
    y = PENDULUM_HOLE_SEPARATION
    while y < height - PENDULUM_HOLE_SEPARATION/2:
        holes.append({
            "cx": 0,
            "cy": y_offset + y,
            "r": TIGHT_LARGE_BOLT_RADIUS,
        })
        y += PENDULUM_HOLE_SEPARATION

    piece = {
        "cx": origin.x,
        "cy": origin.y,
        "cz": cz,
        "type": "pendulum",
        "color": color,
        "speed": speed,
        "points": P,
        "holes": holes,
        "left_full_in_angle": LEFT_FULL_IN_ANGLE,
        "right_full_in_angle": RIGHT_FULL_IN_ANGLE,
    }
    data["pieces"].append(piece)

def add_bar(data, origin, y_offset, cz, speed, color):
    add_holed_rectangle(data, origin, y_offset, cz, PENDULUM_BAR_WIDTH, PENDULUM_BAR_HEIGHT, speed, color)

def add_weight(data, origin, y_offset, cz, speed, color):
    add_holed_rectangle(data, origin, y_offset, cz, PENDULUM_WEIGHT_WIDTH, PENDULUM_WEIGHT_HEIGHT, speed, color)

def generate(data, verge_center, y_offset, cz, speed, color):
    y_offset -= PENDULUM_HOLE_SEPARATION
    add_bar(data, verge_center, y_offset, cz + 1, speed, color)

    y_offset += PENDULUM_HOLE_SEPARATION*13
    add_bar(data, verge_center, y_offset, cz, speed, color)

    y_offset += PENDULUM_HOLE_SEPARATION*13
    add_weight(data, verge_center, y_offset, cz + 1, speed, color)
    add_weight(data, verge_center, y_offset, cz + 2, speed, color)
    add_weight(data, verge_center, y_offset, cz - 1, speed, color)
    add_weight(data, verge_center, y_offset, cz - 2, speed, color)
