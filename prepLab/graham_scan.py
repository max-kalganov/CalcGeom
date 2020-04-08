from typing import Tuple, Optional, Iterable, Callable

import numpy as np
from sortedcontainers import SortedList
from geompreds import orient2d

from ct import CANVAS_WIDTH, CANVAS_HEIGHT, DEFAULT_NUM_OF_POINTS
from utils import dist, dist_between_points
from visualizer import SimpleVisualizer


class GrahamScan:
    def __init__(self):
        self.all_points: Optional[SortedList] = None
        self.conv = []
        self.start_point: Optional[Tuple[int, int]] = None
        self.cur_index: Optional[int] = None

    def full_init(self, vis: SimpleVisualizer):
        self.__init__()
        self.init_field(vis)

    def _tan(self, point: Tuple[float, float]) -> Tuple[float, float]:
        if point == self.start_point:
            return 0, 0
        if point[0] == self.start_point[0] and point[1] != self.start_point[1]:
            return (1 if point[1] > self.start_point[1] else -1) * np.inf, point[1]
        return (point[1] - self.start_point[1]) / (point[0] - self.start_point[0]), dist_between_points(self.start_point, point)

    def init_field(self, vis: SimpleVisualizer):
        seen = {}
        x_values = np.random.normal(loc=CANVAS_WIDTH // 2, scale=CANVAS_WIDTH // 8, size=DEFAULT_NUM_OF_POINTS)
        y_values = np.random.normal(loc=CANVAS_HEIGHT // 2, scale=CANVAS_HEIGHT // 8, size=DEFAULT_NUM_OF_POINTS)
        x_values = x_values[(x_values >= 0) & (x_values <= CANVAS_WIDTH)]
        y_values = y_values[(y_values >= 0) & (y_values <= CANVAS_HEIGHT)]
        min_len = min(len(x_values), len(y_values))
        x_values = x_values[:min_len]
        y_values = y_values[:min_len]

        min_x_ind = np.argmin(x_values)
        self.start_point = x_values[min_x_ind], y_values[min_x_ind]
        self.all_points = SortedList(zip(x_values[x_values != self.start_point[0]],
                                         y_values[y_values != self.start_point[1]]),
                                     key=self._tan)

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
        self.gen_conv()
        self.draw_conv(vis)

    def draw_conv(self, vis: SimpleVisualizer):
        def divided_coords() -> Iterable[int]:
            for point in self.conv:
                yield point[0]
                yield point[1]

        vis.canv.create_line(*divided_coords())

    def gen_conv(self):
        def get_next():
            assert self.cur_index <= len(self.all_points)
            if self.cur_index == len(self.all_points):
                el = self.start_point
            else:
                el = self.all_points[self.cur_index]
            self.cur_index += 1
            return el

        def is_r_turn(p1: Tuple[float, float], p2: Tuple[float, float], p3: Tuple[float, float]) -> bool:
            return orient2d(p1, p2, p3) <= 0

        self.cur_index = 0
        self.conv.append(self.start_point)
        v = get_next()
        w = get_next()
        while w != self.start_point:
            if is_r_turn(self.conv[-1], v, w):
                v = self.conv.pop()
            else:
                self.conv.append(v)
                v = w
                w = get_next()
        self.conv.append(v)
        self.conv.append(self.start_point)

if __name__ == '__main__':
    alg = GrahamScan()
    v = SimpleVisualizer(init_func=alg.full_init,
                         action_func=alg.action)
    v.run_loop()
