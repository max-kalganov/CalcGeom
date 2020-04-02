import random
from typing import List, Tuple, Any

from Models import VDEdge
from ct import CANVAS_WIDTH, CANVAS_HEIGHT, DEFAULT_NUM_OF_POINTS_CONVEXHULL
from visualizer import VisualizerConvexHull
import numpy as np
from scipy.spatial import ConvexHull


class VoronoiDiagram:
    def __init__(self):
        self.windows_width = 10

    def init_points_function(self, obj: VisualizerConvexHull, number_of_points=DEFAULT_NUM_OF_POINTS_CONVEXHULL):
        self.all_points = []
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
            self.all_points.append([x, y])

        self.all_points = sorted(self.all_points, key=lambda point: (point[0], point[1]))

    def _get_vor_and_conv(self, points: List[List[int]]) -> Tuple[Any, Any]:
        if len(points) < 3:
            conv_points = points
            vor_points = self._get_vor(points)
            return vor_points, conv_points

        s1, s2 = self._divide_points(points)
        vor_s1, conv_s1 = self._get_vor_and_conv(s1)
        vor_s2, conv_s2 = self._get_vor_and_conv(s2)
        merged_conv, first_pair, last_pair = self._merge_conv(conv_s1, conv_s2)
        merged_vor = self._merge_vor(vor_s1, vor_s2, first_pair, last_pair)
        return merged_vor, merged_conv

    @staticmethod
    def _divide_points(points) -> Tuple[List[List[int]], List[List[int]]]:
        return points[:(len(points)//2)], points[(len(points)//2):]

    @staticmethod
    def _merge_conv(conv_s1: List[List[int]], conv_s2: List[List[int]]):
        full = conv_s2 + conv_s1
        try:
            hull = ConvexHull(full)
        except Exception as e:
            x_ = conv_s2[0][0]
            x_count = 1
            y_ = conv_s2[1][1]
            y_count = 1
            for point in full[1:]:
                if point[0] == x_:
                    x_count += 1
                if point[1] == y_:
                    y_count += 1
            if y_count == len(full) or x_count == len(full):
                return full, None, None
            raise e
        return [full[point] for point in hull.vertices], None, None

    def action_decor(self, vis: VisualizerConvexHull):
        vor, _ = self._get_vor_and_conv(self.all_points)
        self._draw_vor(vor, vis)

    def _draw_vor(self, vor: List[VDEdge], vis: VisualizerConvexHull):
        for edge in vor:
            vis.canv.create_line(edge.between_point.x, edge.between_point.y, edge.angle_point.x, edge.angle_point.y)
        vis.canv.pack()

    def _get_vor(self, points: List[List[int]]) -> List[VDEdge]:
        if len(points) == 1:
            return []
        assert len(points) == 2
        return [VDEdge(points[0], points[1])]

    def _merge_vor(self, vor_s1: List[VDEdge], vor_s2: List[VDEdge], first_pair, last_pair) -> List[VDEdge]:
        return vor_s1 + vor_s2


if __name__ == '__main__':
    alg = VoronoiDiagram()
    v = VisualizerConvexHull(init_func=alg.init_points_function,
                             action_func=alg.action_decor)

