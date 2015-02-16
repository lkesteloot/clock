
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

from math import sqrt, sin, cos, atan2

# 2D vector class.
class Vector:
    @staticmethod
    def from_pair(p):
        return Vector(p[0], p[1])

    @staticmethod
    def circle(t):
        return Vector(cos(t), sin(t))

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def __str__(self):
        return "(%g,%g)" % (self.x, self.y)

    def __repr__(self):
        return str(self)

    def __neg__(self):
        return Vector(-self.x, -self.y)

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return Vector(self.x*other, self.y*other)

    def __div__(self, other):
        return Vector(self.x/other, self.y/other)

    def length(self):
        return sqrt(self.x**2 + self.y**2)

    def normalized(self):
        return self/self.length()

    # Angle is in radians.
    def rotated(self, angle):
        return Vector(self.x*cos(angle) - self.y*sin(angle),
                      self.x*sin(angle) + self.y*cos(angle))

    # Rotated 90 counter-clockwise.
    def reciprocal(self):
        return Vector(-self.y, self.x)

    # Returns angle in radians.
    def angle(self):
        return atan2(self.y, self.x)

    def flipX(self):
        return Vector(-self.x, self.y)

    def flipY(self):
        return Vector(self.x, -self.y)

    def to_pair(self):
        return self.x, self.y

