import random

from Models import Dot
from ct import CANVAS_WIDTH, CANVAS_HEIGHT
from visualizer import Visualizer


class GridMethod:
    def __init__(self):
        self.number_of_points =250000
        self.windows_width = 50
        self.windows = [[[] for j in range(CANVAS_WIDTH//self.windows_width + 1)] for i in range(CANVAS_HEIGHT//self.windows_width + 1)]
        self.colored_points = []

    def init_points_function(self, obj: Visualizer):
        for i in range(self.number_of_points):
            x = random.randint(0, CANVAS_WIDTH)
            y = random.randint(0, CANVAS_HEIGHT)
            point = obj.canv.create_rectangle((x, y) * 2)
            self.windows[y//self.windows_width][x//self.windows_width].append(point)

    def action_decor(self, vis: Visualizer):
        def action(event):
            # probably you should improve this coloring
            for point in self.colored_points:
                vis.canv.itemconfig(point, outline="#000000")
            self.colored_points = []

            for lines in self.windows[min_y//self.windows_width+1:max_y//self.windows_width]:
                for points_in_window in lines[min_x//self.windows_width+1:max_x//self.windows_width]:
                    for point in points_in_window:
                        vis.canv.itemconfig(point, outline="#ff0000")
                        self.colored_points.append(point)
                for points_in_window in [lines[min_x//self.windows_width], lines[max_x//self.windows_width]]:
                    for point in points_in_window:
                        coords = vis.canv.coords(point)
                        if min_x <= coords[0] <= max_x and min_y <= coords[1] <= max_y:
                            vis.canv.itemconfig(point, outline="#ff0000")
                            self.colored_points.append(point)

            for border_lines in [self.windows[min_y//self.windows_width], self.windows[max_y//self.windows_width]]:
                for points_in_window in border_lines[min_x//self.windows_width+1:max_x//self.windows_width]:
                    for point in points_in_window:
                        coords = vis.canv.coords(point)
                        if min_x <= coords[0] <= max_x and min_y <= coords[1] <= max_y:
                            vis.canv.itemconfig(point, outline="#ff0000")
                            self.colored_points.append(point)

        min_x, max_x = (vis.polygon_dots[0].x, vis.polygon_dots[1].x)
        min_y, max_y = (vis.polygon_dots[0].y, vis.polygon_dots[1].y)
        if vis.polygon_dots[0].x > vis.polygon_dots[1].x:
            min_x, max_x = max_x, min_x
        if vis.polygon_dots[0].y > vis.polygon_dots[1].y:
            min_y, max_y = max_y, min_y

        return action

    @staticmethod
    def capture_points_decor(vis: Visualizer):
        def capture_points(event):
            vis.temp_points.append(vis.canv.create_rectangle((event.x, event.y) * 2, outline="#ff0000"))
            vis.polygon_dots.append(Dot(x=event.x, y=event.y))
            if len(vis.polygon_dots) == 2:
                vis.stop_capturing(event)

        def draw_polygon():
            vis.polygon = vis.canv.create_rectangle(list(vis.unroll_dots(vis.polygon_dots)),
                                                      outline='gray',
                                                      fill='',
                                                      width=2)
            vis.canv.pack()

        vis.draw_polygon = draw_polygon
        return capture_points


if __name__ == '__main__':
    alg = GridMethod()
    v = Visualizer(init_func=alg.init_points_function,
                   action_func=alg.action_decor,
                   capture_points_func=alg.capture_points_decor)

