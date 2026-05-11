import math


# MediaPipe Face Landmarker indices for six-point MAR (inner lip contour)
# Uses 478-landmark model (same indices as 468-landmark for lips)
LIP_INDICES = {
    "p1": 61,   # left corner
    "p2": 0,    # upper mid
    "p3": 269,  # upper right
    "p4": 181,  # upper left
    "p5": 291,  # right corner
    "p6": 405,  # lower right
    "p7": 409,  # lower left
    "p8": 17,   # lower mid
}


def distance(p1, p2):
    return math.hypot(p2.x - p1.x, p2.y - p1.y)


def calculate(landmarks):
    p = {}
    for key, idx in LIP_INDICES.items():
        p[key] = landmarks[idx]

    width = distance(p["p1"], p["p5"])
    if width == 0.0:
        return 0.0
    mar = (
        distance(p["p2"], p["p8"])
        + distance(p["p3"], p["p7"])
        + distance(p["p4"], p["p6"])
    ) / (3.0 * width)

    return mar
