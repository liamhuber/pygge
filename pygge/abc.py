from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Literal, Tuple

from pygge.data_types import TwoTuple
from pygge.traitlets import Int2d, PositiveInt, ImageTrait, Anchor, CoordinateFrame
from traitlets import HasTraits, Instance


class MetaTraited(type(HasTraits), type(ABC)):
    pass


class IsGraphic(HasTraits, ABC, metaclass=MetaTraited):
    """For typing"""
    size = PositiveInt()
    _image = ImageTrait()

    def __init__(self, size):
        HasTraits.__init__(self, size=size)

    @property
    def image(self):
        if self._image is None:
            self.render()
        return self._image

    @abstractmethod
    def render(self):
        pass


class HasParent(HasTraits, ABC, metaclass=MetaTraited):
    parent = Instance(klass=IsGraphic, allow_none=True, default_value=None)
    position = Int2d(allow_none=True)
    anchor = Anchor()
    coordinate_frame = CoordinateFrame()

    def __init__(
            self,
            parent: Optional[IsGraphic] = None,
            position: Optional[Int2d] = None,
            anchor: Literal["upper left"] = "upper left",
            coordinate_frame: Literal["upper left", "center"] = "upper left"
    ):
        if parent is not None and position is None:
            raise TypeError("Objects with a parent must also provide a position, but got None")
        HasTraits.__init__(self, parent=parent, position=position, anchor=anchor, coordinate_frame=coordinate_frame)

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
