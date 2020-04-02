from typing import Tuple, List, Optional

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
    first_point: FloatDot
    second_point: FloatDot

    def __init__(self, point1: Dot, point2: Dot):
        between_point = FloatDot((point1.x + point2.x)/2, (point1.y + point2.y)/2)
        if point1.y == point2.y:
            self.slope = None
            self.b = None
            self.first_point = FloatDot(between_point.x, 0)
            self.second_point = FloatDot(between_point.x, CANVAS_HEIGHT)
        elif point1.x == point2.x:
            self.slope = 0
            self.b = between_point.y
            self.first_point = FloatDot(0, between_point.y)
            self.second_point = FloatDot(CANVAS_WIDTH, between_point.y)
        else:
            self.slope = (point1.x - point2.x)/(point2.y - point1.y)
            self.b = between_point.y - self.slope * between_point.x
            if self.slope > 0:
                x = -self.b/self.slope
                if 0 <= x <= CANVAS_WIDTH:
                    self.first_point = FloatDot(x, 0)
                else:
                    self.first_point = FloatDot(0, self.b)

                y = self.slope * CANVAS_WIDTH + self.b
                if 0 <= y <= CANVAS_HEIGHT:
                    self.second_point = FloatDot(CANVAS_WIDTH, y)
                else:
                    self.second_point = FloatDot((CANVAS_HEIGHT - self.b) / self.slope, CANVAS_HEIGHT)
            else:
                x = -self.b/self.slope
                if 0 <= x <= CANVAS_WIDTH:
                    self.first_point = FloatDot(x, 0)
                else:
                    self.first_point = FloatDot(CANVAS_WIDTH, self.slope * CANVAS_WIDTH + self.b)

                if 0 <= self.b <= CANVAS_HEIGHT:
                    self.second_point = FloatDot(0, self.b)
                else:
                    self.second_point = FloatDot((CANVAS_HEIGHT - self.b) / self.slope, CANVAS_HEIGHT)
        self._check_points(self.first_point, self.second_point)

    def set_first_point(self, point: FloatDot):
        self._check_points(point, self.second_point)
        self.first_point = point

    def set_second_point(self, point: FloatDot):
        self._check_points(self.first_point, point)
        self.second_point = point

    @staticmethod
    def _check_points(p1: FloatDot, p2: FloatDot):
        assert p1.y <= p2.y, f"p1 y is greater then p2 y"
        if p1.y == p2.y:
            assert p1.x <= p2.x, f"p1 x is greater then p2 x, and p1 y == p2 y"

    def in_borders(self, point1: FloatDot) -> bool:
        if self.first_point.x >= self.second_point.x:
            res = self.second_point.x <= point1.x <= self.first_point.x
        else:
            res = self.first_point.x <= point1.x <= self.second_point.x

        return res and self.first_point.y <= point1.y <= self.second_point.y

    def func(self, x: float) -> float:
        assert self.slope is not None
        return self.slope * x + self.b


def intersection(edge1: VDEdge, edge2: VDEdge) -> Optional[FloatDot]:
    def check_vert_and_line(vert: VDEdge, line: VDEdge) -> Optional[FloatDot]:
        y = line.func(vert.first_point.x)
        fd = FloatDot(vert.first_point.x, y)
        return fd if vert.in_borders(fd) and line.in_borders(fd) else None

    if edge1.slope is None and edge2.slope is None:
        return None if edge1.first_point.x != edge2.first_point.x else edge1.first_point

    if edge1.slope is None:
        return check_vert_and_line(edge1, edge2)

    if edge2.slope is None:
        return check_vert_and_line(edge2, edge1)

    if edge1.slope == 0 and edge2.slope == 0:
        return None if edge1.b != edge2.b else edge1.first_point

    x = (edge2.b - edge1.b) / (edge1.slope - edge2.slope)
    y = edge1.func(x)

    fd = FloatDot(x, y)
    return fd if edge1.in_borders(fd) and edge2.in_borders(fd) else None
