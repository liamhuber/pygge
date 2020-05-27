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


class IsOneOfThese(MangledDescriptor):
    """Only allows the attribute to take on certain values."""
    def __init__(self, name, *args):
        super().__init__(name)
        self._allowable_values = []
        for arg in args:
            self._allowable_values.append(arg)

    def __set__(self, obj, value):
        if value is not None and value not in self._allowable_values:
            raise ValueError("Cannot set {}, it is not in {}".format(value, self._allowable_values))
        super().__set__(obj, value)
