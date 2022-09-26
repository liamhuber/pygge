from __future__ import annotations

from typing import Optional, Literal
from PIL import ImageDraw, ImageFont
import numpy as np
from textwrap import wrap as textwrap
from pathlib import Path

from pygge.data_types import Int2d
from pygge.abc import IsGraphic, HasParent


class Text(HasParent):
    def __init__(
            self,
            parent: IsGraphic,
            position: Optional[Int2d] = None,
            anchor: Literal["upper left"] = "upper left",
            coordinate_frame: Literal["upper left", "center"] = "upper left",
            text: str = "",
            font: Optional[str] = None,
            font_size: int = 12,
            color: str = "black",
            wrap: bool = True,
    ):
        super().__init__(parent=parent, position=position, anchor=anchor, coordinate_frame=coordinate_frame)
        self.text = text
        self._font = None
        self.font = font
        self.font_size = font_size
        self._used_font_size = font_size
        self.color = color
        self.wrap = wrap

    @property
    def font(self):
        return self._font if self._font is not None \
            else str(Path(f"{__file__}").absolute().parent.parent.joinpath("resources/fonts/Roboto-Regular.ttf"))

    @font.setter
    def font(self, new_font):
        # Use default if is None
        if new_font is None:
            new_font = None  # Up two, resources, fonts, Roboto-Regular.ttf
        elif not Path(new_font).is_file():
            raise ValueError(f"Font file {new_font} not found.")
        self._font = new_font

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


class HasText(IsGraphic):
    def __init__(
            self,
            text_position: Optional[Int2d] = None,
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
            position=text_position,
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
