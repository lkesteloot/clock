
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

import argparse

# Draw shapes into array of points.

def add_arc(p, begin_deg, end_deg, radius):
    sys.stderr.write("Drawing from %d to %d at %g\n" % (begin_deg, end_deg, radius) )
    for deg in auto_range(begin_deg, end_deg):
        rad = deg*DEG_TO_RAD
        p.append(Vector(cos(rad), sin(rad))*radius)

# Specify four points.
def add_bezier(p, p1, p2, p3, p4, point_count):
    for i in range(point_count):
        t = float(i) / (point_count - 1)

        # Interpolate the primary segments.
        pp1 = p1 + (p2 - p1)*t
        pp2 = p2 + (p3 - p2)*t
        pp3 = p3 + (p4 - p3)*t

        # Interpolate the secondary segments.
        ppp1 = pp1 + (pp2 - pp1)*t
        ppp2 = pp2 + (pp3 - pp2)*t

        # Interpolate the tertiary segments.
        pppp1 = ppp1 + (ppp2 - ppp1)*t

        p.append(pppp1)

