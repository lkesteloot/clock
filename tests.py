
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

from config import WIDTH, HEIGHT
import draw

def main():
    out = sys.stdout

    parser = argparse.ArgumentParser(description='Generate gears.')
    parser.add_argument("command", help="command to run")

    args = parser.parse_args()

    color = "#000000"

    draw.header(out, WIDTH, HEIGHT)

    # Parts of clock for cutting. Spool.
    if args.command == "spool":
        # Inside.
        draw.circle(out, 5*DPI, 5*DPI, LOOSE_SLIP_HOLE_RADIUS, color)
        draw.circle(out, 5*DPI, 5*DPI, 0.80*DPI, color)

        # Outside.
        draw.circle(out, 10*DPI, 5*DPI, LOOSE_SLIP_HOLE_RADIUS, color)
        draw.circle(out, 10*DPI, 5*DPI, 1.25*DPI, color)
        # Hole for wire.
        draw.circle(out, 10*DPI + 0.85*DPI, 5*DPI, 0.05*DPI, color)

        # Outside.
        draw.circle(out, 15*DPI, 5*DPI, LOOSE_SLIP_HOLE_RADIUS, color)
        draw.circle(out, 15*DPI, 5*DPI, 1.25*DPI, color)

    # Low tooth-count test.
    if args.command == "low_tooth_count":
        gear_train = train.GearTrain(out, WIDTH/4, HEIGHT*3/5, 40)
        hole_radius = 0.1*DPI

        gear_train.add_gear(6, None, hole_radius)
        # gear_train.add_gear(6, train.EAST, hole_radius)

    # Laser test.
    if args.command == "laser_test":
        gear_train = train.GearTrain(out, WIDTH/4, HEIGHT*3/5, 5)
        hole_radius = 0.1*DPI

        gear_train.add_gear(64, None, hole_radius)
        gear_train.cy -= 10
        gear_train.add_gear(16, train.NORTH, hole_radius)

    # Output for cover of Graphics Engine book.
    if args.command == "ge_book":
        gear_train = train.GearTrain(out, 0, 0, 5)
        gear_train.set_angle_offset(-2)
        hole_radius = 0.05*DPI

        gear_train.add_gear(18, None, hole_radius)
        gear_train.add_gear(30, train.NORTH, hole_radius)
        gear_train.add_gear(20, None, hole_radius)
        gear_train.add_gear(60, train.WEST, hole_radius)
        gear_train.add_gear(16, None, hole_radius)
        gear_train.add_gear(64, train.NORTH, hole_radius)
        gear_train.add_gear(24, None, hole_radius)
        gear_train.add_gear(40, train.WEST, hole_radius)
        gear_train.add_gear(20, None, hole_radius)
        gear_train.add_gear(26, train.NORTH, hole_radius)
        gear_train.add_gear(16, None, hole_radius)
        gear_train.add_gear(24, train.WEST, hole_radius)

    # Hole test.
    if args.command == "hole_test":
        cx = DPI
        cy = DPI

        if False:
            r = 0.25*DPI
            for i in range(5):
                draw.circle(out, cx, cy, r, "#000000")
                cx += DPI*0.75
                r += 0.001*DPI

        if False:
            r = 0.255*DPI
            r2 = 0.40*DPI
            for i in range(3):
                draw.circle(out, cx, cy, r, "#000000")
                draw.circle(out, cx, cy, r2, "#000000")
                cx += DPI*0.95
                r += 0.001*DPI

        if True:
            r = 0.394*DPI
            for i in range(5):
                draw.circle(out, cx, cy, r, "#000000")
                cx += DPI*0.95
                r += 0.001*DPI

    # Gear for inlay.
    if args.command == "inlay":
        gear_train = train.GearTrain(out, 50, 50, 20)
        gear_train.set_angle_offset(0)
        hole_radius = 0.3*DPI

        gear_train.add_gear(18, None, hole_radius)

    draw.footer(out)

if __name__ == "__main__":
    main()
