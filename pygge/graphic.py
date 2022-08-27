from __future__ import annotations

from pygge.abc import GraphicCore, HasParent
from pygge.data_types import Int2d, PositiveInt
from pygge.parent import HasChildren
from PIL import Image
import numpy as np
from typing import Tuple, Optional, Literal


class IsChild(GraphicCore, HasParent):
    def __init__(
            self,
            size: PositiveInt,
            color: str = '#0000',
            parent: Optional[Graphic] = None,
            position: Optional[Int2d] = None,
            anchor: Literal["upper left"] = "upper left",
            coordinate_frame: Literal["upper left", "center"] = "upper left"
    ):
        GraphicCore.__init__(self, size=size, color=color)
        HasParent.__init__(
            self,
            parent=parent,
            position=position,
            anchor=anchor,
            coordinate_frame=coordinate_frame
        )

    def crop(self):
        cropping_offset = np.array(self.clamped_box) - np.array(self.free_box)
        image = self.image
        if np.any(cropping_offset != 0):
            cropping_box = tuple((np.array(cropping_offset) + np.array((0, 0) + self.image.size)).astype(int))
            image = self.image.crop(box=cropping_box)
        return image

    @property
    def _numeric_anchor(self) -> Int2d:
        if self.anchor == "upper left":
            return Int2d(0, 0)
        elif self.anchor == "center":
            return Int2d(self.size * 0.5)
        else:
            raise ValueError(f"Anchor frame '{self.anchor}' not recognized")

    @property
    def corner1(self) -> Int2d:
        if self.parent is not None:
            return self.relative_position - self._numeric_anchor
        else:
            return Int2d(0, 0)

    @property
    def corner2(self) -> Int2d:
        return self.corner1 + self.size

    @property
    def free_box(self) -> Tuple[int, int, int, int]:
        return self.corner1.astuple() + self.corner2.astuple()

    @property
    def clamped_box(self) -> Tuple[int, int, int, int]:
        return self.corner1.clamp(min_=(0, 0), max_=self.parent.size).astuple() + \
               self.corner2.clamp(min_=(0, 0), max_=self.parent.size).astuple()


class Graphic(IsChild, HasChildren):
    """
    Example:
        >>> graphic = Graphic(
        >>>     (100, 400),
        >>>     color='black'
        >>> )
        >>> graphic.children.title = Graphic(
        >>>         graphic.size * (0.9, 0.1),
        >>>         position=graphic.size * 0.05,
        >>>         text='The Title'
        >>>     )
        >>> )
        >>> graphic.image.show()
    """
    def __init__(
            self,
            size: PositiveInt,
            color: str = '#0000',
            parent: Optional[Graphic] = None,
            position: Optional[Int2d] = None,
    ):
        IsChild.__init__(self, size=size, color=color, parent=parent, position=position)
        HasChildren.__init__(self)

    def render(self):
        self._image = Image.new("RGBA", self.size.astuple(), self.color)
        for child in self.children.values():
            child.render()
            cropped_image = child.crop()
            self.image.paste(cropped_image, box=child.clamped_box, mask=cropped_image)
