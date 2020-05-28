# coding: utf-8
# Copyright (c) Liam Huber
# Distributed under the terms of "New BSD License", see the LICENSE file.

from . shape import Shape

"""
A four-sided shape.
"""

__author__ = "Liam Huber"
__copyright__ = "Copyright 2020, Liam Huber"
__version__ = "0.0"
__maintainer__ = "Liam Huber"
__email__ = "liam.huber@gmail.com"
__status__ = "development"
__date__ = "May 28, 2020"


class Rectangle(Shape):

    @property
    def face_angles(self):
        return {
            'n': 0,
            'w': 90,
            's': 180,
            'e': 270
        }

    @property
    def face_vectors(self):
        w, h = 0.5 * self.size
        return self._all_values_to_pilarray({
            'n': (0, h),
            'w': (-w, 0),
            's': (0, -h),
            'e': (w, 0)
        })

    @property
    def corner_angles(self):
        return {
            'nw': 45,
            'sw': 135,
            'se': 225,
            'ne': 315
        }

    @property
    def corner_vectors(self):
        w, h = 0.5 * self.size
        return self._all_values_to_pilarray({
            'nw': (-w, h),
            'sw': (-w, -h),
            'se': (w, -h),
            'ne': (w, h),
        })

    @property
    def polygon(self):
        w, h = self.size.inttuple
        return (
            (0, 0),
            (w, 0),
            (w, h),
            (0, h)
        )
