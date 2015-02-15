
import math

from config import TAU, SEPARATOR_RADIUS

# Closed circle.
def generate_circle_points(x, y, r, n):
    p = []

    for i in range(n + 1):
        t = float(i)/n*TAU
        p.append((x + math.cos(t)*r, y + math.sin(t)*r))

    return p

def generate(x, y, hole_radius):
    piece = {
        "type": "separator",
        "cx": x,
        "cy": y,
        "plane": 0,
        "color": "#FFFFFF",
        "hole_radius": hole_radius,
        "outer_radius": SEPARATOR_RADIUS,
        "points": generate_circle_points(0, 0, SEPARATOR_RADIUS, 100),
        "speed": 0,
    }
    return piece

