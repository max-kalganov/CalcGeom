from typing import Tuple, List

from dataclasses import dataclass
from ct import CANVAS_HEIGHT, CANVAS_WIDTH


@dataclass
class Dot:
    x: int
    y: int

    def get_tuple(self) -> Tuple[int, int]:
        return self.x, self.y


@dataclass
class FloatDot:
    x: float
    y: float


class VDEdge:
    f_point: FloatDot
    s_point: FloatDot

    def __init__(self, point1: Dot, point2: Dot):
        between_point = FloatDot((point1.x + point2.x)/2, (point1.y + point2.y)/2)
        if point1.y == point2.y:
            self.f_point = FloatDot(between_point.x, 0)
            self.s_point = FloatDot(between_point.x, CANVAS_HEIGHT)
        elif point1.x == point2.x:
            self.f_point = FloatDot(0, between_point.y)
            self.s_point = FloatDot(CANVAS_WIDTH, between_point.y)
        else:
            slope = (point1.x - point2.x)/(point2.y - point1.y)
            b = between_point.y - slope * between_point.x
            if slope > 0:
                x = -b/slope
                if 0 <= x <= CANVAS_WIDTH:
                    self.f_point = FloatDot(x, 0)
                else:
                    self.f_point = FloatDot(0, b)

                y = slope * CANVAS_WIDTH + b
                if 0 <= y <= CANVAS_HEIGHT:
                    self.s_point = FloatDot(CANVAS_WIDTH, y)
                else:
                    self.s_point = FloatDot((CANVAS_HEIGHT - b)/slope, CANVAS_HEIGHT)
            else:
                x = -b/slope
                if 0 <= x <= CANVAS_WIDTH:
                    self.f_point = FloatDot(x, 0)
                else:
                    self.f_point = FloatDot(CANVAS_WIDTH, slope*CANVAS_WIDTH + b)

                if 0 <= b <= CANVAS_HEIGHT:
                    self.s_point = FloatDot(0, b)
                else:
                    self.s_point = FloatDot((CANVAS_HEIGHT - b)/slope, CANVAS_HEIGHT)
