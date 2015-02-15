
# Of course I didn't make it far without making a vector class.

from math import sqrt, sin, cos, atan2

class Vector:
    @staticmethod
    def from_pair(p):
        return Vector(p[0], p[1])

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

