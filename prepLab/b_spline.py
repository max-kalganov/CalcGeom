from typing import Optional

import numpy as np

from visualizer import VisualizerSpline


class BSpline:
    def __init__(self):
        self.main_points = None

    def draw_spline(self, vis: VisualizerSpline, new_point: np.array, index: Optional[int] = None):
        pass


if __name__ == '__main__':
    alg = BSpline()
    vis = VisualizerSpline(alg)
    vis.run_loop()
