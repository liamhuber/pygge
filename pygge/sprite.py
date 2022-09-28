from __future__ import annotations

from typing import Optional, Literal

from pygge.data_types import TwoTuple
from pygge.abc import IsGraphic, HasParent
from pygge.traitlets import Int2d, FileTrait
from traitlets import HasTraits, Bool
from abc import ABC


class Sprite(HasParent, HasTraits):
    sprite = FileTrait(default=None, allow_none=True)
    offset = Int2d()
    scale_x = Bool(default_value=False)
    scale_y = Bool(default_value=False)

    def __init__(
            self,
            parent: Optional[IsGraphic] = None,
            position: Optional[TwoTuple] = None,
            anchor: Literal["upper left"] = "upper left",
            coordinate_frame: Literal["upper left", "center"] = "upper left",
            sprite: Optional[str] = None,
            offset: Optional[TwoTuple] = None,
            scale_x: bool = False,
            scale_y: bool = False,
    ):
        HasParent.__init__(self, parent=parent, position=position, anchor=anchor, coordinate_frame=coordinate_frame)
        HasTraits.__init__(sprite=sprite, offset=offset, scale_x=scale_x, scale_y=scale_y)

    @property
    def size(self) -> TwoTuple:
        raise NotImplementedError

    def render(self):
        raise NotImplementedError


class HasSprite(IsGraphic, ABC):
    def __init__(
            self,
            sprite_position: Optional[TwoTuple] = None,
            sprite_anchor: Literal["upper left"] = "upper left",
            sprite_coordinate_frame: Literal["upper left", "center"] = "upper left",
            sprite: Optional[str] = None,
            sprite_offset: Optional[TwoTuple] = None,
            sprite_scale_x: bool = False,
            sprite_scale_y: bool = False,
    ):
        self._sprite = Sprite(
            parent=self,
            position=sprite_position if sprite_position is not None else (0, 0),
            anchor=sprite_anchor,
            coordinate_frame=sprite_coordinate_frame,
            sprite=sprite,
            offset=sprite_offset,
            scale_x=sprite_scale_x,
            scale_y=sprite_scale_y,
        )

    @property
    def sprite(self):
        return self._sprite
