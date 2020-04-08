from typing import Tuple

import numpy as np
from sortedcontainers import SortedList

from Models import Dot
from ct import CANVAS_WIDTH, CANVAS_HEIGHT, DEFAULT_NUM_OF_POINTS
from utils import dist, dist_between_points
from visualizer import SimpleVisualizer


class GrahamScan:
    def __init__(self):
        self.all_points = None

    def init_field(self, vis: SimpleVisualizer):
        def tan(point1: Tuple[int, int], point2: Tuple[int, int]) -> Tuple[float, float]:
            if point2[0] == point1[0] and point2[1] != point1[1]:
                return (1 if point2[1] > point1[1] else -1)*np.inf, point2[1]
            return (point2[1] - point1[1])/(point2[0] - point1[0]), dist_between_points(point1, point2)
        seen = {}
        x_values = np.random.normal(loc=CANVAS_WIDTH // 2, scale=CANVAS_WIDTH // 8, size=DEFAULT_NUM_OF_POINTS)
        y_values = np.random.normal(loc=CANVAS_HEIGHT // 2, scale=CANVAS_HEIGHT // 8, size=DEFAULT_NUM_OF_POINTS)

        min_x_ind = np.argmin(x_values)
        self.all_points = SortedList(zip(x_values, y_values),
                                     key=lambda point: tan((x_values[min_x_ind], y_values[min_x_ind]),
                                                           point))

        for x, y in zip(x_values, y_values):
            if x in seen:
                if y not in seen[x]:
                    seen[x].add(y)
                else:
                    continue
            else:
                seen.setdefault(x, {y})
            vis.canv.create_rectangle((x, y) * 2)

    def action(self, vis: SimpleVisualizer):
        pass


if __name__ == '__main__':
    alg = GrahamScan()
    v = SimpleVisualizer(init_func=alg.init_field,
                         action_func=alg.action)
    v.run_loop()
