from typing import Tuple

import numpy as np


def dist(a):
    return np.sqrt(a[0] ** 2 + a[1] ** 2)


def dist_between_points(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    diff = p2[0] - p1[0], p2[1] - p1[1]
    return dist(diff)


def binsearch(points, key, val: Tuple[float, float]):
    low: int = 0
    high: int = len(points) - 1
    while low < high:
        mid = (low + high) // 2
        if key(points[mid]) < key(val):
            low = mid + 1
        else:
            high = mid
    return low if points[low] == val else -1

