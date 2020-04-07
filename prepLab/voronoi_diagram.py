import numpy as np

from scipy.spatial import ConvexHull
from typing import List, Tuple, Optional

from visualizer import VisualizerConvexHull
from Models import VDEdge, Dot, intersection, FloatDot
from ct import CANVAS_WIDTH, CANVAS_HEIGHT, DEFAULT_NUM_OF_POINTS_CONVEXHULL
from utils import get_border_points, get_vdedges, dist, main_dot_to_edge, clear


class VoronoiDiagram:
    def __init__(self):
        self.all_points: List[Dot] = []

    def init_points_function(self, obj: VisualizerConvexHull, number_of_points=DEFAULT_NUM_OF_POINTS_CONVEXHULL):
        self.all_points: List[Dot] = []
        seen = {}
        x_values = np.random.normal(loc=CANVAS_WIDTH // 2, scale=CANVAS_WIDTH // 8, size=number_of_points)
        y_values = np.random.normal(loc=CANVAS_HEIGHT // 2, scale=CANVAS_HEIGHT // 8, size=number_of_points)

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
            self.all_points.append(Dot(x, y))

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
        merged_conv, start_left_ind, start_right_ind, \
        finish_left_ind, finish_right_ind = self._merge_conv(conv_s1, conv_s2)
        self._merge_vor(conv_s1, conv_s2,
                        start_left_ind, start_right_ind,
                        finish_left_ind, finish_right_ind)
        return merged_conv

    def _get_vor(self, points: List[Dot]):
        if len(points) == 2:
            new_vdedge = VDEdge(points[0], points[1])
            get_vdedges(points[0]).append(new_vdedge)
            get_vdedges(points[1]).append(new_vdedge)

    @staticmethod
    def _divide_points(points: List[Dot]) -> Tuple[List[Dot], List[Dot]]:
        return points[:(len(points) // 2)], points[(len(points) // 2):]

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
        indices = [start_left_ind, start_right_ind]

        def next_point(left: bool) -> Dot:
            if left:
                next_p = conv_s1[indices[0]]
                indices[0] = (indices[0] + 1) % len(conv_s1)
            else:
                next_p = conv_s2[indices[1]]
                indices[1] = (indices[1] - 1) % len(conv_s2)
            return next_p

        def find_edge(cur_point: Dot, cur_edge: VDEdge, cur_search_edge: VDEdge, next: bool) \
                -> Tuple[Optional[FloatDot], Optional[VDEdge]]:
            vdedges = get_vdedges(cur_point)

            min_y, edge_min_y = FloatDot(float('inf'), float('inf')), None
            for edge in vdedges:
                if next and edge != cur_search_edge:
                    continue
                intersec = intersection(cur_edge, edge)
                if intersec is not None and intersec.y < min_y.y:
                    min_y = intersec
                    edge_min_y = edge

            return (None, None) if edge_min_y is None else (min_y, edge_min_y)

        cur_left_point = next_point(left=True)
        cur_right_point = next_point(left=False)

        cur_edge = VDEdge(cur_left_point, cur_right_point)
        e_l, e_r, next_l, next_r = None, None, False, False
        while cur_left_point != conv_s1[finish_left_ind] or cur_right_point != conv_s2[finish_right_ind]:
            intersec_l, e_l = find_edge(cur_left_point, cur_edge, e_l, next_l)
            intersec_r, e_r = find_edge(cur_right_point, cur_edge, e_r, next_r)
            next_l, next_r = False, False

            l_dist = None if intersec_l is None else dist(intersec_l, cur_edge.first_point)
            r_dist = None if intersec_r is None else dist(intersec_r, cur_edge.first_point)
            assert not (l_dist is None and r_dist is None), f"two None"
            if r_dist is None or (l_dist is not None and l_dist < r_dist):
                self._proc_left_intersect(cur_left_point, cur_edge, e_l, intersec_l)
                next_l = True

                cur_left_point = next_point(left=True)
                cur_edge = VDEdge(cur_left_point, cur_right_point, intersec_l)
                cur_edge.make_first_point_border()
            elif l_dist is None or (r_dist is not None and r_dist < l_dist):
                self._proc_right_intersect(cur_right_point, cur_edge, e_r, intersec_r)
                next_r = True

                cur_right_point = next_point(left=False)
                cur_edge = VDEdge(cur_left_point, cur_right_point, intersec_r)
                cur_edge.make_first_point_border()
            else:
                self._proc_left_intersect(cur_left_point, cur_edge, e_l, intersec_l)
                self._proc_right_intersect(cur_right_point, cur_edge, e_r, intersec_r)
                next_l, next_r = True, True

                cur_left_point = next_point(left=True)
                cur_right_point = next_point(left=False)

                cur_edge = VDEdge(cur_left_point, cur_right_point, intersec_l)
                cur_edge.make_first_point_border()

        cur_edge.return_first_point_from_temp()
        get_vdedges(cur_left_point).append(cur_edge)
        get_vdedges(cur_right_point).append(cur_edge)

    def _proc_left_intersect(self, cur_left_point: Dot, cur_edge: VDEdge, e_l: VDEdge, intersec_l: FloatDot):
        get_vdedges(cur_left_point).append(cur_edge)

        if e_l.between_point.y > intersec_l.y:
            e_l.first_point = intersec_l
        else:
            e_l.second_point = intersec_l

        # if e_l.first_point.x > e_l.second_point.x\
        #     or (e_l.first_point.x == e_l.second_point.x and intersec_l.y <= e_l.between_point.y):
        #     e_l.first_point = intersec_l
        # else:
        #     e_l.second_point = intersec_l

        cur_edge.return_first_point_from_temp()
        cur_edge.set_second_point(intersec_l)

    def _proc_right_intersect(self, cur_right_point: Dot, cur_edge: VDEdge, e_r: VDEdge, intersec_r: FloatDot):
        get_vdedges(cur_right_point).append(cur_edge)

        if e_r.between_point.y >= intersec_r.y:
            e_r.first_point = intersec_r
        else:
            e_r.second_point = intersec_r

        # if e_r.first_point.x < e_r.second_point.x \
        #         or (e_r.first_point.x == e_r.second_point.x and intersec_r.y <= e_r.between_point.y):
        #     e_r.first_point = intersec_r
        # else:
        #     e_r.second_point = intersec_r

        cur_edge.return_first_point_from_temp()
        cur_edge.set_second_point(intersec_r)

    def _draw_vor(self, vis: VisualizerConvexHull):
        seen = set()
        for list_of_edges in main_dot_to_edge.values():
            for edge in list_of_edges:
                if edge not in seen:
                    f_point, s_point = self.proc_borders(edge)
                    seen.add(edge)
                    if f_point is not None and s_point is not None:
                        vis.canv.create_line(f_point.x, f_point.y, s_point.x,
                                             s_point.y)
        vis.canv.pack()
        main_dot_to_edge.clear()

    @staticmethod
    def proc_borders(edge: VDEdge) -> Tuple[FloatDot, FloatDot]:
        def _proc_f_point() -> FloatDot:
            if edge.slope is None:
                first_point = FloatDot(edge.between_point.x, 0)
            elif edge.slope == 0:
                first_point = FloatDot(0, edge.between_point.y)
            else:
                if edge.slope > 0:
                    x = -edge.b / edge.slope
                    if 0 <= x <= CANVAS_WIDTH:
                        first_point = FloatDot(x, 0)
                    else:
                        first_point = FloatDot(0, edge.b)
                else:
                    x = -edge.b / edge.slope
                    if 0 <= x <= CANVAS_WIDTH:
                        first_point = FloatDot(x, 0)
                    else:
                        first_point = FloatDot(CANVAS_WIDTH, edge.slope * CANVAS_WIDTH + edge.b)
            return first_point

        def _proc_s_point() -> FloatDot:
            if edge.slope is None:
                second_point = FloatDot(edge.between_point.x, CANVAS_HEIGHT)
            elif edge.slope == 0:
                second_point = FloatDot(CANVAS_WIDTH, edge.between_point.y)
            else:
                if edge.slope > 0:
                    y = edge.slope * CANVAS_WIDTH + edge.b
                    if 0 <= y <= CANVAS_HEIGHT:
                        second_point = FloatDot(CANVAS_WIDTH, y)
                    else:
                        second_point = FloatDot((CANVAS_HEIGHT - edge.b) / edge.slope, CANVAS_HEIGHT)
                else:
                    if 0 <= edge.b <= CANVAS_HEIGHT:
                        second_point = FloatDot(0, edge.b)
                    else:
                        second_point = FloatDot((CANVAS_HEIGHT - edge.b) / edge.slope, CANVAS_HEIGHT)
            return second_point

        # TODO: check, if edge not in window
        # if VDEdge.in_map(edge.first_point) or VDEdge.in_map(edge.second_point):
        #     f_point = edge.first_point if VDEdge.in_map(edge.first_point) else _proc_f_point()
        #     s_point = edge.second_point if VDEdge.in_map(edge.second_point) else _proc_s_point()
        # else:
        #     f_point = None
        #     s_point = None

        f_point = edge.first_point if VDEdge.in_map(edge.first_point) else _proc_f_point()
        s_point = edge.second_point if VDEdge.in_map(edge.second_point) else _proc_s_point()

        return f_point, s_point


if __name__ == '__main__':
    alg = VoronoiDiagram()
    v = VisualizerConvexHull(init_func=alg.init_points_function,
                             action_func=alg.action_decor)
