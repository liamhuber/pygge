from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Tuple

from traitlets import Instance, Dict

from pygge.base import IsGraphic, Traited
from pygge.data_types import TwoTuple
from pygge.traitlets import Int2d, Anchor, CoordinateFrame


class HasParent(Traited, ABC):
    parent = Instance(klass=IsGraphic, allow_none=True, default_value=None)
    position = Int2d(allow_none=True)
    anchor = Anchor()
    coordinate_frame = CoordinateFrame()

    def initialize(self, *args, **kwargs):
        if self.parent is not None and self.position is None:
            raise TypeError("Objects with a parent must also provide a position, but got None")

    @property
    @abstractmethod
    def size(self) -> TwoTuple:
        pass

    @property
    def _relative_position(self) -> TwoTuple:
        if self.parent is None:
            return TwoTuple(0, 0)

        if self.coordinate_frame == "upper left":
            return self.position
        elif self.coordinate_frame == "center":
            return self.position * (1, -1) + self.parent.size * 0.5
        else:
            raise ValueError(f"Coordinate frame '{self.coordinate_frame}' not recognized")

    @property
    def _numeric_anchor(self) -> TwoTuple:
        if self.parent is None:
            return TwoTuple(0, 0)

        if self.anchor == "upper left":
            return TwoTuple(0, 0)
        elif self.anchor == "center":
            return TwoTuple(self.size * 0.5)
        else:
            raise ValueError(f"Anchor frame '{self.anchor}' not recognized")

    @property
    def position_on_parent(self) -> TwoTuple:
        return self._relative_position - self._numeric_anchor

    @property
    def corner1(self) -> TwoTuple:
        return self.position_on_parent

    @property
    def corner2(self) -> TwoTuple:
        return self.position_on_parent + self.size

    @property
    def free_box(self) -> Tuple[int, int, int, int]:
        return self.position_on_parent.astuple() + self.corner2.astuple()

    @property
    def clamped_box(self) -> Tuple[int, int, int, int]:
        return self.position_on_parent.clamp(min_=(0, 0), max_=self.parent.size).astuple() + \
               self.corner2.clamp(min_=(0, 0), max_=self.parent.size).astuple()


class Adder:
    def __init__(self, parent: HasChildren):
        self._parent = parent

    def __call__(self, name: str, child):
        self._parent.children[name] = child


class HasChildren(Traited, ABC):
    children = Dict(default_value={}, read_only=True)

    def initialize(self):
        self._adder = Adder(self)

    @property
    def add(self):
        return self._adder

    def remove(self, key):
        return self.children.pop(key)
