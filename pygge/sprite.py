from __future__ import annotations

from typing import Optional, Literal

from pygge.data_types import Int2d
from pygge.abc import IsGraphic, HasParent


class Sprite(HasParent):
    def __init__(
            self,
            parent: IsGraphic,
            position: Optional[Int2d] = None,
            anchor: Literal["upper left"] = "upper left",
            coordinate_frame: Literal["upper left", "center"] = "upper left",
            sprite: Optional[str] = None,
            offset: Optional[Int2d] = None,
            scale_x: bool = False,
            scale_y: bool = False,
    ):
        super().__init__(parent=parent, position=position, anchor=anchor, coordinate_frame=coordinate_frame)
        self.sprite = sprite
        self.offset = Int2d(offset) if offset is not None else Int2d(0, 0)
        self.scale_x = scale_x
        self.scale_y = scale_y


class HasSprite(IsGraphic):
    def __init__(
            self,
            sprite_position: Optional[Int2d] = None,
            sprite_anchor: Literal["upper left"] = "upper left",
            sprite_coordinate_frame: Literal["upper left", "center"] = "upper left",
            sprite: Optional[str] = None,
            sprite_offset: Optional[Int2d] = None,
            sprite_scale_x: bool = False,
            sprite_scale_y: bool = False,
    ):
        self._sprite = Sprite(
            parent=self,
            position=sprite_position,
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
