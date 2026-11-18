"""Cálculos geométricos internos para preparar el control del rig 3D."""

import math


# Índices MediaPipe: muñeca, pulgar, índice, medio, anular y meñique.
FINGER_CHAINS = {
    "thumb": [1, 2, 3, 4],
    "index": [5, 6, 7, 8],
    "middle": [9, 10, 11, 12],
    "ring": [13, 14, 15, 16],
    "pinky": [17, 18, 19, 20],
}


def _angle_degrees(a, b, c):
    """Ángulo ABC en grados. Los puntos son tuplas (x, y, z)."""
    ba = [a[i] - b[i] for i in range(3)]
    bc = [c[i] - b[i] for i in range(3)]
    dot = sum(ba[i] * bc[i] for i in range(3))
    norm_ba = math.sqrt(sum(v * v for v in ba))
    norm_bc = math.sqrt(sum(v * v for v in bc))
    if norm_ba < 1e-8 or norm_bc < 1e-8:
        return 0.0
    cosine = max(-1.0, min(1.0, dot / (norm_ba * norm_bc)))
    return round(math.degrees(math.acos(cosine)), 2)


def calculate_finger_angles(landmarks):
    """
    Devuelve ángulos geométricos de las articulaciones.
    Los ángulos se calculan con puntos 3D normalizados de MediaPipe.
    """
    points = [(p.x, p.y, p.z) for p in landmarks]
    result = {}

    for finger, chain in FINGER_CHAINS.items():
        a, b, c, d = chain
        result[finger] = {
            "mcp": _angle_degrees(points[0],
                                  points[a], points[b]),
            "pip": _angle_degrees(points[a], points[b], points[c]),
            "dip": _angle_degrees(points[b], points[c], points[d]),
        }

    return result
