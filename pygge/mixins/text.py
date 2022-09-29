from __future__ import annotations

from PIL import ImageDraw, ImageFont
import numpy as np
from textwrap import wrap as textwrap

from pygge.mixins.family import HasParent
from pygge.traitlets import FontTrait
from pygge.base import Traited
from traitlets import Unicode, Int, Bool
from abc import ABC, abstractmethod


class Text(HasParent):
    text = Unicode(default_value=None, allow_none=True)
    font = FontTrait()
    font_size = Int(default_value=12)
    color = Unicode(default_value="black")
    wrap = Bool(default_value=True)

    def initialize(self):
        self._used_font_size = self.font_size

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


class HasText(Traited, ABC):
    def initialize(self):
        self._text = Text(parent=self)

    @property
    def text(self):
        return self._text

    @property
    @abstractmethod
    def size(self):
        pass

    @property
    @abstractmethod
    def image(self):
        pass
