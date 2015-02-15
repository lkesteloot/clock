
import sys
import argparse
import json

from config import DPI, WIDTH, HEIGHT, MODULE, TIGHT_LARGE_BOLT_RADIUS, LOOSE_LARGE_BOLT_RADIUS, MODULE, MATERIAL_THICKNESS, BEARING_RADIUS
import train
import frame
import escapement
from vector import Vector

def main():
    parser = argparse.ArgumentParser(description='Generate gears.')

    args = parser.parse_args()

    # Data file we're going to output.
    data = {
        "material_thickness": MATERIAL_THICKNESS,
        "pieces": [],
    }

    # Full clock in place.
    gear_train = train.GearTrain(data, 6*DPI, HEIGHT/2, MODULE)

    # Hour hand:
    gear_train.add_gear(64, None, LOOSE_LARGE_BOLT_RADIUS, plane=0, suppress=True)
    gear_train.add_gear(16, train.WEST, BEARING_RADIUS, plane=0)

    gear_train.add_gear(60, None, BEARING_RADIUS, plane=2)
    gear_train.add_gear(20, train.EAST, BEARING_RADIUS, plane=2)

    # Minute hand:
    gear_train.add_gear(60, None, BEARING_RADIUS, plane=4)
    gear_train.add_gear(20, train.EAST, BEARING_RADIUS, plane=4)

    mid1_holder_x = gear_train.cx

    gear_train.add_gear(49, None, BEARING_RADIUS, plane=2)
    gear_train.add_gear(20, train.EAST, BEARING_RADIUS, plane=2)

    mid2_holder_x = gear_train.cx

    gear_train.add_gear(60, None, BEARING_RADIUS, plane=0)
    gear_train.add_gear(21, train.EAST, BEARING_RADIUS, plane=0)

    mid2_holder_x = (mid2_holder_x + gear_train.cx)/2

    gear_train.add_gear(60, None, BEARING_RADIUS, plane=4)
    gear_train.add_gear(21, train.EAST, BEARING_RADIUS, plane=4)

    # Separator to escapement.
    gear_train.add_separators_to_plane(2, BEARING_RADIUS)

    # Add escapement.
    escapement.generate(data, 0, Vector(gear_train.cx, gear_train.cy), gear_train.speed, BEARING_RADIUS, plane=2)

    # Add frame.
    frame.generate(data, "#00FF00")

    json.dump(data, sys.stdout, indent=4)

if __name__ == "__main__":
    main()