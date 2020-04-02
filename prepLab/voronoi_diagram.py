import random
from typing import List, Tuple, Any, Dict

from Models import VDEdge, Dot, intersection, FloatDot
from ct import CANVAS_WIDTH, CANVAS_HEIGHT, DEFAULT_NUM_OF_POINTS_CONVEXHULL
from utils import get_main_dot, get_border_points, get_vdedges, dist, main_dot_to_edge
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
        self._get_vor_and_conv(self.all_points)
        self._draw_vor(vis)

    def _get_vor_and_conv(self, points: List[Dot]) -> List[Dot]:
        if len(points) < 3:
            conv_points = points
            self._get_vor(points)
            return conv_points

        s1, s2 = self._divide_points(points)
        conv_s1 = self._get_vor_and_conv(s1)
        conv_s2 = self._get_vor_and_conv(s2)
        merged_conv, start_left_ind, start_right_ind,\
            finish_left_ind, finish_right_ind = self._merge_conv(conv_s1, conv_s2)
        self._merge_vor(conv_s1, conv_s2,
                        start_left_ind, start_right_ind,
                        finish_left_ind, finish_right_ind)
        return merged_conv

    def _get_vor(self, points: List[Dot]) -> List[VDEdge]:
        if len(points) == 1:
            return []
        assert len(points) == 2
        new_vdedge = VDEdge(points[0], points[1])
        get_vdedges(points[0]).append(new_vdedge)
        get_vdedges(points[1]).append(new_vdedge)

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
        full_conv = [full[point] for point in hull.vertices]
        sl_ind, sr_ind, fl_ind, fr_ind = get_border_points(full_conv, conv_s1, conv_s2)
        return full_conv, sl_ind, sr_ind, fl_ind, fr_ind

    def _merge_vor(self, conv_s1: List[Dot], conv_s2: List[Dot],
                   start_left_ind: int, start_right_ind: int,
                   finish_left_ind: int, finish_right_ind: int):
        cur_left_ind = start_left_ind
        cur_right_ind = start_right_ind

        def next_point(left: bool) -> Dot:
            global cur_left_ind, cur_right_ind
            if left:
                next_p = conv_s1[cur_left_ind]
                cur_left_ind = (cur_left_ind + 1)%len(conv_s1)
            else:
                next_p = conv_s2[cur_right_ind]
                cur_right_ind = (cur_right_ind - 1)%len(conv_s2)
            return next_p

        def find_edge(cur_point: Dot, cur_edge: VDEdge) -> Tuple[FloatDot, VDEdge]:
            for edge in get_vdedges(cur_point):
                intersec = intersection(cur_edge, edge)
                if intersec is not None:
                    return intersec, edge

        cur_left_point = next_point(True)
        cur_right_point = next_point(False)

        cur_edge = VDEdge(cur_left_point, cur_right_point)
        while cur_left_point != conv_s1[finish_left_ind] or cur_right_point != conv_s2[finish_right_ind]:
            intersec_l, e_l = find_edge(cur_left_point, cur_edge)
            intersec_r, e_r = find_edge(cur_right_point, cur_edge)
            l_dist = dist(intersec_l, cur_edge.first_point)
            r_dist = dist(intersec_r, cur_edge.first_point)
            if l_dist < r_dist:
                cur_edge.set_second_point(intersec_l)
                cur_left_point = next_point(True)
                get_vdedges(cur_left_point).append(cur_edge)
                cur_edge = VDEdge(cur_left_point, cur_right_point, intersec_l)
            elif r_dist < l_dist:
                cur_edge.set_second_point(intersec_r)
                cur_right_point = next_point(False)
                get_vdedges(cur_right_point).append(cur_edge)
                cur_edge = VDEdge(cur_left_point, cur_right_point, intersec_r)
            else:
                assert False, "work with l_dist = r_dist"
        # TODO: clear extra edges
        get_vdedges(cur_left_point).append(cur_edge)
        get_vdedges(cur_right_point).append(cur_edge)

    def _draw_vor(self, vis: VisualizerConvexHull):
        seen = set()
        for list_of_edges in main_dot_to_edge.values():
            for edge in list_of_edges:
                if edge not in seen:
                    seen.add(edge)
                    vis.canv.create_line(edge.first_point.x, edge.first_point.y, edge.second_point.x, edge.second_point.y)
        vis.canv.pack()


if __name__ == '__main__':
    alg = VoronoiDiagram()
    v = VisualizerConvexHull(init_func=alg.init_points_function,
                             action_func=alg.action_decor)

