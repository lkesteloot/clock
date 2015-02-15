import math, sys

from config import GEAR_SPACING, TAU
import gear
import separator
import bind

NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3

COLORS = [
        "#FF0000",
        "#00FF00",
        "#0000FF",
        "#FFFFFF",
        "#CCCC00",
        "#00CCCC",
        "#CC00CC",
]

class GearTrain:
    # module is distance between teeth divided by pi.
    def __init__(self, data, cx, cy, module):
        self.data = data
        self.cx = cx
        self.cy = cy
        self.last_teeth_count = 0
        self.last_plane = None
        self.color_index = 0
        self.speed = 1.0
        self.module = module
        self.angle_offset = 0

    def set_angle_offset(self, angle_offset):
        "Rotate all gears by this much, where pi means an entire tooth on a one-tooth gear."
        self.angle_offset = angle_offset

    def add_separators_to_plane(self, plane, hole_radius):
        if self.last_plane is not None:
            min_plane = min(plane, self.last_plane) + 1
            max_plane = max(plane, self.last_plane) - 1
            for separator_plane in range(min_plane, max_plane + 1):
                piece = separator.generate(self.cx, self.cy, hole_radius)
                piece["plane"] = separator_plane
                piece["speed"] = self.speed
                bind.add_bind_info(piece)
                self.data["pieces"].append(piece)

    def add_gear(self, teeth_count, direction, hole_radius, plane=1, suppress=False):
        distance = (self.last_teeth_count + teeth_count)/2.0*self.module + GEAR_SPACING

        x = self.cx
        y = self.cy

        if direction is None:
            # Different gear pair, change colors.
            self.color_index = (self.color_index + 1) % len(COLORS)

            # Make separators.
            self.add_separators_to_plane(plane, hole_radius)
        else:
            if direction == NORTH:
                y -= distance
            elif direction == EAST:
                x += distance
            elif direction == SOUTH:
                y += distance
            elif direction == WEST:
                x -= distance

            self.speed *= -float(self.last_teeth_count) / teeth_count

        # sys.stderr.write("%g %g %g %g %d\n" % (x,y,distance,MODULE,teeth_count))

        # Calculate the rotating of this new gear. It depends on the direction we went.
        # For each direction we have the position (0 - TAU tooth to tooth) of the old
        # gear in that direction and of the new gear at the opposite side of the gear.
        # We add those, move half a TAU so they interlock, and divide by 2 because the
        # angle assumes pi tooth to tooth.
        if direction == NORTH:
            angle = (self.last_teeth_count*TAU*0 + teeth_count*TAU/2 + TAU/2)/2 - self.angle_offset
        elif direction == EAST:
            angle = (self.last_teeth_count*TAU/4 + teeth_count*TAU*3/4 + TAU/2)/2 - self.angle_offset
        elif direction == SOUTH:
            angle = (self.last_teeth_count*TAU/2 + teeth_count*TAU*0 + TAU/2)/2 - self.angle_offset
        elif direction == WEST:
            angle = (self.last_teeth_count*TAU*3/4 + teeth_count*TAU/4 + TAU/2)/2 - self.angle_offset
        else:
            angle = self.angle_offset

        piece = gear.generate(x, y, teeth_count,
                hole_radius, angle, COLORS[self.color_index], self.module)

        piece["speed"] = self.speed
        piece["plane"] = plane
        bind.add_bind_info(piece)
        if not suppress:
            self.data["pieces"].append(piece)

        self.cx = x
        self.cy = y
        self.last_teeth_count = teeth_count
        self.last_plane = plane
