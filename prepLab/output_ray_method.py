import random
from math import ceil, floor
from typing import Tuple
import numpy as np
from geompreds import orient2d

from Models import Dot
from ct import CANVAS_WIDTH, CANVAS_HEIGHT, DEFAULT_NUM_OF_POINTS
from visualizer import Visualizer


class OutputRayMethod:
    def __init__(self):
        self.colored_points = []

    def init_points_function(self, obj: Visualizer, number_of_points=DEFAULT_NUM_OF_POINTS):
        self.all_points = []
        seen = {}
        for i in range(number_of_points):
            x = random.randint(0, CANVAS_WIDTH)
            y = random.randint(0, CANVAS_HEIGHT)
            if x in seen:
                if y not in seen[x]:
                    seen[x].add(y)
                else:
                    continue
            else:
                seen.setdefault(x, {y})

            point = obj.canv.create_rectangle((x, y) * 2)
            self.all_points.append(point)

    @staticmethod
    def get_min_max_coords(prev_node_pos: Dot, node_pos: Dot) -> Tuple[int, int, int, int]:
        x1, x2 = (prev_node_pos.x, node_pos.x)
        y1, y2 = (prev_node_pos.y, node_pos.y)
        min_x, max_x = (x1, x2) if x1 < x2 else (x2, x1)
        min_y, max_y = (y1, y2) if y1 < y2 else (y2, y1)
        return min_x, max_x, min_y, max_y

    def is_in_polygon(self, vis: Visualizer, point) -> bool:
        def is_on_left_if_equal(node_that_equal: Dot, node_idx) -> bool:
            prev_point_y = vis.polygon_dots[node_idx-1].y
            next_point_y = vis.polygon_dots[(node_idx+1) % len(vis.polygon_dots)].y
            return np.sign(prev_point_y - node_that_equal.y) * np.sign(next_point_y - node_that_equal.y) < 0

        def is_on_left_by_func(point_x, point_y, prev_node: Dot, cur_node: Dot, cur_node_idx: int) -> bool:
            if prev_node.x != cur_node.x:
                k = (prev_node.y - cur_node.y) / (prev_node.x - cur_node.x)
                b = cur_node.y - k * cur_node.x
                func_res = k * point_x + b
                is_fit_func = (k > 0 and point_y >= func_res) or (k < 0 and point_y <= func_res)
            else:
                is_fit_func = True

            return (is_fit_func and point_y != prev_node.y)\
                   and (point_y != cur_node.y
                        or is_on_left_if_equal(cur_node, cur_node_idx))

        def is_on_left_if_equal_shewchuk(target_point_x: int, target_point_y:int, node_that_equal: Dot, node_idx)\
                -> bool:
            prev_point = vis.polygon_dots[node_idx-1]
            next_point = vis.polygon_dots[(node_idx+1) % len(vis.polygon_dots)]

            return np.sign(orient2d((target_point_x, target_point_y),
                                    node_that_equal.get_tuple(),
                                    prev_point.get_tuple())) \
                 * np.sign(orient2d((target_point_x, target_point_y),
                                    node_that_equal.get_tuple(),
                                    next_point.get_tuple())) < 0

        def is_on_left_by_func_shewchuk(point_x: int, point_y: int, prev_node: Dot, cur_node: Dot, cur_node_idx: int) -> bool:
            if prev_node.x != cur_node.x:
                if prev_node.y < cur_node.y:
                    is_fit_func = orient2d(prev_node.get_tuple(), cur_node.get_tuple(), (point_x, point_y)) >= 0
                else:
                    is_fit_func = orient2d(cur_node.get_tuple(), prev_node.get_tuple(), (point_x, point_y)) >= 0
            else:
                is_fit_func = True

            return (is_fit_func and point_y != prev_node.y)\
                   and (point_y != cur_node.y
                        or is_on_left_if_equal_shewchuk(point_x, point_y, cur_node, cur_node_idx))

        def is_point_on_left(point_x: int, point_y: int, prev_node: Dot, cur_node: Dot, cur_node_idx: int):
            x_min, x_max, y_min, y_max = self.get_min_max_coords(prev_node, cur_node)

            return point_x <= x_max \
                   and y_min <= point_y <= y_max \
                   and is_on_left_by_func_shewchuk(point_x, point_y, prev_node, cur_node, cur_node_idx)

        point_x, point_y = vis.canv.coords(point)[:2]
        prev_node_pos = vis.polygon_dots[0]
        crossed_edges = 0
        for node_idx, node_pos in enumerate(vis.polygon_dots[1:]):
            if is_point_on_left(point_x, point_y, prev_node_pos, node_pos, node_idx+1):
                crossed_edges += 1

            prev_node_pos = node_pos
        node_pos = vis.polygon_dots[0]
        if is_point_on_left(point_x, point_y, prev_node_pos, node_pos, 0):
            crossed_edges += 1

        return crossed_edges % 2 != 0

    def decorate_point(self, vis, old_points, point):
        if point in old_points:
            old_points.remove(point)
        else:
            vis.canv.itemconfig(point, outline="#ff0000")
        self.colored_points.append(point)

    def action_decor(self, vis: Visualizer):
        def action(event):
            # probably you should improve this coloring
            old_points = set(self.colored_points)
            self.colored_points = []

            for point in self.all_points:
                if self.is_in_polygon(vis, point):
                    self.decorate_point(vis, old_points, point)

            for point in old_points:
                vis.canv.itemconfig(point, outline="#000000")

        return action


if __name__ == '__main__':
    alg = OutputRayMethod()
    v = Visualizer(init_func=alg.init_points_function,
                   action_func=alg.action_decor)

