from typing import Optional

import numpy as np

from visualizer import VisualizerSpline


class BSpline:
    def __init__(self):
        self.points = None
        self.b = None

    def change_spline(self, new_point, point_index: int, vis:VisualizerSpline) -> Optional[np.array]:
        self.points[point_index] = new_point
        spline_indices = self.get_indices_to_change(point_index)
        b_indices = self._get_b_indices_to_change(spline_indices)
        self._calc_new_b(b_indices)
        all_splines = []
        for i in spline_indices:
            all_splines.append(self._draw(self._calc_spline(self.b[3*i:(3*i+4)]), vis))
        return all_splines

    def _calc_spline(self, cur_b):
        t = np.linspace(0, 1, num=10)
        all_t = np.stack([(1-t)**3, 3*t*(1-t)**2, 3*t**2*(1-t), t**3])
        assert cur_b.shape == (4, 2), f"wrong shape"
        return all_t.transpose() @ cur_b

    def get_b(self, i):
        bi_m1 = (self.points[i-2] + 2 * self.points[i-1])/3
        bi_p1 = (2 * self.points[i-1] + self.points[i])/3
        bi = (bi_m1 + bi_p1) / 2
        return np.stack([bi_m1, bi, bi_p1])

    def _add_spline(self) -> Optional[np.array]:
        if len(self.points) == 3:
            self.b = np.stack([self.points[0], self.points[1]])
        elif len(self.points) > 3:
            last_b = self.get_b(-1)
            spline = self._calc_spline(np.vstack([self.b[-2:], last_b[:-1]]))
            self.b = np.vstack([self.b, last_b])
            return spline
        return None

    def _draw(self, func_points, vis: VisualizerSpline):
        shape = func_points.shape
        spline = vis.canv.create_line(func_points.reshape(1, shape[0] * shape[1])[0].tolist())
        return spline

    def draw_spline(self, vis: VisualizerSpline, new_point: np.array, index: Optional[int] = None):
        self.points = np.vstack([self.points, new_point]) if self.points is not None \
            else np.array([new_point.tolist()])
        func_points = self._add_spline()

        if func_points is None:
            return None
        else:
            return self._draw(func_points, vis)

    def redraw_last(self, vis: VisualizerSpline):
        bi_m2 = (self.points[-3] + self.points[-2])/2
        bi_m1 = self.points[-2]
        bi = self.points[-1]

        last_b = np.stack([bi_m2, bi_m1, bi])
        self.b = np.vstack([self.b[:-4], last_b])
        func_points = self._calc_spline(self.b[-4:])
        return self._draw(func_points, vis)


if __name__ == '__main__':
    vis = VisualizerSpline(BSpline)
    vis.run_loop()
