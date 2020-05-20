# coding: utf-8
# Copyright (c) Liam Huber
# Distributed under the terms of "New BSD License", see the LICENSE file.

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from . datatypes import Positive, TwoDee, PILArray
from types import MethodType
from textwrap import wrap as textwrap

"""
A base class for building on PIL images.
"""

__author__ = "Liam Huber"
__copyright__ = "Copyright 2020, Liam Huber"
__version__ = "0.0"
__maintainer__ = "Liam Huber"
__email__ = "liam.huber@gmail.com"
__status__ = "development"
__date__ = "May 11, 2020"


class Graphic:
    """
    A base class for images.

    Attributes:
        size (Positive): A tuple for the x and y sizes.
        color (str): The color (html or hex) of the graphic background. (Default is #0000, transparent.)
        children (Children): Holds components.
        image (PIL.Image): The actual visual.
    """
    size = Positive()

    def __init__(self, size, color="#0000"):
        self.size = size
        self.color = color
        self.children = Children(self)
        self._image = None

    @property
    def image(self):
        if self._image is None:
            self.render()
        return self._image

    def render(self):
        """
        Layer components into an image.

        Returns:
            (PIL.Image): The graphic for this game piece.

        Raises:
            ValueError: If content is not set for *all* components.
        """
        self._prepare_image()
        self.children.render()

    def _prepare_image(self):
        self._image = Image.new("RGBA", self.size.inttuple, self.color)

    def save(self, fp, format=None, **params):
        self.image.save(fp, format=format, **params)

    def to_pilarray(self, x):
        return np.array(x).view(PILArray)


class Children:
    reserved_keys = ['_parent', '_layer_dict', 'n_children']

    def __init__(self, parent):
        self._parent = parent
        self._layer_dict = {}
        self.n_children = 0

    def __setattr__(self, key, value):
        if key in self.reserved_keys:
            super().__setattr__(key, value)
        else:
            if not isinstance(value, Component):
                raise ValueError('The children can only be graphics but got {}'.format(type(value)))
            value._name = key
            value._parent = self._parent
            value.remove = MethodType(remove, value)
            self._layer_dict[key] = value.layer
            self.n_children += 1
            super().__setattr__(key, value)

    def __str__(self):
        return str(self._get_just_child_names())

    def _get_just_child_names(self):
        keys = list(self.__dict__.keys())
        for k in self.reserved_keys:
            keys.remove(k)
        return keys

    def render(self):
        ordered_children = self._get_children_in_order()
        for child in ordered_children:
            child.render()

    def _get_children_in_order(self):
        layers = []
        children = []
        for k in self._get_just_child_names():
            child = getattr(self, k)
            layer = child.layer
            children.append(child)
            layers.append(layer)
        return [children[n] for n in np.argsort(layers)]


def remove(child):
    child._parent.n_children -= 1
    delattr(child._parent.children._zorder_dict, child._name)
    delattr(child._parent.children, child._name)


class Component(Graphic):
    """
    Components are images or text which are added to a canvas in layers.

    Attributes:
        position (TwoDee): Pixels relative to the anchor position to shift the component when applying it to the
            parent canvas (positive values are right and down for 'upper left' anchor, right and up for 'center').
        content: The actual meat of the component.
        layer (int): What order to apply the component to the canvas (lower layers are applied earlier.) (Default is 0.)
        anchor ('upper left'/'center'): Whether to compare upper left corners of the canvas and component, or centers
            for applying the component to the canvas.
        angle (float): How much to rotate the source by in degrees. (Default is 0.)
        resample: c.f. PIL.resize docs.
    """
    position = TwoDee()

    def __init__(self, size, color='#0000', position=None, content=None, layer=0, anchor='upper left', angle=0, resample=0):
        super().__init__(size, color=color)
        self.position = position
        self._name = None
        self._parent = None
        self.content = content
        self.layer = layer
        self.anchor = anchor
        self.angle = angle
        self.resample = resample

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, void):
        raise AttributeError("can't set attribute. Name is set on assignment to a component collection.")

    def render(self):
        if self.content is None and self.children.n_children == 0:
            raise ValueError("Cannot render {} because no content is set and it has no children.".format(self._name))
        super().render()
        if self.angle != 0:
            image = self.image.rotate(self.angle, resample=self.resample, expand=True)
        else:
            image = self.image
        self._parent.image.paste(image, box=self._get_render_box(image), mask=image)

    def _get_render_box(self, image):
        if self.anchor.lower() == 'upper left':
            return self.position.inttuple + (self.position + image.size).inttuple
        elif self.anchor.lower() == 'center':
            position = 0.5*self._parent.size + (1, -1)*self.position
            return (position - 0.5 * np.array(image.size)).inttuple + (position + 0.5 * np.array(image.size)).inttuple
        else:
            raise ValueError("Expected an anchor of {} or {} but got {}".format('upper left', 'center', self.anchor))

    def get_depth(self, d=0):
        """Find the distance from this component to the owning game piece."""
        d += 1
        try:
            return self._parent.get_depth(d=d)
        except AttributeError:
            return d

    def set_relative_position(self, relative_position):
        self.position = np.array(relative_position) * self._parent.size


