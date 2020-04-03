import random
from time import sleep

import numpy as np
from ct import CANVAS_WIDTH, CANVAS_HEIGHT, DEFAULT_NUM_OF_POINTS
from visualizer import Visualizer, SimpleVisualizer


class IsometricProjection:
    def __init__(self):
        self.polygon = None

    def init_points_function(self, obj: Visualizer):
        x_len, y_len, z_len = (np.random.random(3)*150 + 100).astype(int) * 2
        self.polygon = self._gen_polygon(x_len, y_len, z_len)
        self.draw_polygon(self.make_projection())

    @staticmethod
    def _gen_polygon(x_len: int, y_len: int , z_len: int) -> np.array:
        def gen_2d_pol():
            pol = np.array([-x_len / 2, -y_len / 2, 0])
            pos_add = np.array([[0, y_len, 0], [x_len, 0, 0]])
            for i in [1, -1]:
                for add in pos_add:
                    pol = np.stack([pol, pol[-1]*i*add])
            return pol
        bottom_polygon = gen_2d_pol()
        top_polygon = np.array([0, 0, z_len]) + bottom_polygon
        res_polygon = np.stack([bottom_polygon, top_polygon])
        return res_polygon

    def turn_polygon(self):
        pass

    def draw_polygon(self, polygon_2d: np.array, vis: SimpleVisualizer):
        pass

    def make_projection(self) -> np.array:
        pass

    def action_decor(self, vis: SimpleVisualizer):
        def action():
            for i in range(1000):
                self.turn_polygon()
                self.draw_polygon(self.make_projection(), vis)
                sleep(0.1)
        return action


if __name__ == '__main__':
    alg = OutputRayMethod()
    v = Visualizer(init_func=alg.init_points_function,
                   action_func=alg.action_decor)

