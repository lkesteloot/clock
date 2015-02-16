
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
import argparse
from math import sin, cos, tan, sqrt, pi, atan, floor, acos

from vector import Vector
from config import DPI, TAU
import bind

WIDTH = 16 * DPI
HEIGHT = 12 * DPI

DEG_TO_RAD = pi/180
RAD_TO_DEG = 1/DEG_TO_RAD

# Dimensions are in points.
VERT_DIST_PT = 312   # Get this from the output of gear.py

# Escapement wheel parameters.
ESC_RADIUS = 3*DPI
ESC_TOOTH_HEIGHT = 0.5*DPI
ESC_TOOTH_COUNT = 30
ESC_FILLET_POINT_COUNT = 10
ESC_CREST_FILLET_RADIUS = 0.02*DPI
ESC_TROUGH_FILLET_RADIUS = 0.08*DPI

UNSCALED_ROOT_RADIUS = 3 * DPI
UNSCALED_TOOTH_HEIGHT = 1 * DPI
UNSCALED_OFFSET = 50.0/72 * DPI
UNSCALED_TOTAL_OFFSET = UNSCALED_ROOT_RADIUS + UNSCALED_TOOTH_HEIGHT*2 + UNSCALED_OFFSET
SCALE = float(VERT_DIST_PT) / UNSCALED_TOTAL_OFFSET
ROOT_RADIUS = UNSCALED_ROOT_RADIUS * SCALE
TOOTH_HEIGHT = UNSCALED_TOOTH_HEIGHT * SCALE
TOOTH_CLIP = 0.90
FRONT_ANGLE_TIP_DEG = 10
BACK_ANGLE_TIP_DEG = 22
ESCAPEMENT_CENTER = Vector(0, 0)
VERGE_CENTER = ESCAPEMENT_CENTER + Vector(0, -UNSCALED_TOTAL_OFFSET*SCALE)

VERGE_WIDTH = 0.25 * DPI * SCALE
DROP_DISTANCE = 0.14 * DPI * SCALE
VERGE_SMALL_RADIUS = 1 * DPI * SCALE
VERGE_LEFT_INNER_RADIUS = 4.25 * DPI * SCALE
VERGE_LEFT_OUTER_RADIUS = VERGE_LEFT_INNER_RADIUS + VERGE_WIDTH
SPREAD_DEG = 43
DEPTH_DEG = 15
VERGE_LEFT_INNER_DEG = 270 - SPREAD_DEG
VERGE_LEFT_OUTER_DEG = VERGE_LEFT_INNER_DEG - 2
VERGE_LEFT_BACK_DEG = VERGE_LEFT_INNER_DEG - DEPTH_DEG
VERGE_RIGHT_INNER_RADIUS = VERGE_LEFT_INNER_RADIUS + DROP_DISTANCE
VERGE_RIGHT_OUTER_RADIUS = VERGE_RIGHT_INNER_RADIUS + VERGE_WIDTH
VERGE_RIGHT_INNER_DEG = 270 + SPREAD_DEG
VERGE_RIGHT_OUTER_DEG = VERGE_RIGHT_INNER_DEG - 2
VERGE_RIGHT_BACK_DEG = VERGE_RIGHT_INNER_DEG + DEPTH_DEG
VERGE_STEP_DEG = 1

VERGE_RIGHT_INNER_FRONT_DEG = VERGE_RIGHT_BACK_DEG - int(VERGE_WIDTH*180/(pi*VERGE_RIGHT_INNER_RADIUS))
VERGE_LEFT_INNER_FRONT_DEG = VERGE_LEFT_BACK_DEG + int(VERGE_WIDTH*180/(pi*VERGE_LEFT_INNER_RADIUS))
VERGE_RIGHT_SMALL_FRONT_DEG = VERGE_RIGHT_BACK_DEG - int(VERGE_WIDTH/2*180/(pi*VERGE_SMALL_RADIUS))
VERGE_LEFT_SMALL_FRONT_DEG = VERGE_LEFT_BACK_DEG + int(VERGE_WIDTH/2*180/(pi*VERGE_SMALL_RADIUS))
VERGE_RIGHT_SMALL_BACK_DEG = VERGE_RIGHT_BACK_DEG + int(VERGE_WIDTH/2*180/(pi*VERGE_SMALL_RADIUS))
VERGE_LEFT_SMALL_BACK_DEG = VERGE_LEFT_BACK_DEG - int(VERGE_WIDTH/2*180/(pi*VERGE_SMALL_RADIUS))

