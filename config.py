
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

DPI = 72
# For plates or the whole train.
WIDTH = 24 * DPI
HEIGHT = 8 * DPI
# For cut parts.
if False:
    WIDTH = 24 * DPI
    HEIGHT = 18 * DPI
TAU = 2*math.pi

SCALE = 1

NUM_POINTS_ROOT = 10
NUM_POINTS_FILLET = 10
NUM_POINTS_FLANK = 10
NUM_POINTS_TOP = 10

# Space between coupled gears
GEAR_SPACING = 0.05*DPI

# Size of tooth.
MODULE = 0.10*DPI

# Conversion
MM_TO_INCH = 0.0393701

# Main axle sizes.
TIGHT_LARGE_BOLT_RADIUS = 0.3125/2*DPI # See [1].
LOOSE_LARGE_BOLT_RADIUS = TIGHT_LARGE_BOLT_RADIUS*1.1
BEARING_RADIUS = 22.0/2*MM_TO_INCH*DPI - 0.002*DPI

# Hand-picked to be smaller than the inside of the tooth of the smallest gear.
SEPARATOR_RADIUS = 0.70*DPI

# Binding info. These bolts hold the gears together.
BIND_BOLT_RADIUS = 0.138/2*DPI # See [1].
LOOSE_BIND_BOLT_RADIUS = BIND_BOLT_RADIUS - 0.0035*DPI
BIND_NUT_RADIUS = 3.0/8/2*DPI
BIND_DISTANCE = 0.5625*DPI
BIND_COUNT = 6

# We're using 3/16 acrylic.
MATERIAL_THICKNESS = 3.0/16*DPI

# References:
# [1]: http://us.mt.com/dam/mt_ext_files/Editorial/Generic/5/bolt_thread_types_dimensions_0x0002464400026aa20006025d_files/bolt.pdf
