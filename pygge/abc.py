from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Literal

from pygge.data_types import PositiveInt, Int2d


class GraphicCore(ABC):
    def __init__(
            self,
            size: PositiveInt,
            color: str = '#0000',
    ):
        self._size = None
        self.size = size
        self.color = color
        self._image = None

    @property
    def size(self) -> PositiveInt:
        return self._size

    @size.setter
    def size(self, new_size):
        if isinstance(new_size, PositiveInt):
            self._size = new_size
        else:
            self._size = PositiveInt(new_size)

    @property
    def image(self):
        if self._image is not None:
            return self._image
        else:
            self.render()
            return self._image

    @abstractmethod
    def render(self):
        pass


class HasParent:
    def __init__(
            self,
            parent: GraphicCore = None,
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
    def position(self):
        return self._position

    @position.setter
    def position(self, new_pos):
        self._position = Int2d(new_pos)

    @property
    def relative_position(self) -> Int2d:
        if self.coordinate_frame == "upper left":
            return self.position
        elif self.coordinate_frame == "center":
            return self.position * (1, -1) + self.parent.size * 0.5
        else:
            raise ValueError(f"Coordinate frame '{self.coordinate_frame}' not recognized")
