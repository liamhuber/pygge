# coding: utf-8
# Copyright (c) Liam Huber
# Distributed under the terms of "New BSD License", see the LICENSE file.

from . shape import Shape
import numpy as np

"""
A rounded shape, where faces and corners have the same meaning.
"""

__author__ = "Liam Huber"
__copyright__ = "Copyright 2020, Liam Huber"
__version__ = "0.0"
__maintainer__ = "Liam Huber"
__email__ = "liam.huber@gmail.com"
__status__ = "development"
__date__ = "May 28, 2020"


class Ellipse(Shape):

    curve_resolution = 10000

    @property
    def face_angles(self):
        return {
            'n': 0,
            'w': 90,
            's': 180,
            'e': 270,
            'nw': 45,
            'sw': 135,
            'se': 225,
            'ne': 315
        }

    @property
    def face_vectors(self):
        w, h = 0.5 * self.size
        return self._all_values_to_pilarray({
            'n': (0, h),
            'w': (-w, 0),
            's': (0, -h),
            'e': (w, 0),
            'nw': (-w, h),
            'sw': (-w, -h),
            'se': (w, -h),
            'ne': (w, h),
        })

    @property
    def corner_angles(self):
        return self.face_angles

    @property
    def corner_vectors(self):
        return self.face_vectors

    @property
    def polygon(self):
        w, h = self.size.inttuple
        return tuple([
            (int(0.5 * w * (1 + np.sin(theta))), int(0.5 * h * (1 + np.cos(theta))))
            for theta in np.linspace(start=0, stop=2*np.pi, num=self.curve_resolution, endpoint=False)
        ])
