# coding: utf-8
# Copyright (c) Liam Huber
# Distributed under the terms of "New BSD License", see the LICENSE file.

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from . descriptors import Positive, TwoDee, PILArray, IsOneOfThese
from types import MethodType
from textwrap import wrap as textwrap
from copy import deepcopy

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


class Canvas:
    """
    A virtual 2d space that holds graphics.

    Attributes:
        size (Positive): A tuple for the x and y sizes.
        color (str): The color (html or hex) of the graphic background. (Default is None, which gives transparent.)
        children (Children): Holds sub-graphics.
        image (PIL.Image): The actual visual.
        position (tuple): The position
        depth (0): Where the canvas sits in the tree of graphics. It must always be the root.
    """
    size = Positive('size')
    depth = 0

    def __init__(self, size, color=None):
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
        self._image = Image.new("RGBA", self.size.inttuple, self.color or '#0000')

    def save(self, fp, format=None, **params):
        self.image.save(fp, format=format, **params)

    def copy(self):
        return deepcopy(self)

    @staticmethod
    def to_pilarray(x):
        """
        Converts an `numpy.ndarray`-like object to a `PILArray` (which is the same, but has a method for converting
        itself to a tuple of integers).
        """
        return np.array(x).view(PILArray)


class Children:
    """
    Manages sub-graphics of a graphic or canvas. Particularly, organizes the rendering behaviour so that sub-graphics
    with a higher layer value are rendered on top.

    Graphics are added as children by simple assignment, and can then later be removed by calling that child with the
    `remove()` method.

    Note:
         Layer values in sub-sub-graphics of two different sub-graphics don't know about each other. Any two graphics
         which need to know about each other's layer value *must* belong to the same parent graphic.
    """
    reserved_keys = ['_parent', 'parent', '_layer_dict']

    def __init__(self, parent):
        self._parent = None
        self.parent = parent
        self._layer_dict = {}

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, new_parent):
        if not isinstance(new_parent, Canvas):
            raise TypeError("Only Canvas objects can have graphics children, but got {}".format(type(new_parent)))
        self._parent = new_parent

    def __setattr__(self, key, value):
        if key in self.reserved_keys:
            super().__setattr__(key, value)
        else:
            if not isinstance(value, Graphic):
                raise ValueError('The children can only be graphics but got {}'.format(type(value)))
            value._name = key
            value.parent = self.parent
            value.remove = MethodType(remove, value)
            super().__setattr__(key, value)

    def __str__(self):
        return str(self._get_just_child_names())

    def _get_just_child_names(self):
        keys = list(self.__dict__.keys())
        to_remove = np.intersect1d(keys, self.reserved_keys)
        for k in to_remove:
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

    def __len__(self):
        return len(self._get_just_child_names())


def remove(child):
    delattr(child.parent.children, child.name)


