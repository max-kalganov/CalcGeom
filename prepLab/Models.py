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
    first_point: Optional[FloatDot]
    second_point: Optional[FloatDot]

    def __init__(self, point1: Dot, point2: Dot, start_point: Optional[FloatDot] = None):
        self.between_point = FloatDot((point1.x + point2.x) / 2, (point1.y + point2.y) / 2)
        self.temp = None
        self.first_point = None
        self.second_point = None
        self._get_slope_and_b(point1, point2, start_point)
        self._get_first_point(start_point)
        self._get_second_point()
        self._check_points(self.first_point, self.second_point)

    def _get_slope_and_b(self, point1: Dot, point2: Dot, start_point: FloatDot):
        if point1.y == point2.y:
            self.slope = None
            self.b = None
        elif point1.x == point2.x:
            self.slope = 0
            self.b = start_point.y if start_point else self.between_point.y
        else:
            self.slope = (point1.x - point2.x) / (point2.y - point1.y)
            if start_point:
                self.b = start_point.y - self.slope * start_point.x
            else:
                self.b = self.between_point.y - self.slope * self.between_point.x

    def _get_first_point(self, start_point: FloatDot = None):
        if start_point:
            self.first_point = start_point
        elif self.slope is None:
            self.first_point = FloatDot(self.between_point.x, float('-inf'))
        elif self.slope == 0:
            self.first_point = FloatDot(float('-inf'), self.between_point.y)
        else:
            if self.slope > 0:
                self.first_point = FloatDot(float('-inf'), float('-inf'))
            else:
                self.first_point = FloatDot(float('inf'), float('-inf'))

    def _get_second_point(self):
        if self.slope is None:
            self.second_point = FloatDot(self.between_point.x, float('inf'))
        elif self.slope == 0:
            self.second_point = FloatDot(float('inf'), self.between_point.y)
        else:
            if self.slope > 0:
                self.second_point = FloatDot(float('inf'), float('inf'))
            else:
                self.second_point = FloatDot(float('-inf'), float('inf'))

    def make_first_point_border(self):
        self.temp = self.first_point
        self._get_first_point()
        self._check_points(self.first_point, self.second_point)

    def return_first_point_from_temp(self):
        if self.temp is not None:
            self.set_first_point(self.temp)
            self.temp = None

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

    @staticmethod
    def in_map(point: FloatDot) -> bool:
        return 0 <= point.x <= CANVAS_WIDTH and 0 <= point.y <= CANVAS_HEIGHT

    def in_borders(self, point1: FloatDot) -> bool:
        if self.first_point.x >= self.second_point.x:
            res = self.first_point.x >= point1.x >= self.second_point.x
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
        assert edge1.b != edge2.b, 'Equal b, этого не должно быть, если такое случилось, ' \
                                   'нужно учитывать, что могла вернуться точка на есконечности'
        return None if edge1.b != edge2.b else edge1.first_point

    x = (edge2.b - edge1.b) / (edge1.slope - edge2.slope)
    y = edge1.func(x)

    fd = FloatDot(x, y)
    return fd if edge1.in_borders(fd) and edge2.in_borders(fd) else None

