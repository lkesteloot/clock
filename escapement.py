
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

from math import sin, cos, tan, sqrt, pi, atan, floor, acos

from vector import Vector
from config import DPI, TAU
import bind
import draw

DEG_TO_RAD = pi/180
RAD_TO_DEG = 1/DEG_TO_RAD

# Escapement wheel parameters.
ESC_RADIUS = 2*DPI
ESC_TOOTH_HEIGHT = 0.5*DPI
ESC_TOOTH_COUNT = 15
ESC_TOOTH_ANGLE = TAU/ESC_TOOTH_COUNT
ESC_FILLET_POINT_COUNT = 10
ESC_CREST_FILLET_RADIUS = 0.04*DPI
ESC_TROUGH_FILLET_RADIUS = 0.06*DPI

# Offset of verge center from escapement center.
VERGE_OFFSET = Vector(0, 5*DPI)

# Angle around escapement where the points are.
VERGE_ANGLE = ESC_TOOTH_ANGLE*5.5
VERGE_LEFT_ANGLE = TAU/4 + VERGE_ANGLE/2
VERGE_RIGHT_ANGLE = TAU/4 - VERGE_ANGLE/2

# Distance from center of escapement to points.
VERGE_POINT_RADIUS = ESC_RADIUS*1.1

# Height of verge tooth.
VERGE_TOOTH_HEIGHT = 0.5*DPI

# Width of verge tooth.
VERGE_TOOTH_WIDTH = 1*DPI

# Length of control vectors between the teeth.
VERGE_CTRL = 1.5*DPI

# Offset and Bezier control vector for middle control point.
VERGE_MIDDLE_OFFSET = Vector(1.5*DPI, -1*DPI)
VERGE_MIDDLE_CTRL = Vector(1*DPI, -1*DPI)

# Offset and Bezier control vector for bottom control point.
VERGE_BOTTOM_OFFSET = Vector(0, 8*DPI)
VERGE_BOTTOM_CTRL = Vector(1*DPI, 0)

def generate_escapement_wheel(color, center, angle_offset_deg, speed, hole_radius, cz):
    # We're making a triangle tooth but with fillets on both the crest and the
    # trough. Throughout this code, variables that end with "c" are for the
    # crest, those that end with "t" are for the trough.

    # Radial distance to crest and trough fillet circle centers.
    rdc = ESC_RADIUS + (ESC_TOOTH_HEIGHT - ESC_CREST_FILLET_RADIUS)/2;
    rdt = ESC_RADIUS - (ESC_TOOTH_HEIGHT - ESC_TROUGH_FILLET_RADIUS)/2;

    # Centers of the crest and trough circles.
    cc = Vector(rdc, 0)
    ct = Vector(rdt, 0).rotated(ESC_TOOTH_ANGLE/2)

    # Now we need to know how much of these circles to draw. We need to draw
    # just enough so that the remaining line segment between them is tangent
    # to both circles. One way to determine a line tangent to two circles is
    # to determine a line between the center of one circle and an imaginary
    # circle that's centered on the other circle and the sum of the two
    # radii. This pretend circle will have the suffix "p".
    rp = ESC_CREST_FILLET_RADIUS + ESC_TROUGH_FILLET_RADIUS

    # If our pretend circle is centered on the crest fillet, then we have a
    # triangle with these three points: (1) The center of the trough triangle,
    # (2) the center of the crest triangle, and (3) the point on the pretend
    # circle. The angle at point 3 is a right angle, since line (1-3) is
    # tangent to our pretend circle. We must calculate the angle at point 2.
    hyp = (cc - ct).length()
    angle = acos(rp / hyp)

    # This angle is independent of the relative orientation of our two fillets,
    # but for us we need to know the absolute angle. We therefore subtract it
    # from the angle between the two centers.
    angle = (ct - cc).angle() - angle

    # Make the points for each tooth.
    tooth_points = []

    # Fillet for the crest.
    for i in range(ESC_FILLET_POINT_COUNT):
        t = float(i)/(ESC_FILLET_POINT_COUNT - 1)
        theta = -angle + t*angle*2
        tooth_points.append(cc + Vector.circle(theta)*ESC_CREST_FILLET_RADIUS)

    # Fillet for the trough.
    for i in range(ESC_FILLET_POINT_COUNT):
        t = float(i)/(ESC_FILLET_POINT_COUNT - 1)
        # We have to subtract tooth_angle here because the math above
        # does not take into account that the two circles repeat
        # in a circle.
        theta = angle - t*(angle*2 - ESC_TOOTH_ANGLE) + pi
        tooth_points.append(ct + Vector.circle(theta)*ESC_TROUGH_FILLET_RADIUS)

    # Stamp each tooth.
    p = []
    for tooth in range(ESC_TOOTH_COUNT):
        # Transform to tooth position.
        phi = tooth*ESC_TOOTH_ANGLE + angle_offset_deg*DEG_TO_RAD

        for v in tooth_points:
            p.append(v.rotated(phi))

    # Close curve.
    p.append(p[0])

    piece = {
        "type": "escapement_wheel",
        "color": color,
        "points": [v.to_pair() for v in p],
        "cx": center.x,
        "cy": center.y,
        "cz": cz,
        "speed": speed,
        "hole_radius": hole_radius,
    }
    return piece

