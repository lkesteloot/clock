import math

from config import LOOSE_BIND_BOLT_RADIUS, BIND_DISTANCE, BIND_COUNT, TAU

def add_bind_info(piece):
    centers = []
    for i in range(BIND_COUNT):
        t = float(i)/BIND_COUNT*TAU
        centers.append((math.cos(t)*BIND_DISTANCE, math.sin(t)*BIND_DISTANCE))

    piece["bind"] = {
        "hole_radius": LOOSE_BIND_BOLT_RADIUS,
        "centers": centers,
    }

