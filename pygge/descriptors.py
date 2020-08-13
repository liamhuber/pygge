# coding: utf-8
# Copyright (c) Liam Huber
# Distributed under the terms of "New BSD License", see the LICENSE file.

import numpy as np

"""
Special data descriptors.
"""

__author__ = "Liam Huber"
__copyright__ = "Copyright 2020, Liam Huber"
__version__ = "0.0"
__maintainer__ = "Liam Huber"
__email__ = "liam.huber@gmail.com"
__status__ = "development"
__date__ = "May 8, 2020"


class PILArray(np.ndarray):
    @property
    def inttuple(self):
        if len(self.shape) > 1:
            raise ValueError("Can only convert 1d PILArrays to tuples, but have shape {}".format(self.shape))
        return tuple(self.astype(int))


class MangledDescriptor:
    def __init__(self, name):
        self.name = '_{}__{}'.format(self.__class__.__name__, name)

    def __set__(self, obj, value):
        setattr(obj, self.name, value)

    def __get__(self, obj, cls):
        return getattr(obj, self.name)


class TwoDee(MangledDescriptor):
    def __set__(self, obj, value):
        if value is None:
            super().__set__(obj, value)
        else:
            arr = np.array(value)
            value = arr.view(PILArray)
            if len(value) != 2:
                raise ValueError("TwoDee values must be two-dimensional, but got {} dimensions.".format(len(value)))
            super().__set__(obj, value)


class Positive(TwoDee):
    def __set__(self, obj, value):
        super().__set__(obj, value)
        value = getattr(obj, self.name)
        if value is not None and not np.all(value > 0):
            raise ValueError("All values must be strictly greater than zero, but got {}".format(value))


class Alignment(MangledDescriptor):
    def __set__(self, obj, value):
        setattr(obj, self.name, self.LocationString(value))

    class LocationString(str):
        _ALLOWABLE = ['upper left', 'center']

        def __new__(cls, value='upper left'):
            if value not in cls._ALLOWABLE:
                raise ValueError('Location set to "{}" but expected one of: {} or "{}"'.format(
                    value,
                    ', '.join('"{}"'.format(ok) for ok in cls._ALLOWABLE[:-1]),
                    cls._ALLOWABLE[-1]
                ))
            return super().__new__(cls, value)

        @property
        def is_center(self):
            return self == 'center'

        @property
        def is_upper_left(self):
            return self == 'upper left'
