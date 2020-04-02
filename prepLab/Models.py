from typing import Tuple, List

from dataclasses import dataclass


@dataclass
class Dot:
    x: int
    y: int

    def get_tuple(self) -> Tuple[int, int]:
        return (self.x, self.y)


@dataclass
class FloatDot:
    x: float
    y: float


class VDEdge:
    between_point: FloatDot
    angle_point: FloatDot

    def __init__(self, point1: List[int], point2: List[int]):
        self.between_point = FloatDot((point1[0] + point2[0])/2, (point1[1] + point2[1])/2)
        if point1[1] == point2[1]:
            self.angle_point = FloatDot(self.between_point.x, self.between_point.y + 1)
        elif point1[0] == point2[0]:
            self.angle_point = FloatDot(self.between_point.x + 1, self.between_point.y)
        else:
            slope = (point1[0] - point2[0])/(point2[1] - point1[1])
            step = 200
            self.angle_point = FloatDot(self.between_point.x + step, step*slope + self.between_point.y)


