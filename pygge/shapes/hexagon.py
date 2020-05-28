# coding: utf-8
# Copyright (c) Liam Huber
# Distributed under the terms of "New BSD License", see the LICENSE file.

import numpy as np
from . shape import Shape

"""
A six-sided shape.

TODO: Add Hex2, rotated by 60 degrees.
"""

__author__ = "Liam Huber"
__copyright__ = "Copyright 2020, Liam Huber"
__version__ = "0.0"
__maintainer__ = "Liam Huber"
__email__ = "liam.huber@gmail.com"
__status__ = "development"
__date__ = "May 28, 2020"


class Hex(Shape):

    @property
    def face_angles(self):
        return {
            'n': 0,
            'nw': 60,
            'sw': 120,
            's': 180,
            'se': 240,
            'ne': 300
        }

    @property
    def face_vectors(self):
        r, h = 0.5 * self.size
        x = np.sqrt(0.75) * r * np.cos(np.deg2rad(30))
        y = np.sqrt(0.75) * r * np.sin(np.deg2rad(30))
        return self._all_values_to_pilarray({
            'n': (0, h),
            'nw': (-x, y),
            'sw': (-x, -y),
            's': (0, -h),
            'se': (x, -y),
            'ne': (x, y)
        })

    @property
    def corner_angles(self):
        return {
            'nw': 30,
            'w': 90,
            'sw': 150,
            'se': 210,
            'e': 270,
            'ne': 330
        }

    @property
    def corner_vectors(self):
        r, h = 0.5 * self.size
        x = r * np.sin(np.deg2rad(30))
        return self._all_values_to_pilarray({
            'nw': (-x, h),
            'w': (-r, 0),
            'sw': (-x, -h),
            'se': (x, -h),
            'e': (r, 0),
            'ne': (x, h),
        })

    @property
    def polygon(self):
        w, h = self.size.inttuple
        cx, cy = (0.5 * self.size).inttuple
        xl = (0.25 * self.size).inttuple[0]
        xr = (0.75 * self.size).inttuple[0]
        return (
            (xl, 0),
            (xr, 0),
            (w, cy),
            (xr, h),
            (xl, h),
            (0, cy)
        )