class Picture(Component):
    """
    A component for putting in a picture.

    Attributes:
        box (tuple/list/numpy.ndarray): Four int values giving the top-left and bottom-right of the content to sample.
            (Default is None, which uses the largest box centered in the middle of the content which has the same aspect
            ratio as the size of the component.)
    """

    def __init__(self, size, color='#0000', position=None, content=None, layer=0, anchor='upper left', angle=0, resample=0, box=None):
        super().__init__(size, color=color, position=position, content=content, layer=layer, anchor=anchor, angle=angle, resample=resample)
        self.box = box

    def _ensure_image(self, image):
        if isinstance(image, Image.Image):
            image = image.convert('RGBA')
        elif isinstance(image, str):
            if image[0] == '#':
                image = Image.new('RGBA', self.size.inttuple, image)
            else:
                image = Image.open(image).convert('RGBA')
        else:
            raise ValueError("Expected a PIL.Image, hex-code color, or path to an image file.")
        return image

    def _prepare_image(self):
        image = self._ensure_image(self.content)
        if self.box is not None:
            image = image.crop(box=self.box)
        ratio = self.size / np.array(image.size)
        if np.all(ratio <= 1):
            scale = np.amax(ratio)
        else:
            scale = np.amin(ratio)
        new_size = np.array(image.size) * scale
        image = image.resize(tuple(new_size.astype(int)), resample=self.resample)
        box = list((0.5 * (new_size - self.size)).inttuple + (0.5 * (new_size + self.size)).inttuple)
        dx = (box[2] - box[0]) - self.size.inttuple[0]
        dy = (box[3] - box[1]) - self.size.inttuple[1]
        box[2] -= dx
        box[3] -= dy  # To stop stupid rounding errors, TODO: this better
        image = image.crop(box=box)
        self._image = image


class Text(Component):
    """
    A component with text.
    """

    def __init__(self, size, color='#0000', position=None, content=None, layer=0, anchor='upper left', angle=0, resample=0,
                 font=None, font_size=14, font_color='black'):
        super().__init__(size, color=color, position=position, content=content, layer=layer, anchor=anchor, angle=angle, resample=resample)
        self.font = font
        self.font_size = font_size
        self.font_color = font_color

    def _prepare_image(self):
        image = Image.new("RGBA", self.size.inttuple, self.color)
        text = str(self.content)
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(self.font, size=self.font_size)
        xy = self._get_pos_from_anchor(draw, text, font)
        draw.text(xy, text, fill=self.font_color, font=font, anchor='L')
        self._image = image

    def _get_pos_from_anchor(self, draw, text, font):
        if self.anchor.lower() == 'upper left':
            return 0, 0
        elif self.anchor.lower() == 'center':
            return (0.5 * (self.size - draw.textsize(text, font=font))).inttuple
        else:
            raise ValueError("Expected an anchor of 'upper left' or 'center' but got {}".format(self.anchor))


class TextBox(Text):
    """
    A component with wrapping text.
    """

    @staticmethod
    def textwrap(text, width):
        return '\n'.join(textwrap(text, width=width))

    def _prepare_image(self):
        image = Image.new("RGBA", self.size.inttuple, self.color)
        # text = str(self.content)
        draw = ImageDraw.Draw(image)

        # wrapped = self._get_wrapped_text(text, draw)
        # resized_font = self._get_shrunk_font(wrapped, draw)
        wrapped, resized_font = self._shrink_to_box(str(self.content), draw)

        xy = self._get_pos_from_anchor(draw, wrapped, resized_font)
        draw.multiline_text(xy, wrapped, fill=self.font_color, font=resized_font, anchor='L')
        self._image = image

    def _shrink_to_box(self, text, draw):
        font_size = self.font_size

        while True:
            font = ImageFont.truetype(self.font, size=font_size)
            wrapped, wrapped_size = self._fit_width(text, draw, font)
            if wrapped_size[1] <= self.size[1]:
                break
            font_size -= 2
        return wrapped, font

    def _fit_width(self, text, draw, font):
        n_lines = 1
        while True:
            width = int(len(text) / n_lines)
            wrapped = self.textwrap(text, width=width)
            wrapped_size = draw.multiline_textsize(wrapped, font=font)
            if wrapped_size[0] <= self.size[0]:
                break
            n_lines += 1
        return wrapped, wrapped_size

    def _get_wrapped_text(self, text, draw):
        """
        Wrap text into multiple lines until the aspect ratio approximates the underlying component.

        Args:
            text (str): The text to wrap.
            draw (PIL.ImageDraw.Draw): The drawing tool.

        Returns:
            (list): The text split into a list with one element for each line.
        """
        component_aspect = self.size[1] / self.size[0]
        font = ImageFont.truetype(self.font, size=self.font_size)
        n_lines = 1
        while True:
            width = int(len(text) / n_lines)
            wrapped = self.textwrap(text, width=width)
            wrapped_size = draw.multiline_textsize(wrapped, font=font)
            wrapped_aspect = wrapped_size[1] / wrapped_size[0]
            if wrapped_aspect > component_aspect:
                break
            n_lines += 1
        return wrapped

    def _get_shrunk_font(self, wrapped, draw):
        """
        Shrink font until the wrapped text fits inside the component's size.

        Args:
            wrapped (list): The text
            draw (PIL.ImageDraw.Draw): The drawing tool.

        Returns:
            (PIL.ImageFont.FreeTypeFont): The resized font.
        """
        font_size = self.font_size
        while True:
            font = ImageFont.truetype(self.font, size=font_size)
            text_size = draw.multiline_textsize(wrapped, font=font)

            if np.any(text_size > self.size):
                font_size -= 2
            else:
                break
        return font
