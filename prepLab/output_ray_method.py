import random
from math import ceil, floor
from Models import Dot
from ct import CANVAS_WIDTH, CANVAS_HEIGHT, DEFAULT_NUM_OF_POINTS
from visualizer import Visualizer


class OutputRayMethod:
    def __init__(self):
        self.colored_points = []
        self.all_points = []

    def init_points_function(self, obj: Visualizer, number_of_points=DEFAULT_NUM_OF_POINTS):
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

    def action_decor(self, vis: Visualizer):
        def action(event):
            # probably you should improve this coloring
            old_points = set(self.colored_points)
            self.colored_points = []

        return action


if __name__ == '__main__':
    alg = OutputRayMethod()
    v = Visualizer(init_func=alg.init_points_function,
                   action_func=alg.action_decor)