# Given a tooth description and the tooth angle from radial (from tip), returns
# the angle from the center of the wheel. I couldn't find a closed form for
# this, so we just look for it.
def find_tooth_angle(root_radius, tooth_height, tooth_angle_tip_deg):
    low_rad = 0
    high_rad = pi/4

    for i in range(10):
        mid_rad = (low_rad + high_rad) / 2
        c = root_radius * cos(mid_rad)
        s = root_radius * sin(mid_rad)

        candidate_tooth_angle_tip_rad = atan(s / (root_radius + tooth_height - c))
        candidate_tooth_angle_tip_deg = candidate_tooth_angle_tip_rad * RAD_TO_DEG

        if candidate_tooth_angle_tip_deg > tooth_angle_tip_deg:
            high_rad = mid_rad
        else:
            low_rad =  mid_rad

    tooth_angle_deg = int(floor((low_rad + high_rad) / 2 * RAD_TO_DEG + 0.5))

    sys.stderr.write("find_tooth_angle(%g) = %g\n" % (tooth_angle_tip_deg, tooth_angle_deg))

    return tooth_angle_deg

def auto_range(begin, end):
    if begin <= end:
        return range(begin, end + 1)
    else:
        return range(begin, end - 1, -1)

def add_arc(p, begin_deg, end_deg, radius):
    sys.stderr.write("Drawing from %d to %d at %g\n" % (begin_deg, end_deg, radius) )
    for deg in auto_range(begin_deg, end_deg):
        rad = deg*DEG_TO_RAD
        p.append(Vector(cos(rad), sin(rad))*radius)

def generate_escapement_wheel_old(color, center, angle_offset_deg, speed, hole_radius, cz):
    # Angle where the arc ends and the tooth starts.
    front_angle_deg = find_tooth_angle(ROOT_RADIUS, TOOTH_HEIGHT, FRONT_ANGLE_TIP_DEG)

    # Angle when the tooth ends and the arc starts. Larger than front_angle_deg.
    back_angle_deg = find_tooth_angle(ROOT_RADIUS, TOOTH_HEIGHT, BACK_ANGLE_TIP_DEG)

    # Make the points for each tooth.
    tooth_points = []

    # Start at previous tooth's end of tooth. That's our end of tooth minus one
    # tooth's worth of degrees.
    add_arc(tooth_points, back_angle_deg - 360/NUM_TEETH, front_angle_deg, ROOT_RADIUS)

    # The tip of the tooth is at zero degrees. Start where the arc ended and go
    # TOOTH_CLIP of the way to the tip.
    rad = front_angle_deg*DEG_TO_RAD
    end_of_arc = Vector(cos(rad), sin(rad))*ROOT_RADIUS
    tip_of_tooth = Vector(ROOT_RADIUS + TOOTH_HEIGHT, 0.0)
    tooth_points.append(end_of_arc + (tip_of_tooth - end_of_arc)*TOOTH_CLIP)

    # Move over a bit for the clipped tooth. Interpolate like we did just now,
    # but go to the start of the arc.
    rad = back_angle_deg*DEG_TO_RAD
    start_of_arc = Vector(cos(rad), sin(rad))*ROOT_RADIUS
    tooth_points.append(start_of_arc + (tip_of_tooth - start_of_arc)*TOOTH_CLIP)

    # Draw each tooth.
    p = []
    for tooth in range(NUM_TEETH):
        # Transform to tooth position.
        phi = tooth*2*pi/NUM_TEETH + angle_offset_deg*DEG_TO_RAD

        for v in tooth_points:
            # Flip X so that the teeth are pointing the right way.
            p.append(v.rotated(phi).flipX())

    # Close curve.
    p.append(p[0])

    piece = {
        "type": "escapement_wheel",
        "color": color,
        "points": [(v.x, v.y) for v in p],
        "cx": center.x,
        "cy": center.y,
        "cz": cz,
        "speed": speed,
        "hole_radius": hole_radius,
    }
    return piece

def generate_escapement_wheel(color, center, angle_offset_deg, speed, hole_radius, cz):
    # We're making a triangle tooth but with fillets on both the crest and the
    # trough. Throughout this code, variables that end with "c" are for the
    # crest, those that end with "t" are for the trough.

    # Angle of entire tooth.
    tooth_angle = TAU/ESC_TOOTH_COUNT

    # Radial distance to crest and trough fillet circle centers.
    rdc = ESC_RADIUS + (ESC_TOOTH_HEIGHT - ESC_CREST_FILLET_RADIUS)/2;
    rdt = ESC_RADIUS - (ESC_TOOTH_HEIGHT - ESC_TROUGH_FILLET_RADIUS)/2;

    # Centers of the crest and trough circles.
    cc = Vector(rdc, 0)
    ct = Vector(rdt, 0).rotated(tooth_angle/2)

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
        theta = angle - t*(angle*2 - tooth_angle) + pi
        tooth_points.append(ct + Vector.circle(theta)*ESC_TROUGH_FILLET_RADIUS)

    # Stamp each tooth.
    p = []
    for tooth in range(ESC_TOOTH_COUNT):
        # Transform to tooth position.
        phi = tooth*tooth_angle + angle_offset_deg*DEG_TO_RAD

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

