from typing import Optional, List, Iterable, Dict

import numpy as np

from visualizer import VisualizerSpline


class BSpline:
    def __init__(self):
        self.points = None
        self.b = None
        self.d_ind_to_b_ind: Dict[int, List[int]] = {}

    def change_spline(self, new_point, point_index: int, vis: VisualizerSpline) -> Optional[np.array]:
        self.points[point_index] = new_point
        spline_indices = self.get_indices_to_change(point_index)
        assert point_index in self.d_ind_to_b_ind
        b_indices = self.d_ind_to_b_ind[point_index]
        self._update_b(b_indices)
        all_splines = []
        for i in spline_indices:
            all_splines.append(self._draw(self._calc_spline(self.b[3*i:(3*i+4)]), vis))
        return all_splines

    def get_indices_to_change(self, point_index: int) -> Iterable[int]:
        bottom_bound = max(0, point_index-3)
        upper_bound = min(point_index, self.points.shape[0] - 4)
        return range(bottom_bound, upper_bound+1)

    def _gen_point_to_b_map(self):
        points_shape = self.points.shape[0]
        assert points_shape >= 6

        self.d_ind_to_b_ind[0] = [0]
        self.d_ind_to_b_ind[1] = list(range(1, 4))
        self.d_ind_to_b_ind[2] = list(range(2, 7))

        for d_ind in range(3, points_shape - 1):
            i = d_ind - 2
            self.d_ind_to_b_ind[d_ind] = list(range(3 * i, 3*(i+2) + 1))

        cur_i = points_shape - 3
        self.d_ind_to_b_ind[points_shape - 1] = [cur_i*3]
        self.d_ind_to_b_ind[points_shape - 2] = list(range(3*(cur_i - 1), 3*cur_i))
        self.d_ind_to_b_ind[points_shape - 3] = list(range(3*(cur_i - 2), 3*(cur_i - 1) + 2))

    def _update_b(self, b_indices: List[int]):
        b_to_update = np.array(b_indices)
        border_b = b_to_update[(b_to_update <= 2) | (b_to_update >= (self.b.shape[0] - 3))]
        mid_b = b_to_update[(b_to_update > 2) & (b_to_update < self.b.shape[0] - 3)]

        if border_b.shape:
            self._update_border_b(border_b)

        if mid_b.shape:
            b_i = mid_b[mid_b % 3 == 0]
            b_i_p = mid_b[mid_b % 3 == 1]
            b_i_m = mid_b[mid_b % 3 == 2]

            self.b[b_i_m] = (self.points[b_i_m // 3 + 1] + 2 * self.points[b_i_m // 3 + 2])/3
            self.b[b_i_p] = (2 * self.points[b_i_p // 3 + 1] + self.points[b_i_p // 3 + 2]) / 3
            self.b[b_i] = (self.b[b_i - 1] + self.b[b_i + 1])/2

    def _update_border_b(self, indices: Iterable):
        for i in indices:
            if i in {0, 1}:
                self.b[i] = self.points[i]
            elif i == self.b.shape[0] - 1:
                self.b[i] = self.points[self.points.shape[0] - 1]
            elif i == self.b.shape[0] - 2:
                self.b[i] = self.points[self.points.shape[0] - 2]
            else:
                self.b[i] = (self.points[i//3] + self.points[i//3 + 1])/2

    @staticmethod
    def _calc_spline(cur_b):
        t = np.linspace(0, 1, num=10)
        all_t = np.stack([(1-t)**3, 3*t*(1-t)**2, 3*t**2*(1-t), t**3])
        if cur_b.shape != (4, 2):
            print(cur_b.shape)
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
        return self._draw(func_points, vis) if func_points is not None else None

    def redraw_last(self, vis: VisualizerSpline):
        bi_m2 = (self.points[-3] + self.points[-2])/2
        bi_m1 = self.points[-2]
        bi = self.points[-1]

        last_b = np.stack([bi_m2, bi_m1, bi])
        self.b = np.vstack([self.b[:-4], last_b])
        func_points = self._calc_spline(self.b[-4:])
        self._gen_point_to_b_map()
        return self._draw(func_points, vis)


if __name__ == '__main__':
    vis = VisualizerSpline(BSpline)
    vis.run_loop()
