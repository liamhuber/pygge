from __future__ import annotations

from typing import Optional, Literal
from PIL import ImageDraw, ImageFont
import numpy as np
from textwrap import wrap as textwrap
from pathlib import Path

from pygge.data_types import TwoTuple
from pygge.abc import IsGraphic, HasParent
from pygge.traitlets import FileTrait
from traitlets import HasTraits, Unicode, Int, Bool
from abc import ABC


class FontTrait(FileTrait):
    default_value = str(Path(f"{__file__}").absolute().parent.parent.joinpath("resources/fonts/Roboto-Regular.ttf"))

    def validate(self, obj, value):
        value = self.default_value if value is None else value
        return super().validate(obj, value)


class Text(HasParent, HasTraits):
    text = Unicode(default_value=None, allow_none=True)
    font = FontTrait()
    font_size = Int(default_value=12)
    color = Unicode(default_value="black")
    wrap = Bool(default_value=True)

    def __init__(
            self,
            parent: Optional[IsGraphic] = None,
            position: Optional[TwoTuple] = None,
            anchor: Literal["upper left"] = "upper left",
            coordinate_frame: Literal["upper left", "center"] = "upper left",
            text: Optional[str] = None,
            font: Optional[str] = None,
            font_size: int = 12,
            color: str = "black",
            wrap: bool = True,
    ):
        HasParent.__init__(self, parent=parent, position=position, anchor=anchor, coordinate_frame=coordinate_frame)
        HasTraits.__init__(self, text=text, font=font, font_size=font_size, color=color, wrap=wrap)
        self._used_font_size = font_size

    @property
    def draw(self):
        return ImageDraw.Draw(self.parent.image)

    @property
    def size(self):
        if self.wrap:
            _, _, size = self._shrunk_to_box()
        else:
            size = self.draw.textsize(self.text, font=self._used_font_size)
        return size

    def render(self):
        if self.text is None:
            return
        if self.wrap:
            text, font, _ = self._shrunk_to_box()
            draw_method = self.draw.multiline_text
        else:
            font = ImageFont.truetype(self.font, size=self.font_size)
            draw_method = self.draw.text
        self._ensure_leq(self.size, self.parent.size)
        draw_method(self.position_on_parent.astuple(), self.text, fill=self.color, font=font, anchor='la')

    def _shrunk_to_box(self):
        """
        Uses largest font and least lines which will fit the text inside the graphic to_rescale.

        Returns:
            (str): The wrapped text with newline '\n' characters as needed.
            (PIL.ImageFont.FreeTypeFont): The appropriately sized font.
        """
        font_size = self.font_size
        print(self.font)
        while True:
            font = ImageFont.truetype(self.font, size=font_size)
            wrapped, wrapped_size = self._fit_width(font)
            if wrapped_size[1] + self.position[1] <= self.parent.size[1]:
                break
            font_size -= 1
        return wrapped, font, wrapped_size

    def _fit_width(self, font):
        """
        Breaks the text into new lines until the width fits inside the graphic width.

        Args:
            font (PIL.ImageFont.FreeTypeFont): The font to use (includes its to_rescale).

        Returns:
            (str): The wrapped text with newline '\n' characters as needed.
            (tuple): The to_rescale of the wrapped font.
        """
        n_lines = 1
        while True:
            width = int(len(self.text) / n_lines)
            wrapped = self.textwrap(self.text, width=width)
            wrapped_size = self.draw.multiline_textsize(wrapped, font=font)
            if wrapped_size[0] + self.position[0] <= self.parent.size[0]:
                break
            n_lines += 1
        return wrapped, wrapped_size

    @staticmethod
    def textwrap(text, width):
        return '\n'.join(textwrap(text, width=width))

    @staticmethod
    def _ensure_leq(size, bounds):
        if not np.all(size <= bounds):
            raise ValueError("{} is not always <= {}".format(size, bounds))


class HasText(ABC):
    def __init__(
            self,
            text_position: Optional[TwoTuple] = None,
            text_anchor: Literal["upper left"] = "upper left",
            text_coordinate_frame: Literal["upper left", "center"] = "upper left",
            text: Optional[str] = None,
            text_font: Optional[str] = None,
            text_font_size: int = 12,
            text_color: str = "black",
            text_wrap: bool = True,
    ):
        self._text = Text(
            parent=self,
            position=text_position if text_position is not None else (0, 0),
            anchor=text_anchor,
            coordinate_frame=text_coordinate_frame,
            text=text,
            font=text_font,
            font_size=text_font_size,
            color=text_color,
            wrap=text_wrap
        )

    @property
    def text(self):
        return self._text
