import random
from math import ceil, floor
from Models import Dot
from ct import CANVAS_WIDTH, CANVAS_HEIGHT
from visualizer import Visualizer


class GridMethod:
    def __init__(self):
        self.number_of_points =200000
        self.windows_width = 10
        self.windows = [[[] for j in range(CANVAS_WIDTH//self.windows_width + 1)] for i in range(CANVAS_HEIGHT//self.windows_width + 1)]
        self.colored_points = []

    def init_points_function(self, obj: Visualizer):
        seen = {}
        for i in range(self.number_of_points):
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
            self.windows[y//self.windows_width][x//self.windows_width].append(point)

    def decorate_all_points(self, vis, old_points, points):
        for point in points:
            if point in old_points:
                old_points.remove(point)
            else:
                vis.canv.itemconfig(point, outline="#ff0000")
            self.colored_points.append(point)

    def check_and_decorate_points(self, vis, old_points, second_type_windows, min_x, max_x, min_y, max_y):
        for point in second_type_windows:
            coords = vis.canv.coords(point)
            if min_x <= coords[0] <= max_x and min_y <= coords[1] <= max_y:
                if point in old_points:
                    old_points.remove(point)
                else:
                    vis.canv.itemconfig(point, outline="#ff0000")
                self.colored_points.append(point)

    def check_first_and_last_window(self, vis, old_points, line, min_x, max_x, min_y, max_y):
        if ceil(min_x / self.windows_width) != min_x / self.windows_width:
            self.check_and_decorate_points(vis, old_points, line[floor(min_x / self.windows_width)],
                                           min_x, max_x, min_y, max_y)

        if floor(max_x / self.windows_width) != max_x / self.windows_width:
            self.check_and_decorate_points(vis, old_points, line[floor(max_x / self.windows_width)],
                                           min_x, max_x, min_y, max_y)

    def check_first_or_last_line(self, line_num, vis, old_points, min_x, max_x, min_y, max_y):
        border_windows = self.windows[line_num]
        for sec_type_window in border_windows[
                               ceil(min_x / self.windows_width):floor(max_x / self.windows_width)]:
            self.check_and_decorate_points(vis, old_points, sec_type_window,
                                           min_x, max_x, min_y, max_y)

        self.check_first_and_last_window(vis, old_points, border_windows, min_x, max_x, min_y, max_y)

    def action_decor(self, vis: Visualizer):
        def action(event):
            # probably you should improve this coloring
            old_points = set(self.colored_points)
            self.colored_points = []

            for line in self.windows[ceil(min_y / self.windows_width):floor(max_y / self.windows_width)]:
                for first_type_window in line[ceil(min_x / self.windows_width):floor(max_x / self.windows_width)]:
                    self.decorate_all_points(vis, old_points, first_type_window)

                self.check_first_and_last_window(vis, old_points, line, min_x, max_x, min_y, max_y)

            if ceil(min_y / self.windows_width) != min_y / self.windows_width:
                self.check_first_or_last_line(floor(min_y / self.windows_width),
                                              vis, old_points, min_x, max_x, min_y, max_y)

            if floor(max_y / self.windows_width) != max_y / self.windows_width:
                self.check_first_or_last_line(floor(max_y / self.windows_width),
                                              vis, old_points, min_x, max_x, min_y, max_y)

            for point in old_points:
                vis.canv.itemconfig(point, outline="#000000")

        x1, x2 = (vis.polygon_dots[0].x, vis.polygon_dots[1].x)
        y1, y2 = (vis.polygon_dots[0].y, vis.polygon_dots[1].y)
        min_x, max_x = (x1, x2) if x1 < x2 else (x2, x1)
        min_y, max_y = (y1, y2) if y1 < y2 else (y2, y1)

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

