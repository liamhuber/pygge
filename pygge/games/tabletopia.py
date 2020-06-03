# coding: utf-8
# Copyright (c) Liam Huber
# Distributed under the terms of "New BSD License", see the LICENSE file.

from PIL import Image, ImageDraw
from .. shapes import Shape, Hex, Rectangle, Ellipse
from abc import abstractmethod
import numpy as np

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


class TileMap(Rectangle):

    def __init__(self, default_tile, located_tiles, dimension, spacing=10, **graphic_kwargs):
        self.spacing = spacing
        self.default_tile = default_tile
        if 'size' in graphic_kwargs.keys():
            raise AttributeError("Size was found in kwargs, but is set automatically here.")
        map_size = self._dimension_to_size(dimension)
        super().__init__(map_size, **graphic_kwargs)

        occupied_locations = []
        for tile, locations in located_tiles:
            for location in locations:
                self._add_tile(tile, location)
                occupied_locations.append(location)

        for m in np.arange(dimension[0]):
            for n in np.arange(dimension[1]):
                if (m, n) not in occupied_locations:
                    self._add_tile(default_tile, (m, n))

    @abstractmethod
    def _dimension_to_size(self, dimension):
        raise NotImplementedError

    @abstractmethod
    def _location_to_position(self, location):
        raise NotImplementedError

    def _add_tile(self, tile, location):
        # self.add_picture(
        #     'tile_{}_{}'.format(*location),
        #     tile.size,
        #     position=self._location_to_position(location),
        #     content=tile.image
        # )
        self.add_graphic(tile.copy(), 'tile_{}_{}'.format(*location), position=self._location_to_position(location))

    def get_magnetic_map(self):
        pass


class HexMap(TileMap):
    def _dimension_to_size(self, dimension):
        return (self.default_tile.size + self.spacing) * (np.array(dimension) * [0.75, 1] + [0.5, 0.5])

    def _location_to_position(self, location):
        dx = 0.75 * self.default_tile.size[0] + self.spacing
        x0 = self.spacing
        dy = self.default_tile.size[1] + self.spacing
        y0 = np.array([0, 0.5]) * self.default_tile.size[1] + self.spacing
        m, n = location
        return np.array([m * dx + x0, n * dy + y0[m % 2]])


class SquareMap(TileMap):

    def _dimension_to_size(self, dimension):
        return dimension * (self.default_tile.size + self.spacing)

    def _location_to_position(self, location):
        return location * (self.default_tile.size + self.spacing) + 0.5 * self.spacing
