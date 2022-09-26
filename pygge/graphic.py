from __future__ import annotations

from abc import ABC, abstractmethod

from pygge.abc import HasParent, IsGraphic
from pygge.data_types import Int2d, PositiveInt
from pygge.parent import HasChildren
from pygge.text import HasText
from PIL import Image
import numpy as np
from typing import Optional, Literal


class GraphicCore(IsGraphic, ABC):
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


class Graphic(GraphicCore, HasParent, HasChildren, HasText):
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
            anchor: Literal["upper left"] = "upper left",
            coordinate_frame: Literal["upper left", "center"] = "upper left",

            text_position: Optional[Int2d] = None,
            text_anchor: Literal["upper left"] = "upper left",
            text_coordinate_frame: Literal["upper left", "center"] = "upper left",
            text: Optional[str] = None,
            text_font: Optional[str] = None,
            text_font_size: int = 12,
            text_color: str = "black",
            text_wrap: bool = True,
    ):
        GraphicCore.__init__(self, size=size, color=color)
        HasParent.__init__(
            self,
            parent=parent,
            position=position,
            anchor=anchor,
            coordinate_frame=coordinate_frame
        )
        HasChildren.__init__(self)
        HasText.__init__(
            self,
            text_position=text_position,
            text_anchor=text_anchor,
            text_coordinate_frame=text_coordinate_frame,
            text=text,
            text_font=text_font,
            text_font_size=text_font_size,
            text_color=text_color,
            text_wrap=text_wrap,
        )

    def render(self):
        self._image = Image.new("RGBA", self.size.astuple(), self.color)
        self.text.render()
        for child in self.children.values():
            child.render()
            cropped_image = child.crop()
            self.image.paste(cropped_image, box=child.clamped_box, mask=cropped_image)

    def crop(self):
        cropping_offset = np.array(self.clamped_box) - np.array(self.free_box)
        image = self.image
        if np.any(cropping_offset != 0):
            cropping_box = tuple((np.array(cropping_offset) + np.array((0, 0) + self.image.size)).astype(int))
            image = self.image.crop(box=cropping_box)
        return image