def generate_verge(color, center, angle_offset_deg, speed, hole_radius, cz):
    left_full_in_angle, _, _ = find_intersection_rotation(
            VERGE_CENTER, VERGE_LEFT_OUTER_RADIUS,
            ESCAPEMENT_CENTER, ROOT_RADIUS + TOOTH_HEIGHT, True)
    left_full_in_angle -= VERGE_LEFT_BACK_DEG
    right_full_in_angle, _, _ = find_intersection_rotation(
            VERGE_CENTER, VERGE_RIGHT_INNER_RADIUS,
            ESCAPEMENT_CENTER, ROOT_RADIUS + TOOTH_HEIGHT, False)
    right_full_in_angle -= VERGE_RIGHT_INNER_FRONT_DEG

    p = []
    add_arc(p, VERGE_RIGHT_BACK_DEG, VERGE_RIGHT_OUTER_DEG, VERGE_RIGHT_OUTER_RADIUS)
    add_arc(p, VERGE_RIGHT_INNER_DEG, VERGE_RIGHT_INNER_FRONT_DEG, VERGE_RIGHT_INNER_RADIUS)
    add_arc(p, VERGE_RIGHT_SMALL_FRONT_DEG, VERGE_LEFT_SMALL_FRONT_DEG, VERGE_SMALL_RADIUS)
    add_arc(p, VERGE_LEFT_INNER_FRONT_DEG, VERGE_LEFT_INNER_DEG, VERGE_LEFT_INNER_RADIUS)
    add_arc(p, VERGE_LEFT_OUTER_DEG, VERGE_LEFT_BACK_DEG, VERGE_LEFT_OUTER_RADIUS)
    add_arc(p, VERGE_LEFT_SMALL_BACK_DEG, VERGE_RIGHT_SMALL_BACK_DEG - 360, VERGE_SMALL_RADIUS)

    # Close shape.
    p.append(p[0])

    # Rotate and translate to position, flip Y vertically.
    phi = angle_offset_deg*DEG_TO_RAD
    # Flip X so that the teeth are pointing the right way.
    p = [v.rotated(phi).flipX() for v in p]

    piece = {
        "type": "verge",
        "color": color,
        "points": [(v.x, v.y) for v in p],
        "cx": center.x,
        "cy": center.y,
        "cz": cz,
        "speed": speed,
        "hole_radius": hole_radius,
        "left_full_in_angle": left_full_in_angle,
        "right_full_in_angle": right_full_in_angle,
    }
    return piece

# Return the angle in degrees that circle 1 (at center c1, radius r1) would have
# to rotate so that the point at (r1,0) were on circle 2 (at center c2, radius r2).
def find_intersection_rotation(c1, r1, c2, r2, turn_right):
    # Distance between circle centers.
    d = (c2 - c1).length()
    sys.stderr.write("d = " + str(d) + "\n")

    # Distance to line going through intersecting points.
    a = (r1**2 - r2**2 + d**2) / (2*d)
    sys.stderr.write("a = " + str(a) + "\n")

    # Distance from line connecting centers to intersecting points.
    h = sqrt(r1**2 - a**2)
    sys.stderr.write("h = " + str(h) + "\n")

    # Point at intersection of both lines.
    c = c1 + (c2 - c1)*a/d
    sys.stderr.write("c = " + str(c) + "\n")

    # Point at intersection that's a right-hand turn from circle 1.
    turn_vector = (c2 - c1).reciprocal()*h/d
    if turn_right:
        p = c - turn_vector
    else:
        p = c + turn_vector
    sys.stderr.write("p = " + str(p) + "\n")

    # Find angle.
    angle = (p - c1).angle()*RAD_TO_DEG
    sys.stderr.write("angle = " + str(angle) + "\n")

    return angle, c, p