class Graphic(Canvas):
    """
    A 2d graphic, possibly holding other sub-graphics.

    Attributes:
        size (Positive): A tuple for the x and y sizes.
        color (str): The color (html or hex) of the graphic background. (Default is #0000, transparent.)
        position (TwoDee): Pixels between the `anchor` of this graphic a the reference point in the parent graphic
            (which depends on the `coordinates` setting). Meaningless if this is not a sub-graphic of a larger graphic.
            (Default is None.)
        anchor ('upper left'/'center'): Whether position indicates the location of the upper-left corner of this graphic
            or the center of it. (Default is 'upper left'.)
        coordinate_frame ('upper left'/'center'): Whether position is measured from the upper left corner of the parent
            graphic (x>0 is right, y>0 is down), or the center of the parent graphic (x>0 is still right, but y>0 is
            up). (Default is 'upper left'.)
        layer (int): The relative rendering order inside the parent canvas; higher layers are rendered on top. (Default
            is 0.)
        angle (float): How much to rotate the graphic by before pasting it onto the parent canvas.
        resample: c.f. PIL documentation for pasting.
        parent (Graphic): The graphic onto which this graphic will be pasted. (Default is None.)
        name (str): The name by which this graphic is known to its parent. (Automatically filled on assignment to a
            parent graphic's `children`.)
        children (Children): Holds sub-graphics to be pasted onto this graphic.
        image (PIL.Image): The actual visual being rendered.
        depth (int): How many layers of parent graphics exist above this one.
    """
    position = TwoDee('position')
    anchor = IsOneOfThese('anchor', 'upper left', 'center')
    coordinate_frame = IsOneOfThese('coordinate_frame', 'upper left', 'center')

    def __init__(
            self,
            size,
            color=None,
            position=None,
            anchor='upper left',
            coordinate_frame='upper left',
            layer=0,
            angle=0,
            resample=0
    ):
        super().__init__(size, color=color)
        self.position = position
        self.anchor = anchor.lower()
        self.coordinate_frame = coordinate_frame.lower()
        self.layer = layer
        self.angle = angle
        self.resample = resample
        self.parent = None
        self._name = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, void):
        raise AttributeError("can't set attribute. Name is set on assignment to a component collection.")

    @property
    def depth(self):
        try:
            return self.parent.depth + 1
        except AttributeError:
            return 0

    def render(self):
        if self.position is not None and self.parent is None:
            raise ValueError("Position is not None, but this graphic has no parent.")
        elif self.position is None and self.parent is not None:
            raise ValueError("Position is None, but this graphic has a parent.")
        if len(self.children) == 0 and self.color is None:
            raise ValueError("Cannot render {} because it is soooooo boring.".format(self._name))
        super().render()

        if self.angle != 0:
            image = self.image.rotate(self.angle, resample=self.resample, expand=True)
        else:
            image = self.image

        if self.parent is None:
            self._image = image
        else:
            if np.any(image.size > self.parent.size):
                raise ValueError('Child {} too big (size={}) for parent (size={})'.format(
                    self.name, image.size, self.parent.size.inttuple
                ))
            self.parent.image.paste(image, box=self._get_render_box(image), mask=image)

    def _get_render_box(self, image):
        size = self.to_pilarray(image.size)

        if self.coordinate_frame == 'upper left':
            position = self.position
        elif self.coordinate_frame == 'center':
            position = 0.5 * self.parent.size + (1, -1) * self.position
        else:
            raise ValueError("Coordinate frame '{}' not recognized, please use 'upper left' or 'center'.".format(
                self.coordinate_frame
            ))

        if self.anchor == 'upper left':
            shift = self.to_pilarray((0, 0))
        elif self.anchor == 'center':
            shift = 0.5 * size
        else:
            raise ValueError("Anchor '{}' not recognized, please use 'upper left' or 'center'.".format(self.anchor))
        corner1 = (position - shift).inttuple
        corner2 = (corner1 + size).inttuple
        max_size = self.parent.size.inttuple
        return self.clamp_to_size_tuple(corner1, max_size) + self.clamp_to_size_tuple(corner2, max_size)

    @staticmethod
    def clamp_to_size_tuple(values, size):
        return tuple(np.clip(values, (0, 0), size).astype(int))


class Picture(Graphic):
    """
    A graphic for holding a picture. Source images will be resized to fit the size of the graphic, leaving empty space
    if necessitated by the relative aspect ratios. A particular subsection of the source image can be used by providing
    the `box` attribute, if desired.

    Attributes:
        (all the attributes of a Graphic plus...)
        content (PIL.Image.Image/str): The image object or path to an image file to use. (Default is None, but it must
            be provided prior to rendering.)
        box (tuple/list/numpy.ndarray): Four int values giving the top-left and bottom-right of the content to sample.
            (Default is None, which uses the largest box centered in the middle of the content which has the same aspect
            ratio as the size of the component.)
    """

    def __init__(
            self,
            size,
            color='#0000',
            position=None,
            layer=0,
            anchor='upper left',
            coordinate_frame='upper left',
            angle=0,
            resample=0,
            content=None,
            box=None):
        super().__init__(
            size,
            color=color,
            position=position,
            anchor=anchor,
            coordinate_frame=coordinate_frame,
            layer=layer,
            angle=angle,
            resample=resample
        )
        self.content = content
        self.box = box

    @staticmethod
    def _ensure_image(image):
        if isinstance(image, Image.Image):
            image = image.convert('RGBA')
        elif isinstance(image, str):
            image = Image.open(image).convert('RGBA')
        else:
            raise ValueError("Expected a PIL.Image or path to an image file.")
        return image

    def _prepare_image(self):
        image = self._ensure_image(self.content)
        if self.box is not None:
            image = image.crop(box=self.box)

        new_size = self._rescale_to_L1_norm_with_locked_aspect_ratio(image.size, self.size)
        new_size = self.clamp_to_size_tuple(new_size, self.size)
        image = image.resize(new_size, resample=self.resample)

        # box = list((0.5 * (new_size - self.size)).inttuple + (0.5 * (new_size + self.size)).inttuple)
        # dx = (box[2] - box[0]) - self.size.inttuple[0]
        # dy = (box[3] - box[1]) - self.size.inttuple[1]
        # box[2] -= dx
        # box[3] -= dy  # To stop stupid rounding errors, TODO: this better
        # image = image.crop(box=box)
        self._image = image

    @staticmethod
    def _rescale_to_L1_norm_with_locked_aspect_ratio(to_rescale, reference):
        ratio = reference / np.array(to_rescale)
        scale = np.amin(ratio)
        return np.array(to_rescale) * scale