def generate_verge(color, esc_center, speed, hole_radius, cz):
    # esc_center is the center of the escapement. Come up with our own center.
    center = esc_center + VERGE_OFFSET

    zero = Vector(VERGE_POINT_RADIUS, 0)
    left_point = esc_center + zero.rotated(VERGE_LEFT_ANGLE)
    right_point = esc_center + zero.rotated(VERGE_RIGHT_ANGLE)

    left_base = (left_point - esc_center).normalized()*VERGE_TOOTH_HEIGHT
    right_base = (right_point - esc_center).normalized()*VERGE_TOOTH_HEIGHT

    left_out = left_point + left_base + left_base.reciprocal().normalized()*VERGE_TOOTH_WIDTH/2
    left_in = left_point + left_base - left_base.reciprocal().normalized()*VERGE_TOOTH_WIDTH/2

    right_out = right_point + right_base - right_base.reciprocal().normalized()*VERGE_TOOTH_WIDTH/2
    right_in = right_point + right_base + right_base.reciprocal().normalized()*VERGE_TOOTH_WIDTH/2

    p = []

    # Left tooth.
    p.append(left_out)
    p.append(left_point)
    p.append(left_in)

    # Between teeth.
    left_ctrl = left_in + (left_in - left_point).normalized()*VERGE_CTRL
    right_ctrl = right_in + (right_in - right_point).normalized()*VERGE_CTRL
    draw.add_bezier(p, left_in, left_ctrl, right_ctrl, right_in, 100)

    # Right tooth.
    p.append(right_in)
    p.append(right_point)
    p.append(right_out)

    # Path to right of right tooth.
    ctrl = right_out + (right_out - right_point).normalized()*VERGE_CTRL
    middle = center + VERGE_MIDDLE_OFFSET
    draw.add_bezier(p, right_out, ctrl, middle + VERGE_MIDDLE_CTRL, middle, 100)

    # Path to bottom.
    bottom = center + VERGE_BOTTOM_OFFSET
    draw.add_bezier(p, middle, middle - VERGE_MIDDLE_CTRL, bottom + VERGE_BOTTOM_CTRL, bottom, 100)

    # Path back from bottom on left.
    middle = center + VERGE_MIDDLE_OFFSET.flipX()
    draw.add_bezier(p, bottom, bottom - VERGE_BOTTOM_CTRL, middle - VERGE_MIDDLE_CTRL.flipX(), middle, 100)

    # Path to the left of left tooth.
    ctrl = left_out + (left_out - left_point).normalized()*VERGE_CTRL
    draw.add_bezier(p, middle, middle + VERGE_MIDDLE_CTRL.flipX(), ctrl, left_out, 100)

    # Normalize to our own center.
    p = [v - center for v in p]

    piece = {
        "type": "verge",
        "color": color,
        "points": [v.to_pair() for v in p],
        "cx": center.x,
        "cy": center.y,
        "cz": cz,
        "speed": speed,
        "hole_radius": hole_radius,
        "left_full_in_angle": -4,
        "right_full_in_angle": 4,
    }
    return piece

# "origin" is the center of the escapement wheel.
def generate(data, origin, speed, hole_radius, cz=0):
    # Home.
    escapement_angle_offset = 4.0

    # Escapement wheel.
    piece = generate_escapement_wheel("#FF6666", origin,
            escapement_angle_offset, speed, hole_radius, cz)
    bind.add_bind_info(piece)
    data["pieces"].append(piece)

    # Verge.
    if True:
        piece = generate_verge("#FF0000", origin, speed, hole_radius, cz)
        data["pieces"].append(piece)