def generate(data, position_type, origin, speed, hole_radius, cz=0):
    if position_type == 0:
        # Home. Not very interesting.
        escapement_angle_offset = 4.0
        verge_angle_offset = -4.0
    elif position_type == 1:
        # Left fully in.
        escapement_angle_offset, c, p = find_intersection_rotation(
                ESCAPEMENT_CENTER, ROOT_RADIUS + TOOTH_HEIGHT,
                VERGE_CENTER, VERGE_LEFT_OUTER_RADIUS, False)
        verge_angle_offset, c, p = find_intersection_rotation(
                VERGE_CENTER, VERGE_LEFT_OUTER_RADIUS,
                ESCAPEMENT_CENTER, ROOT_RADIUS + TOOTH_HEIGHT, True)
        verge_angle_offset -= VERGE_LEFT_BACK_DEG
    elif position_type == 2:
        # Left barely in.
        escapement_angle_offset, c, p = find_intersection_rotation(
                ESCAPEMENT_CENTER, ROOT_RADIUS + TOOTH_HEIGHT,
                VERGE_CENTER, VERGE_LEFT_OUTER_RADIUS, False)
        verge_angle_offset, c, p = find_intersection_rotation(
                VERGE_CENTER, VERGE_LEFT_OUTER_RADIUS,
                ESCAPEMENT_CENTER, ROOT_RADIUS + TOOTH_HEIGHT, True)
        verge_angle_offset -= VERGE_LEFT_OUTER_DEG
    elif position_type == 3:
        # Left almost slipped off.
        escapement_angle_offset, c, p = find_intersection_rotation(
                ESCAPEMENT_CENTER, ROOT_RADIUS + TOOTH_HEIGHT,
                VERGE_CENTER, VERGE_LEFT_INNER_RADIUS, False)
        verge_angle_offset, c, p = find_intersection_rotation(
                VERGE_CENTER, VERGE_LEFT_INNER_RADIUS,
                ESCAPEMENT_CENTER, ROOT_RADIUS + TOOTH_HEIGHT, True)
        verge_angle_offset -= VERGE_LEFT_INNER_DEG
    elif position_type == 4:
        # Right fully in.
        escapement_angle_offset, c, p = find_intersection_rotation(
                ESCAPEMENT_CENTER, ROOT_RADIUS + TOOTH_HEIGHT,
                VERGE_CENTER, VERGE_RIGHT_INNER_RADIUS, True)
        verge_angle_offset, c, p = find_intersection_rotation(
                VERGE_CENTER, VERGE_RIGHT_INNER_RADIUS,
                ESCAPEMENT_CENTER, ROOT_RADIUS + TOOTH_HEIGHT, False)
        verge_angle_offset -= VERGE_RIGHT_INNER_FRONT_DEG
    elif position_type == 5:
        # Right barely in.
        escapement_angle_offset, c, p = find_intersection_rotation(
                ESCAPEMENT_CENTER, ROOT_RADIUS + TOOTH_HEIGHT,
                VERGE_CENTER, VERGE_RIGHT_INNER_RADIUS, True)
        verge_angle_offset, c, p = find_intersection_rotation(
                VERGE_CENTER, VERGE_RIGHT_INNER_RADIUS,
                ESCAPEMENT_CENTER, ROOT_RADIUS + TOOTH_HEIGHT, False)
        verge_angle_offset -= VERGE_RIGHT_INNER_DEG
    elif position_type == 6:
        # Right almost slipped off.
        escapement_angle_offset, c, p = find_intersection_rotation(
                ESCAPEMENT_CENTER, ROOT_RADIUS + TOOTH_HEIGHT,
                VERGE_CENTER, VERGE_RIGHT_OUTER_RADIUS, True)
        verge_angle_offset, c, p = find_intersection_rotation(
                VERGE_CENTER, VERGE_RIGHT_OUTER_RADIUS,
                ESCAPEMENT_CENTER, ROOT_RADIUS + TOOTH_HEIGHT, False)
        verge_angle_offset -= VERGE_RIGHT_OUTER_DEG

    piece = generate_escapement_wheel("#FF6666",
            origin + ESCAPEMENT_CENTER, escapement_angle_offset, speed, hole_radius, cz)
    bind.add_bind_info(piece)
    data["pieces"].append(piece)

    if False:
        piece = generate_verge("#FF0000", origin + VERGE_CENTER, verge_angle_offset, speed, hole_radius, cz)
        bind.add_bind_info(piece)
        data["pieces"].append(piece)

def main():
    out = sys.stdout

    parser = argparse.ArgumentParser(description='Generate escapement.')
    parser.add_argument("--js", dest="output_type", action="store_const", const="js",
            default="svg", help="generate JavaScript file")
    parser.add_argument("--raw", dest="output_type", action="store_const", const="raw",
            default="svg", help="generate raw file")
    parser.add_argument("position_type", type=int, help="position of escapement to draw")

    args = parser.parse_args()

    origin = Vector(WIDTH/2, HEIGHT/2)

    data = {
        "pieces": [],
    }

    header(out, args.output_type)
    generate(out, data, args.output_type, args.position_type, origin)
    footer(out, args.output_type)

    sys.stderr.write("Sanity check: Verge width*2 = %g, tooth spacing = %g\n" %
            ((VERGE_WIDTH + DROP_DISTANCE)*2, 2*pi/NUM_TEETH*(ROOT_RADIUS + TOOTH_HEIGHT)))

if __name__ == "__main__":
    main()
