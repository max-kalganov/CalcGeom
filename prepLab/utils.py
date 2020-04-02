from typing import Dict, Tuple, List, Union, Optional

from Models import Dot, FloatDot, VDEdge

main_dots: Dict[Tuple[int, int], Dot] = {}
mid_dots: Dict[Tuple[float, float], FloatDot] = {}
main_dot_to_edge: Dict[Tuple[int, int], List[VDEdge]] = {}


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
    main_dot_to_edge.setdefault(point.get_tuple(), [])
    return main_dot_to_edge[point.get_tuple()]


def get_border_points(full_conv: List[Dot], conv_s1: List[Dot], conv_s2: List[Dot]) -> Tuple[int, int, int, int]:
    start_left_ind = 0
    finish_left_ind = 0
    start_right_ind = 0
    finish_right_ind = 0
    pointer = 0
    if full_conv[pointer] in conv_s1:
        while full_conv[pointer] in conv_s1:
            pointer = (pointer + 1) % len(full_conv)
        start_left_ind = conv_s1.index(full_conv[pointer - 1])
        start_right_ind = conv_s2.index(full_conv[pointer])

        while full_conv[pointer] not in conv_s1:
            pointer = (pointer + 1) % len(full_conv)
        finish_left_ind = conv_s1.index(full_conv[pointer])
        finish_right_ind = conv_s2.index(full_conv[pointer - 1])

    else:
        while full_conv[pointer] not in conv_s1:
            pointer = (pointer + 1) % len(full_conv)
        finish_left_ind = conv_s1.index(full_conv[pointer])
        finish_right_ind = conv_s2.index(full_conv[pointer - 1])

        while full_conv[pointer] in conv_s1:
            pointer = (pointer + 1) % len(full_conv)
        start_left_ind = conv_s1.index(full_conv[pointer - 1])
        start_right_ind = conv_s2.index(full_conv[pointer])

    return start_left_ind, start_right_ind, finish_left_ind, finish_right_ind


def dist(point1: Union[Dot, FloatDot], point2: Union[Dot, FloatDot]) -> float:
    return ((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2) ** (1/2)