class Text(Graphic):
    """
    A graphic for putting text in a picture.

    Attributes:
        (all the attributes of a Graphic plus...)
        content (PIL.Image.Image/str): The text to use. (Default is None, but it must be provided prior to rendering.)
        font (str): The path to a font which is loadable by PIL's `ImageFont.truetype` method (e.g. '.ttf' files).
        font_size (int): The font to_rescale. (Default is 14.)
        font_color (str): The font color as a hex code or html name. (Default is 'black'.)
    """

    def __init__(
            self,
            size,
            color='#0000',
            position=None,
            layer=0,
            anchor='upper left',
            coordinate_frame='upper left',
            angle=0,
            resample=0,
            content=None,
            font=None,
            font_size=14,
            font_color='black'):
        super().__init__(
            size,
            color=color,
            position=position,
            anchor=anchor,
            coordinate_frame=coordinate_frame,
            layer=layer,
            angle=angle,
            resample=resample
        )
        self.content = content
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
        if self.anchor == 'upper left':
            return 0, 0
        elif self.anchor == 'center':
            return (0.5 * (self.size - draw.textsize(text, font=font))).inttuple
        else:
            raise ValueError("Expected an anchor of 'upper left' or 'center' but got {}".format(self.anchor))


class TextBox(Text):
    """
    A graphic for wrapping text boxes.

    Attributes:
        (all the attributes of a Graphic plus...)
        content (PIL.Image.Image/str): The text to use. (Default is None, but it must be provided prior to rendering.)
        font (str): The path to a font which is loadable by PIL's `ImageFont.truetype` method (e.g. '.ttf' files).
        font_size (int): The font to_rescale. (Default is 14.)
        font_color (str): The font color as a hex code or html name. (Default is 'black'.)
    """

    @staticmethod
    def textwrap(text, width):
        return '\n'.join(textwrap(text, width=width))

    def _prepare_image(self):
        image = Image.new("RGBA", self.size.inttuple, self.color)
        draw = ImageDraw.Draw(image)
        wrapped, resized_font = self._shrink_to_box(str(self.content), draw)
        xy = self._get_pos_from_anchor(draw, wrapped, resized_font)
        draw.multiline_text(xy, wrapped, fill=self.font_color, font=resized_font, anchor='L')
        self._image = image

    def _shrink_to_box(self, text, draw):
        """
        Uses largest font and least lines which will fit the text inside the graphic to_rescale.

        Args:
            text (str): The text to shrink.
            draw (ImageDraw.Draw): A Draw factory for this graphic.

        Returns:
            (str): The wrapped text with newline '\n' characters as needed.
            (PIL.ImageFont.FreeTypeFont): The appropriately sized font.
        """
        font_size = self.font_size

        while True:
            font = ImageFont.truetype(self.font, size=font_size)
            wrapped, wrapped_size = self._fit_width(text, draw, font)
            if wrapped_size[1] <= self.size[1]:
                break
            font_size -= 2
        return wrapped, font

    def _fit_width(self, text, draw, font):
        """
        Breaks the text into new lines until the width fits inside the graphic width.

        Args:
            text (str): The text to shrink.
            draw (ImageDraw.Draw): A Draw factory for this graphic.
            font (PIL.ImageFont.FreeTypeFont): The font to use (includes its to_rescale).

        Returns:
            (str): The wrapped text with newline '\n' characters as needed.
            (tuple): The to_rescale of the wrapped font.
        """
        n_lines = 1
        while True:
            width = int(len(text) / n_lines)
            wrapped = self.textwrap(text, width=width)
            wrapped_size = draw.multiline_textsize(wrapped, font=font)
            if wrapped_size[0] <= self.size[0]:
                break
            n_lines += 1
        return wrapped, wrapped_size
