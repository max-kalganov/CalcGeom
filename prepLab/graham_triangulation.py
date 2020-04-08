from typing import Tuple, Optional, Iterable, Callable

import numpy as np
from PIL._imaging import outline
from sortedcontainers import SortedList
from geompreds import orient2d

from ct import CANVAS_WIDTH, CANVAS_HEIGHT, DEFAULT_NUM_OF_POINTS, DEFAULT_NUM_OF_POINTS_SMALL
from utils import dist, dist_between_points
from visualizer import VisualizerConvexHull


class GrahamTriangulation:
    def __init__(self):
        """
        Инициализация атрибутов
        """

        self.all_points: Optional[SortedList] = None
        self.conv = []
        self.start_point: Optional[Tuple[int, int]] = None
        self.cur_index: Optional[int] = None
        self.lines = []

    def full_init(self, vis: VisualizerConvexHull, num_of_points: int = DEFAULT_NUM_OF_POINTS_SMALL):
        """
        Метод необходим для корректной работы кнопки reinit
        :param vis: объект визуализатора, который выполняет функцию отображения
        :param num_of_points: количество генерируемых точек
        """

        self.__init__()
        self.init_field(vis, num_of_points)

    def _tan_and_dist(self, point: Tuple[float, float]) -> Tuple[float, float]:
        """
        Подсчет тангенса между точкой start_point и point, подсчет дистанции до точки
        :param point: входная точка
        :return: значение тангенса, дистанция до точки
        """
        dist = dist_between_points(self.start_point, point)
        tan = None
        if point == self.start_point:
            tan = 0
        elif point[0] == self.start_point[0] and point[1] != self.start_point[1]:
            tan = (1 if point[1] > self.start_point[1] else -1) * np.inf
        else:
            tan = (point[1] - self.start_point[1]) / (point[0] - self.start_point[0]),
        return tan, dist

    def init_field(self, vis: VisualizerConvexHull, num_of_points: int = DEFAULT_NUM_OF_POINTS_SMALL):
        """
        Инициализация точек
        :param vis: объект визуализатора
        :param num_of_points: количество генерируемых точек
        """
        seen = {}
        x_values = np.random.normal(loc=CANVAS_WIDTH // 2, scale=CANVAS_WIDTH // 8, size=num_of_points)
        y_values = np.random.normal(loc=CANVAS_HEIGHT // 2, scale=CANVAS_HEIGHT // 8, size=num_of_points)
        x_values = x_values[(x_values >= 0) & (x_values <= CANVAS_WIDTH)]
        y_values = y_values[(y_values >= 0) & (y_values <= CANVAS_HEIGHT)]
        min_len = min(len(x_values), len(y_values))
        x_values = x_values[:min_len]
        y_values = y_values[:min_len]

        min_x_ind = np.argmin(x_values)
        self.start_point = x_values[min_x_ind], y_values[min_x_ind]
        self.all_points = SortedList(zip(x_values[x_values != self.start_point[0]],
                                         y_values[y_values != self.start_point[1]]),
                                     key=self._tan_and_dist)

        for x, y in zip(x_values, y_values):
            if x in seen:
                if y not in seen[x]:
                    seen[x].add(y)
                else:
                    continue
            else:
                seen.setdefault(x, {y})
            vis.canv.create_rectangle((x, y) * 2, outline="#ff0000", width=5)

    def action(self, vis: VisualizerConvexHull):
        """
        функция запускается при нажатии кнопки run
        :param vis: объект визуализатора
        """

        self.gen_triangulation()
        self.draw_triangulation(vis)

    def draw_triangulation(self, vis: VisualizerConvexHull):
        """
        отрисовка триангуляции
        :param vis: объект визуализатора
        """

        def divided_coords(line) -> Iterable[int]:
            return [line[0][0], line[0][1], line[1][0], line[1][1]]

        for line in self.lines:
            vis.canv.create_line(*divided_coords(line))

    def gen_triangulation(self):
        """
        построение триангуляции на основе выпуклой оболочки
        """

        def get_next():
            assert self.cur_index <= len(self.all_points)
            if self.cur_index == len(self.all_points):
                el = self.start_point
            else:
                el = self.all_points[self.cur_index]
                self.lines.append((self.start_point, el))
            self.cur_index += 1
            return el

        def is_r_turn(p1: Tuple[float, float], p2: Tuple[float, float], p3: Tuple[float, float]) -> bool:
            """
            проверка поворота
            :param p1: top
            :param p2: v
            :param p3: w
            :return:
                True - поворот правый, либо на прямой
                False - поворот левый
            """
            return orient2d(p1, p2, p3) <= 0

        self.cur_index = 0
        self.conv.append(self.start_point)
        v = get_next()
        w = get_next()
        while w != self.start_point:
            self.lines.append((v, w))
            if is_r_turn(self.conv[-1], v, w):
                v = self.conv.pop()
            else:
                self.conv.append(v)
                v = w
                w = get_next()
        self.conv.append(v)
        self.conv.append(self.start_point)


if __name__ == '__main__':
    alg = GrahamTriangulation()
    v = VisualizerConvexHull(init_func=alg.full_init,
                             action_func=alg.action)
