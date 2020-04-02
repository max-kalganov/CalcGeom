from typing import Dict, Tuple, List

from Models import Dot, FloatDot, VDEdge

main_dots: Dict[Tuple[int, int], Dot] = {}
mid_dots: Dict[Tuple[float, float], FloatDot] = {}
main_dot_to_edge: Dict[Dot, List[VDEdge]] = {}


def get_main_dot(x: int, y: int) -> Dot:
    pair = (x, y)
    if pair not in main_dots:
        new_dot = Dot(x, y)
        main_dots[pair] = new_dot
    return main_dots[pair]


def get_mid_dot(x: float, y: float) -> FloatDot:
    pair = (x, y)
    if pair not in mid_dots:
        new_dot = FloatDot(x, y)
        mid_dots[pair] = new_dot
    return mid_dots[pair]


def get_vdedges(point: Dot) -> List[VDEdge]:
    main_dot_to_edge.setdefault(point, [])
    return main_dot_to_edge[point]
