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
Base classes for allowing simple graphic design on top of PIL Images.
"""

__author__ = "Liam Huber"
__copyright__ = "Copyright 2020, Liam Huber"
__version__ = "0.0"
__maintainer__ = "Liam Huber"
__email__ = "liam.huber@gmail.com"
__status__ = "development"
__date__ = "May 11, 2020"

ANCHOR_POSITIONS = ['upper left', 'center']


class Graphic:
    """
    A 2d graphic, possibly holding other sub-graphics.

    Attributes:
        size (Positive): A 2-tuple of integers for the x and y sizes.
        color (str): The color (html or hex) of the graphic background. (Default is #0000, transparent.)
        position (TwoDee): Pixels between the `anchor` of this graphic a the reference point in the parent graphic
            (which depends on the `coordinates` setting). Meaningless if this is not a sub-graphic of a larger graphic.
            (Default is None.)
        anchor ('upper left'/'center'): Whether position indicates the location of the upper-left corner of this graphic
            or the center of it. (Default is 'upper left'.)
        coordinate_frame ('upper left'/'center'): Whether position is measured from the upper left corner of the parent
            graphic (x>0 is right, y>0 is down), or the center of the parent graphic (x>0 is still right, but y>0 is
            up). (Default is 'upper left'.)
        layer (int): The relative rendering order inside the parent graphic; higher layers are rendered on top. (Default
            is 0.)
        angle (float): How much to rotate the graphic by before pasting it onto the parent canvas.
        resample: cf. PIL documentation for pasting.
        parent (Graphic): The graphic onto which this graphic will be pasted. (Default is None.)
        name (str): The name by which this graphic is known to its parent. (Automatically filled on assignment to a
            parent graphic's `children`.)
        children (Children): Holds sub-graphics to be pasted onto this graphic.
        image (PIL.Image): The actual visual being rendered.
        depth (int): How many layers of parent graphics exist above this one.
    """

    size = Positive('size')
    position = TwoDee('position')
    coordinate_frame = IsOneOfThese('coordinate_frame', *ANCHOR_POSITIONS)
    anchor = IsOneOfThese('anchor', *ANCHOR_POSITIONS)

    def __init__(self, size, **kwargs):
        self.color = None
        self.position = None
        self.anchor = 'upper left'
        self.coordinate_frame = 'upper left'
        self.layer = 0
        self.angle = 0
        self.resample = 0
        self._update_attributes_from_dict(kwargs)

        self.size = size
        self.children = Children(self)
        self._image = None
        self.parent = None
        self._name = 'parent'

    @property
    def image(self):
        """The image is constructed by rendering all children on top of the graphic's own base image."""
        if self._image is None:
            self.render()
        return self._image

    @property
    def name(self):
        """The graphic name is set during assignment as a child of a parent graphic, or is just 'parent'."""
        return self._name

    @property
    def depth(self):
        """Depth measures how many graphics there are in the tree above this graphic."""
        try:
            return self.parent.depth + 1
        except AttributeError:
            return 0

    def _prepare_image(self):
        self._image = Image.new("RGBA", self.size.inttuple, self.color or '#0000')

    def save(self, fp, format=None, **params):
        self.image.save(fp, format=format, **params)

    def copy(self):
        return deepcopy(self)

    def render(self):
        if self.position is not None and self.parent is None:
            raise ValueError("Position is not None, but this graphic has no parent.")
        elif self.position is None and self.parent is not None:
            raise ValueError("Position is None, but this graphic has a parent.")
        self._prepare_image()
        self.children.render()

        if self.angle != 0:
            self._image = self.image.rotate(self.angle, resample=self.resample, expand=True)

    @staticmethod
    def clamp_to_size_tuple(values, size):
        return tuple(np.clip(values, (0, 0), size).astype(int))

    def _get_renderable_image_and_box(self, image):
        """TODO: Refactor for better encapsulation"""
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
        free_box = corner1 + corner2
        max_size = self.parent.size.inttuple
        clamped_box = self.clamp_to_size_tuple(corner1, max_size) + self.clamp_to_size_tuple(corner2, max_size)
        cropping_offset = np.array(clamped_box) - np.array(free_box)
        if np.any(cropping_offset != 0):
            cropping_box = tuple((np.array(cropping_offset) + np.array((0, 0) + image.size)).astype(int))
            image = image.crop(box=cropping_box)
        return image, clamped_box

    @staticmethod
    def to_pilarray(x):
        """
        Converts an `numpy.ndarray`-like object to a `PILArray` (which is the same, but has a method for converting
        itself to a tuple of integers).
        """
        return np.array(x).view(PILArray)

    def _update_attributes_from_dict(self, kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                raise AttributeError("{} has no attribute '{}'".format(self.name, k))


class Children:
    """
    Manages sub-graphics. Particularly, organizes the rendering behaviour so that sub-graphics with a higher layer
    value are rendered on top.

    Graphics are added as children by simple assignment, and can then later be removed by calling that child with the
    `remove()` method.

    Automatically set the `name` attribute of children on assignement to match their assignment key.

    Note:
         Layer ordering in sub-sub-graphics of two different sub-graphics don't know about each other. Any two graphics
         which need to know about each other's layer value *must* belong to the same parent graphic.

    Attributes:
        parent (Graphic): The graphic this object is tracking the children of.
        *anything else* (Graphic): The child graphics that have been assigned.
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
    def parent(self, parent):
        if self._parent is not None:
            raise ValueError("Parent is already set")
        if not isinstance(parent, Graphic):
            raise TypeError("Only Canvas objects can have graphics children, but got {}".format(type(parent)))
        self._parent = parent

    def __setattr__(self, key, value):
        if key in self.reserved_keys:
            super().__setattr__(key, value)
        else:
            if not isinstance(value, Graphic):
                raise ValueError('The children can only be graphics but got {}'.format(type(value)))
            value._name = key
            value.parent = self.parent
            value.remove = MethodType(self.child_removal, value)
            super().__setattr__(key, value)

    @staticmethod
    def child_removal(child):
        delattr(child.parent.children, child.name)

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
            cropped_image, render_box = child._get_renderable_image_and_box(child.image)
            self.parent.image.paste(cropped_image, box=render_box, mask=cropped_image)

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
        stretch (bool): Whether to expand the content to fit the largest dimension of the picture, or the smallest
            dimension of the picture. Note: if the content and the picture (or the `box`) have the same aspect ratio,
            these are the exact same thing. (Default is False, fit smallest dimension.)
    """

    def __init__(self, size, **kwargs):
        self.content = None
        self.box = None
        self.stretch = False
        super().__init__(size, **kwargs)

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

        new_size = self._rescale_to_L1_norm_with_locked_aspect_ratio(image.size, self.size, self.stretch)
        new_size = self.clamp_to_size_tuple(new_size, self.size)
        image = image.resize(new_size, resample=self.resample)

        self._image = image

    @staticmethod
    def _rescale_to_L1_norm_with_locked_aspect_ratio(to_rescale, reference, stretch=False):
        ratio = reference / np.array(to_rescale)
        if stretch:
            scale = np.amax(ratio)
        else:
            scale = np.amin(ratio)
        return np.array(to_rescale) * scale


class Text(Graphic):
    """
    A graphic for putting text in a picture. Can be added as-is or wrapped and shrunk to make a text box.

    Attributes:
        (all the attributes of a Graphic plus...)
        content (PIL.Image.Image/str): The text to use. (Default is None, but it must be provided prior to rendering.)
        font (str): The path to a font which is loadable by PIL's `ImageFont.truetype` method (e.g. '.ttf' files).
        font_size (int): The font to_rescale. (Default is 14.)
        font_color (str): The font color as a hex code or html name. (Default is 'black'.)
        font_anchor ('upper left'/'center'): Where in the graphic the font should be anchored. (Default is
            'upper left'.)
        font_offset (numpy.ndarray/tuple/list): Offset in pixels of the text. (Default is (0, 0).)
        wrap_text (bool): Whether to wrap the text (i.e. make a text box by breaking lines and automaticall shrinking
            the font) or just draw it. (Default is False, just draw it as-is.)
    """

    font_anchor = IsOneOfThese('font_anchor', *ANCHOR_POSITIONS)

    def __init__(self, size, **kwargs):
        self.font = None
        self.font_size = 14
        self.font_color = 'black'
        self.font_anchor = 'upper left'
        self.content = None
        self.wrap_text = False
        self.text_offset = np.array((0, 0))
        super().__init__(size, **kwargs)

    def _prepare_image(self):
        image = Image.new("RGBA", self.size.inttuple, self.color)
        draw = ImageDraw.Draw(image)
        if self.wrap_text:
            text, font, textsize = self._shrink_to_box(str(self.content), draw)
            draw_method = draw.multiline_text
        else:
            text = str(self.content)
            font = ImageFont.truetype(self.font, size=self.font_size)
            textsize = draw.textsize(text, font=font)
            draw_method = draw.text
        self._ensure_leq(textsize, self.size)
        xy = self._get_font_position(textsize)
        draw_method(xy, text, fill=self.font_color, font=font, anchor='L')
        self._image = image

    def _get_font_position(self, textsize):
        if self.font_anchor == 'upper left':
            pos = np.array((0, 0))
        elif self.font_anchor == 'center':
            pos = np.array((0.5 * (self.size - textsize)).inttuple)
        else:
            raise ValueError("Font anchor {} not recognized.".format(self.font_anchor))
        return tuple(pos + self.text_offset)

    @staticmethod
    def _ensure_leq(size, bounds):
        if not np.all(size <= np.array(bounds)):
            raise ValueError("{} is not always <= {}".format(size, bounds))

    @staticmethod
    def textwrap(text, width):
        return '\n'.join(textwrap(text, width=width))

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
            if wrapped_size[1] + self.text_offset[1] <= self.size[1]:
                break
            font_size -= 2
        return wrapped, font, wrapped_size

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
            if wrapped_size[0] + self.text_offset[0] <= self.size[0]:
                break
            n_lines += 1
        return wrapped, wrapped_size
