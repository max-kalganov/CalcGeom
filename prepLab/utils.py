from typing import Tuple

import numpy as np


def dist(a):
    return np.sqrt(a[0] ** 2 + a[1] ** 2)


def dist_between_points(p1: Tuple[int, int], p2: Tuple[int, int]) -> float:
    diff = p2[0] - p1[0], p2[1] - p1[1]
    return dist(diff)
