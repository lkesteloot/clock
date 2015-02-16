
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

from config import LOOSE_BIND_BOLT_RADIUS, BIND_DISTANCE, BIND_COUNT, TAU

# Add information to a piece to allow the six binding holes to be made
# that keep gears moving together.
def add_bind_info(piece):
    centers = []
    for i in range(BIND_COUNT):
        t = float(i)/BIND_COUNT*TAU
        centers.append((math.cos(t)*BIND_DISTANCE, math.sin(t)*BIND_DISTANCE))

    piece["bind"] = {
        "hole_radius": LOOSE_BIND_BOLT_RADIUS,
        "centers": centers,
    }

