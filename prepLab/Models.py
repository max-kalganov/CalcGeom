from typing import Tuple

from dataclasses import dataclass


@dataclass
class Dot:
    x: int
    y: int

    def get_tuple(self) -> Tuple[int, int]:
        return (self.x, self.y)
