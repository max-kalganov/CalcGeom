import random
from Models import Dot
from ct import CANVAS_WIDTH, CANVAS_HEIGHT, DEFAULT_NUM_OF_POINTS_SMALL
from visualizer import VisualizerConvexHull
import numpy as np


class VoronoiDiagram:
    def __init__(self):
        self.windows_width = 10

    def init_points_function(self, obj: VisualizerConvexHull, number_of_points=DEFAULT_NUM_OF_POINTS_SMALL):
        self.all_points = []
        seen = {}
        x_values = np.random.normal(loc=CANVAS_WIDTH//2, scale=CANVAS_WIDTH//8, size=number_of_points)
        y_values = np.random.normal(loc=CANVAS_HEIGHT//2, scale=CANVAS_HEIGHT//8, size=number_of_points)

        for x, y in zip(x_values, y_values):
            if x in seen:
                if y not in seen[x]:
                    seen[x].add(y)
                else:
                    continue
            else:
                seen.setdefault(x, {y})

            point = obj.canv.create_rectangle((x, y) * 2)
            self.all_points.append(point)

    def action_decor(self, vis: VisualizerConvexHull):
        def action(event):
            pass

        return action


if __name__ == '__main__':
    alg = VoronoiDiagram()
    v = VisualizerConvexHull(init_func=alg.init_points_function,
                             action_func=alg.action_decor)

