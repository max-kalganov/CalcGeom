import numpy as np

from time import sleep
from visualizer import SimpleVisualizer
from ct import CANVAS_WIDTH, CANVAS_HEIGHT, DEFAULT_NUM_OF_POINTS, TURNING_PERIOD, SLEEP_PERIOD, TURN_ANGLE


class IsometricProjection:
    def __init__(self):
        self.polygon = None
        self.pairs = self._get_pairs()
        self.turn_mtrx = self._get_turn_mtrx()
        self.proj_mtrx = self._get_proj_mtrx()

    def init_polygon_function(self, obj: SimpleVisualizer):
        x_len, y_len, z_len = (np.random.random(3) * 50 + 100).astype(int) * 2
        self.polygon = self._gen_polygon(x_len, y_len, z_len)
        self.draw_polygon(self.make_projection(), obj)

    @staticmethod
    def _gen_polygon(x_len: int, y_len: int, z_len: int) -> np.array:
        def gen_2d_pol():
            pol = np.array([[-x_len / 2, -y_len / 2, 0]])
            pos_add = np.array([[0, y_len, 0], [x_len, 0, 0]])
            for i in [1, -1]:
                for add in pos_add:
                    if len(pol) == 4:
                        return pol
                    pol = np.vstack([pol, pol[-1] + i * add])
            return pol

        bottom_polygon = gen_2d_pol()
        top_polygon = np.array([0, 0, z_len]) + bottom_polygon
        res_polygon = np.vstack([bottom_polygon, top_polygon])

        return res_polygon

    @staticmethod
    def _get_pairs():
        pairs = []
        for i in range(7):
            pairs.append((i, i + 1))
            if i < 4:
                pairs.append((i, i + 4))
        del pairs[6]
        pairs.append((0, 3))
        pairs.append((4, 7))
        return pairs

    def turn_polygon(self):
        self.polygon = (self.turn_mtrx @ self.polygon.T).T

    def draw_polygon(self, polygon_2d: np.array, vis: SimpleVisualizer):
        vis.canv.delete("all")
        for i1, i2 in self.pairs:
            vis.canv.create_line(polygon_2d[i1, 0], polygon_2d[i1, 1],
                                 polygon_2d[i2, 0], polygon_2d[i2, 1])
        vis.canv.pack()
        vis.canv.update()

    def make_projection(self) -> np.array:

        projection = (self.proj_mtrx @ self.polygon.T).T
        projection = projection[:, :2] + np.array([CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2])
        return projection

    def action_decor(self, vis: SimpleVisualizer):
        for i in range(TURNING_PERIOD):
            self.turn_polygon()
            self.draw_polygon(self.make_projection(), vis)
            sleep(SLEEP_PERIOD)
        print("finish")

    @staticmethod
    def _get_turn_mtrx() -> np.array:
        return np.array([
            [np.cos(TURN_ANGLE), np.sin(TURN_ANGLE), 0],
            [- np.sin(TURN_ANGLE), np.cos(TURN_ANGLE), 0],
            [0, 0, 1]
        ])

    @staticmethod
    def _get_proj_mtrx() -> np.array:
        turn_x = -(np.pi / 2 - np.arctan(1 / np.sqrt(2)))
        turn_z = -np.pi / 4
        x_turn = np.array([
            [1, 0, 0],
            [0, np.cos(turn_x), np.sin(turn_x)],
            [0, - np.sin(turn_x), np.cos(turn_x)]
        ])
        z_turn = np.array([
            [np.cos(turn_z), np.sin(turn_z), 0],
            [- np.sin(turn_z), np.cos(turn_z), 0],
            [0, 0, 1]
        ])

        return x_turn @ z_turn


if __name__ == '__main__':
    alg = IsometricProjection()
    v = SimpleVisualizer(init_func=alg.init_polygon_function,
                         action_func=alg.action_decor)
    v.run_loop()
