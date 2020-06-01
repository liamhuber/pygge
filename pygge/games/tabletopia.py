# coding: utf-8
# Copyright (c) Liam Huber
# Distributed under the terms of "New BSD License", see the LICENSE file.

from PIL import Image, ImageDraw
from .. shapes import Shape, Hex, Rectangle, Ellipse
from abc import abstractmethod

"""
Methods exclusive to the [tabletopia](www.tabletopia.com) platform
"""

__author__ = "Liam Huber"
__copyright__ = "Copyright 2020, Liam Huber"
__version__ = "0.0"
__maintainer__ = "Liam Huber"
__email__ = "liam.huber@gmail.com"
__status__ = "development"
__date__ = "May 28, 2020"


def magnetic_map(shape, color='green', orientable=True, endpoint='n'):
    """
    Args:
        shape (pygge.shapes.Shape): The shape to generate a magnetic map for
        color ('green'/'blue'/'red'): Map colour. Green is no alteration, blue forces back-up, red forces front-up.
            (Default is 'green').
        orientable (bool): Whether to draw the orienting vector. (Default is True.)
        endpoint (str): Which compass direction to end the orientation line on (either a face or corner point).
            (Default is 'n'.)

    Returns:
        (PIL.Image): A Tabletopia magnetic map.
    """
    color = {'green': '#00ff00', 'red': '#ff0000', 'blue': '#0000ff'}[color]
    map_ = Image.new('RGBA', shape.size.inttuple, color=color)
    if orientable:
        draw = ImageDraw.Draw(map_)
        start = 0.5 * shape.size
        try:
            vector = shape.face_vectors[endpoint.lower()]
        except KeyError:
            vector = shape.corner_vectors[endpoint.lower()]
        end = start + vector  # TODO: Double check you don't need to reverse y coord
        draw.line(start.inttuple + end.inttuple, fill='purple', width=1)
    return shape.cut_out_shape(map_)


class Piece2d(Shape):
    """
    TODO: Borders
    """

    def __init__(self, size=None, background=None, **graphic_kwargs):
        if size is None:
            size = self.default_size
        super().__init__(size=size, **graphic_kwargs)
        if background is not None:
            self.add_background('background', content=background)

    @property
    @abstractmethod
    def default_size(self):
        raise NotImplemented


class HexTile(Hex, Piece2d):
    @property
    def default_size(self):
        return 440, 385


class Card(Rectangle, Piece2d):
    @property
    def default_size(self):
        return 440, 624


class Counter(Ellipse, Piece2d):
    @property
    def default_size(self):
        return 244, 228


class TokenHorizontal(Ellipse, Piece2d):
    @property
    def default_size(self):
        return 440, 444
