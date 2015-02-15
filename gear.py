
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
from math import sin, cos, tan, sqrt, pi, atan

from config import NUM_POINTS_ROOT, NUM_POINTS_FILLET, NUM_POINTS_FLANK, NUM_POINTS_TOP

def inv(a):
    return tan(a) - a

def involute(a):
    return atan(a) - a

def cot(a):
    return 1/tan(a)

def sec(a):
    return 1/cos(a)

def generate(cx, cy, z, hole_radius, angle_offset, color, module):
    # Basic ratio.
    alpha = 20 * (pi / 180)
    h = pi / 4
    a = 1
    b = 1.25
    e = 0.38

    # Center of fillet in rack.
    v_c = e - b
    u_c = h + e*sec(alpha) - v_c*tan(alpha)

    # Gear parameters.
    s = 0.0

    # Standard pitch radius. Not affected by shift.
    R = z/2.0

    # Base circle radius.
    R0 = R*cos(alpha)

    # Addendum radius, relative to extended pitch radius.
    r_a = R + s + a

    # Dedendum radius, relative to extended pitch radius.
    r_b = R + s - b

    # s bounds.
    if False:
        s_lo = b - R*(sin(alpha)**2) - e*(1 - sin(alpha))
        s_hi = (R*(psi_max - atan(psi_max) - inv(alpha)) - h) * cot(alpha)
        psi_max = sqrt((r_a / R0)**2 - 1)
        print s_lo, s, s_hi

    # Assume s between s_lo and s_hi.
    psi_min = tan(alpha) + (s + e*(1 - sin(alpha)) - b) / (R0 * sin(alpha)) # XXX sin in denum?
    gamma = (h + s*tan(alpha))/R + inv(alpha)
    phi_min = psi_min - alpha - gamma
    psi_max = sqrt((r_a / R0)**2 - 1)

    phi_max = -(h + e*sec(alpha) + (b - e)*tan(alpha)) / R

    tooth_begin = -pi/z

    if False:
        sys.stderr.write("Range of theta: %g %g\n" % (tooth_begin, phi_max))
        sys.stderr.write("Range of phi: %g %g\n" % (phi_max, phi_min))
        sys.stderr.write("Range of psi: %g %g\n" % (psi_min, psi_max))
        sys.stderr.write("Range of top: %g %g\n" % (psi_max, 0.0))
        sys.stderr.write("Gamma: %g\n" % (gamma,))

    # Single tooth.
    p = []

    # Root.
    if True:
        theta_begin = tooth_begin
        theta_end = phi_max
        for i in range(NUM_POINTS_ROOT):
            theta = theta_begin + (theta_end - theta_begin)*i/(NUM_POINTS_ROOT - 1)
            x = sin(theta)*r_b
            y = cos(theta)*r_b
            p.append( (x, y) )

    # Fillet.
    if True:
        phi_begin = phi_max
        phi_end = phi_min
        for i in range(NUM_POINTS_FILLET):
            phi = phi_begin + (phi_end - phi_begin)*i/(NUM_POINTS_FILLET - 1)
            Lambda = 1 + e/sqrt((R*phi + u_c)**2 + (s + v_c)**2)
            X = Lambda*(R*phi + u_c)
            Y = R + Lambda*(s + v_c)
            x = X*cos(phi) - Y*sin(phi)
            y = X*sin(phi) + Y*cos(phi)
            p.append( (-x, y) )

    # Flank.
    if True:
        psi_begin = psi_min
        psi_end = psi_max
        for i in range(NUM_POINTS_FLANK):
            psi = psi_begin + (psi_end - psi_begin)*i/(NUM_POINTS_FLANK - 1)
            r = R0*sqrt(1 + psi**2)
            theta = gamma + involute(psi)
            x = sin(theta)*r
            y = cos(theta)*r
            p.append( (-x, y) )

    # Top.
    if True:
        theta_begin = -(gamma + involute(psi_max))
        theta_end = 0.0
        for i in range(NUM_POINTS_TOP):
            theta = theta_begin + (theta_end - theta_begin)*i/(NUM_POINTS_TOP - 1)
            x = sin(theta)*r_a
            y = cos(theta)*r_a
            p.append( (x, y) )

    # Mirror the tooth.
    mirror_p = [(-x,y) for x,y in p]
    p.extend(reversed(mirror_p))

    # Draw each tooth.
    P = []
    for tooth in range(z):
        # Transform to tooth position.
        phi = -2*(tooth*pi + angle_offset)/z

        for x, y in p:
            P.append( ((x*cos(phi) - y*sin(phi))*module,
                       -(x*sin(phi) + y*cos(phi))*module) )

    piece = {
        "cx": cx,
        "cy": cy,
        "type": "gear",
        "color": color,
        "points": P,
        "touch_radius": R*module,
        "base_radius": R0*module,
        "hole_radius": hole_radius,
    }
    return piece
