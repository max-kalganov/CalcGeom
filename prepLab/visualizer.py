import random
from tkinter import *
from typing import Callable, Optional, List, Iterable

from Models import Dot
from ct import CANVAS_WIDTH, CANVAS_HEIGHT, BUTTON1, BUTTON1_MOVE, STOP_KEY


class Visualizer:
    polygon_dots: List[Dot] = []
    temp_points = []
    polygon = None

    def __init__(self,
                 init_func: Callable,
                 action_func: Callable,
                 capture_points_func: Optional[Callable] = None,
                 width=CANVAS_WIDTH,
                 height=CANVAS_HEIGHT):
        master = Tk()
        master.title("Calc. Geom.")
        self.canv = Canvas(master,
                           width=width,
                           height=height)
        self.action_func = action_func
        self.canv.pack(expand=YES, fill=BOTH)
        init_func(self)
        self.__set_polygon(capture_points=capture_points_func)
        self.canv.focus_set()
        master.mainloop()

    def __move_polygon(self, new_first_dot: Dot):
        x_change = self.polygon_dots[0].x - new_first_dot.x
        y_change = self.polygon_dots[0].y - new_first_dot.y
        for dot in self.polygon_dots:
            dot.x -= x_change
            dot.y -= y_change

    def __bind_move_polygon_and_action(self):
        def bind_mouse(event):
            self.canv.delete(self.polygon)
            self.__move_polygon(Dot(event.x, event.y))
            self.draw_polygon()
            self.action_func(self)(event)
        self.canv.bind(BUTTON1, bind_mouse)

    def __default_capture_points(self, event):
        self.temp_points.append(self.canv.create_rectangle((event.x, event.y) * 2, outline="#ff0000"))
        self.polygon_dots.append(Dot(x=event.x, y=event.y))

    def stop_capturing(self, event):
        self.canv.unbind(BUTTON1)
        self.canv.unbind(STOP_KEY)
        self.draw_polygon()
        self.__remove_polygon_points()
        self.__bind_move_polygon_and_action()

    def __remove_polygon_points(self):
        for point in self.temp_points:
            self.canv.delete(point)

    def __set_polygon(self, capture_points: Optional[Callable] = None):
        points_proc = capture_points(self) if capture_points is not None else self.__default_capture_points
        self.canv.bind(BUTTON1, points_proc)
        self.canv.bind(STOP_KEY, self.stop_capturing)
        self.canv.pack()

    def draw_polygon(self):
        self.polygon = self.canv.create_polygon(list(self.unroll_dots(self.polygon_dots)),
                                                outline='gray',
                                                fill='',
                                                width=2)
        self.canv.pack()

    @staticmethod
    def unroll_dots(list_of_dots: List[Dot]) -> Iterable[int]:
        for dot in list_of_dots:
            yield dot.x
            yield dot.y


if __name__ == '__main__':
    all_points = []

    def init_function(obj: Visualizer):
        for i in range(100):
            x = random.randint(0, CANVAS_WIDTH)
            y = random.randint(0, CANVAS_HEIGHT)
            all_points.append(obj.canv.create_rectangle((x, y) * 2))

    def action_decor(vis: Visualizer):
        def action(event):
            for i in range(min(10, len(all_points))):
                vis.canv.delete(all_points.pop())
        return action


    v = Visualizer(init_func=init_function,
                   action_func=action_decor,
                   capture_points_func=None)

