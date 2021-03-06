
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
import json

from config import DPI, WIDTH, HEIGHT, MODULE, TIGHT_LARGE_BOLT_RADIUS, MATERIAL_THICKNESS, BEARING_RADIUS
import train
import frame
import escapement
import pendulum
from vector import Vector

def main():
    parser = argparse.ArgumentParser(description='Generate gears.')

    args = parser.parse_args()

    # Data file we're going to output.
    data = {
        "material_thickness": MATERIAL_THICKNESS,
        "dpi": DPI,
        "large_bolt_radius": TIGHT_LARGE_BOLT_RADIUS,
        "pieces": [],
    }

    # Full clock in place.
    gear_train = train.GearTrain(data, 6*DPI, HEIGHT/2, MODULE)
    escapement_cz = 0

    # Hour hand:
    gear_train.add_gear(64, None, BEARING_RADIUS, cz=0)
    gear_train.add_gear(16, train.WEST, BEARING_RADIUS, cz=0)

    gear_train.add_gear(60, None, BEARING_RADIUS, cz=2)
    gear_train.add_gear(20, train.EAST, BEARING_RADIUS, cz=2)

    # Minute hand:
    gear_train.add_gear(60, None, BEARING_RADIUS, cz=4)
    gear_train.add_gear(20, train.EAST, BEARING_RADIUS, cz=4)

    gear_train.add_gear(49, None, BEARING_RADIUS, cz=2)
    gear_train.add_gear(20, train.EAST, BEARING_RADIUS, cz=2)

    gear_train.add_gear(60, None, BEARING_RADIUS, cz=0)
    gear_train.add_gear(21, train.EAST, BEARING_RADIUS, cz=0)

    gear_train.add_gear(60, None, BEARING_RADIUS, cz=4)
    gear_train.add_gear(21, train.EAST, BEARING_RADIUS, cz=4)

    gear_train.add_gear(40, None, BEARING_RADIUS, cz=2)
    gear_train.add_gear(20, train.SOUTH, BEARING_RADIUS, cz=2)

    # Separator to escapement.
    gear_train.add_separators(escapement_cz, BEARING_RADIUS)

    # Add escapement.
    ## data["pieces"] = []
    esc_center = Vector(gear_train.cx, gear_train.cy)
    verge_center, verge_hole_offset = escapement.generate(data, esc_center,
            gear_train.speed, BEARING_RADIUS, cz=escapement_cz)

    # Add frame.
    frame.generate(data, "#00FF00")

    # Add pendulum.
    pendulum.generate(data, verge_center, verge_hole_offset, escapement_cz, gear_train.speed, "#0000FF")

    # Dump JSON output. If generating a custom object, call its to_JSON() method.
    json.dump(data, sys.stdout, indent=4, default=lambda obj: obj.to_JSON())

    gear_train.dump_statistics(sys.stderr)

if __name__ == "__main__":
    main()
