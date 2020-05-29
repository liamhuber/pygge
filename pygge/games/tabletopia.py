# coding: utf-8
# Copyright (c) Liam Huber
# Distributed under the terms of "New BSD License", see the LICENSE file.

from PIL import Image, ImageDraw

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
