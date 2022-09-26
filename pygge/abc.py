from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Literal, Tuple

from pygge.data_types import Int2d


class IsGraphic(ABC):
    """For typing"""
    @property
    @abstractmethod
    def size(self):
        pass

    @property
    @abstractmethod
    def image(self):
        pass


class HasParent(ABC):
    def __init__(
            self,
            parent: IsGraphic,
            position: Optional[Int2d] = None,
            anchor: Literal["upper left"] = "upper left",
            coordinate_frame: Literal["upper left", "center"] = "upper left"
    ):
        self.parent = parent
        self._position = None
        self.position = position if position is not None else (0, 0)
        self.anchor = anchor
        self.coordinate_frame = coordinate_frame

    @property
    @abstractmethod
    def size(self):
        pass

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, new_pos):
        self._position = Int2d(new_pos)

    @property
    def _relative_position(self) -> Int2d:
        if self.coordinate_frame == "upper left":
            return self.position
        elif self.coordinate_frame == "center":
            return self.position * (1, -1) + self.parent.size * 0.5
        else:
            raise ValueError(f"Coordinate frame '{self.coordinate_frame}' not recognized")

    @property
    def _numeric_anchor(self) -> Int2d:
        if self.anchor == "upper left":
            return Int2d(0, 0)
        elif self.anchor == "center":
            return Int2d(self.size * 0.5)
        else:
            raise ValueError(f"Anchor frame '{self.anchor}' not recognized")

    @property
    def position_on_parent(self) -> Int2d:
        return self._relative_position - self._numeric_anchor

    @property
    def corner1(self) -> Int2d:
        return self.position_on_parent

    @property
    def corner2(self) -> Int2d:
        return self.position_on_parent + self.size

    @property
    def free_box(self) -> Tuple[int, int, int, int]:
        return self.position_on_parent.astuple() + self.corner2.astuple()

    @property
    def clamped_box(self) -> Tuple[int, int, int, int]:
        return self.position_on_parent.clamp(min_=(0, 0), max_=self.parent.size).astuple() + \
               self.corner2.clamp(min_=(0, 0), max_=self.parent.size).astuple()
