from __future__ import annotations

from pygge.base import IsGraphic
from pygge.mixins import HasParent, HasChildren, HasSprite, HasText
from pygge.traitlets import Int2d
from traitlets import Unicode
from PIL import Image
import numpy as np
from typing import Optional, Literal


class Graphic(IsGraphic, HasParent, HasChildren, HasText):  # HasSprite
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
    color = Unicode(default_value="#0000")

    def __init__(
            self,
            *args,
            text_position: Optional[Int2d] = None,
            text_anchor: Literal["upper left"] = "upper left",
            text_coordinate_frame: Literal["upper left", "center"] = "upper left",
            text: Optional[str] = None,
            text_font: Optional[str] = None,
            text_font_size: int = 12,
            text_color: str = "black",
            text_wrap: bool = True,
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.text.position = text_position if text_position is not None else self.text.position
        self.text.anchor = text_anchor
        self.text.coordinate_frame = text_coordinate_frame
        self.text.text = text
        self.text.font = text_font if text_font is not None else self.text.font
        self.text.font_size = text_font_size
        self.text.color = text_color
        self.text.wrap = text_wrap



    def render(self):
        self._image = Image.new("RGBA", self.size.astuple(), self.color)
        self.text.render()
        for child in self.children.values():
            cropped_image = child.cropped_image
            self.image.paste(cropped_image, box=child.clamped_box, mask=cropped_image)

    @property
    def cropped_image(self):
        cropping_offset = np.array(self.clamped_box) - np.array(self.free_box)
        image = self.image
        if np.any(cropping_offset != 0):
            cropping_box = tuple((np.array(cropping_offset) + np.array((0, 0) + self.image.size)).astype(int))
            image = self.image.crop(box=cropping_box)
        return image
