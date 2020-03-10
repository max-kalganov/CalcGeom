import random
from math import ceil, floor
from typing import Tuple

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
        def is_on_left_by_func(point_x, point_y, prev_node: Dot, cur_node: Dot) -> bool:
            k = (prev_node.y - cur_node.y) / (prev_node.x - cur_node.x)
            b = cur_node.y - k * cur_node.x
            func_res = k * point_x + b
            return (k > 0 and point_y > func_res) or (k < 0 and point_y < func_res)

        def is_point_on_left(point_x: int, point_y: int, prev_node: Dot, cur_node: Dot):
            x_min, x_max, y_min, y_max = self.get_min_max_coords(prev_node, cur_node)
            return point_x <= x_max \
                   and y_min <= point_y <= y_max \
                   and is_on_left_by_func(point_x, point_y, prev_node, cur_node)

        point_x, point_y = vis.canv.coords(point)[:2]
        prev_node_pos = vis.polygon_dots[0]
        crossed_edges = 0
        for node_pos in vis.polygon_dots[1:]:
            if is_point_on_left(point_x, point_y, prev_node_pos, node_pos):
                crossed_edges += 1

            prev_node_pos = node_pos
        node_pos = vis.polygon_dots[0]
        if is_point_on_left(point_x, point_y, prev_node_pos, node_pos):
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

