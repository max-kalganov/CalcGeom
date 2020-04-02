import random
from typing import List, Tuple, Any, Dict

from Models import VDEdge, Dot
from ct import CANVAS_WIDTH, CANVAS_HEIGHT, DEFAULT_NUM_OF_POINTS_CONVEXHULL
from utils import get_main_dot
from visualizer import VisualizerConvexHull
import numpy as np
from scipy.spatial import ConvexHull


class VoronoiDiagram:
    def __init__(self):
        self.windows_width = 10
        self.all_points: List[Dot] = []

    def init_points_function(self, obj: VisualizerConvexHull, number_of_points=DEFAULT_NUM_OF_POINTS_CONVEXHULL):
        self.all_points: List[Dot] = []
        seen = {}
        x_values = np.random.normal(loc=CANVAS_WIDTH//2, scale=CANVAS_WIDTH//8, size=number_of_points)
        y_values = np.random.normal(loc=CANVAS_HEIGHT//2, scale=CANVAS_HEIGHT//8, size=number_of_points)

        for x, y in zip(x_values, y_values):
            x, y = int(x), int(y)
            if not 0 <= x <= CANVAS_WIDTH:
                continue
            if not 0 <= y <= CANVAS_HEIGHT:
                continue

            if x in seen:
                if y not in seen[x]:
                    seen[x].add(y)
                else:
                    continue
            else:
                seen.setdefault(x, {y})

            obj.canv.create_rectangle((x, y) * 2)
            self.all_points.append(get_main_dot(x, y))

        self.all_points = sorted(self.all_points, key=lambda point: (point.x, point.y))

    def action_decor(self, vis: VisualizerConvexHull):
        vor, _ = self._get_vor_and_conv(self.all_points)
        self._draw_vor(vor, vis)

    def _get_vor_and_conv(self, points: List[Dot]) -> Tuple[List[VDEdge], List[Dot]]:
        if len(points) < 3:
            conv_points = points
            vor_points = self._get_vor(points)
            return vor_points, conv_points

        s1, s2 = self._divide_points(points)
        vor_s1, conv_s1 = self._get_vor_and_conv(s1)
        vor_s2, conv_s2 = self._get_vor_and_conv(s2)
        merged_conv, start_left_ind, start_right_ind,\
            finish_left_ind, finish_right_ind = self._merge_conv(conv_s1, conv_s2)
        merged_vor = self._merge_vor(vor_s1, vor_s2,
                                     conv_s1, conv_s2,
                                     start_left_ind, start_right_ind,
                                     finish_left_ind, finish_right_ind)
        return merged_vor, merged_conv

    def _get_vor(self, points: List[Dot]) -> List[VDEdge]:
        if len(points) == 1:
            return []
        assert len(points) == 2
        return [VDEdge(points[0], points[1])]

    @staticmethod
    def _divide_points(points: List[Dot]) -> Tuple[List[Dot], List[Dot]]:
        return points[:(len(points)//2)], points[(len(points)//2):]

    @staticmethod
    def _merge_conv(conv_s1: List[Dot], conv_s2: List[Dot]) -> Tuple[List[Dot], int, int, int, int]:
        full = conv_s2 + conv_s1
        try:
            cur_full = []
            for i in full:
                cur_full.append([i.x, i.y])
            hull = ConvexHull(cur_full)
        except Exception as e:
            x_ = conv_s2[0].x
            x_count = 1
            y_ = conv_s2[0].y
            y_count = 1
            for point in full[1:]:
                if point.x == x_:
                    x_count += 1
                if point.y == y_:
                    y_count += 1
            if y_count == len(full) or x_count == len(full):
                return full, 0, 0, 0, 0
            raise e
        return [full[point] for point in hull.vertices], 0, 0, 0, 0

    def _merge_vor(self, vor_s1: List[VDEdge], vor_s2: List[VDEdge],
                   conv_s1: List[Dot], conv_s2: List[Dot],
                   start_left_ind: int, start_right_ind: int,
                   finish_left_ind: int, finish_right_ind: int) -> List[VDEdge]:

        return vor_s1 + vor_s2

    def _draw_vor(self, vor: List[VDEdge], vis: VisualizerConvexHull):
        for edge in vor:
            vis.canv.create_line(edge.f_point.x, edge.f_point.y, edge.s_point.x, edge.s_point.y)
        vis.canv.pack()


if __name__ == '__main__':
    alg = VoronoiDiagram()
    v = VisualizerConvexHull(init_func=alg.init_points_function,
                             action_func=alg.action_decor)

