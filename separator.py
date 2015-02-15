
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

import math

from config import TAU, SEPARATOR_RADIUS

# Closed circle.
def generate_circle_points(x, y, r, n):
    p = []

    for i in range(n + 1):
        t = float(i)/n*TAU
        p.append((x + math.cos(t)*r, y + math.sin(t)*r))

    return p

def generate(x, y, hole_radius):
    piece = {
        "type": "separator",
        "cx": x,
        "cy": y,
        "plane": 0,
        "color": "#FFFFFF",
        "hole_radius": hole_radius,
        "outer_radius": SEPARATOR_RADIUS,
        "points": generate_circle_points(0, 0, SEPARATOR_RADIUS, 100),
        "speed": 0,
    }
    return piece

