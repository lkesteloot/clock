
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
from config import DPI, TAU, TIGHT_LARGE_BOLT_RADIUS, PENDULUM_HOLE_SEPARATION, PENDULUM_BAR_WIDTH, PENDULUM_BAR_HEIGHT, PENDULUM_WEIGHT_WIDTH, PENDULUM_WEIGHT_HEIGHT
import draw

CORNER_RADIUS = DPI*0.25
CORNER_POINTS = 32

def add_holed_rectangle(data, cx, cy, cz, width, height, color):
    P = []
    P.append((0, 0))
    P.append((width, 0))
    P.append((width, height))
    P.append((0, height))
    P = draw.round_corners(P, CORNER_RADIUS, CORNER_POINTS)

    holes = []
    y = PENDULUM_HOLE_SEPARATION
    while y < height - PENDULUM_HOLE_SEPARATION/2:
        holes.append({
            "cx": cx + width/2,
            "cy": cy + y,
            "r": TIGHT_LARGE_BOLT_RADIUS,
        })
        y += PENDULUM_HOLE_SEPARATION

    piece = {
        "cx": cx,
        "cy": cy,
        "cz": cz,
        "type": "pendulum_bar",
        "color": color,
        "speed": 0,
        "points": P,
        "holes": holes,
    }
    data["pieces"].append(piece)

def add_bar(data, cx, cy, cz, color):
    add_holed_rectangle(data, cx, cy, cz, PENDULUM_BAR_WIDTH, PENDULUM_BAR_HEIGHT, color)

def add_weight(data, cx, cy, cz, color):
    add_holed_rectangle(data, cx, cy, cz, PENDULUM_WEIGHT_WIDTH, PENDULUM_WEIGHT_HEIGHT, color)

def generate(data, color):
    cx = 0
    cy = 0
    cz = 0

    add_bar(data, cx, cy, cz, color)

    cx += PENDULUM_BAR_WIDTH + 0.1*DPI
    add_bar(data, cx, cy, cz, color)

    cx += PENDULUM_BAR_WIDTH + 0.1*DPI
    add_weight(data, cx, cy, cz, color)
