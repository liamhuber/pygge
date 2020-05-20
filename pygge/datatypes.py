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


class TwoDee:
    def __get__(self, instance, cls):
        if not hasattr(instance, '_twodee_value'):
            return
        return instance._twodee_value

    def __set__(self, instance, value):
        if value is None:
            instance._twodee_value = None
        else:
            arr = np.array(value)
            value = arr.view(PILArray)
            if len(value) != 2:
                raise ValueError("Sizes must be two-dimensional, but got {} dimensions.".format(len(value)))
            instance._twodee_value = value


class Positive:
    def __get__(self, instance, cls):
        if not hasattr(instance, '_positive_value'):
            return
        return instance._positive_value

    def __set__(self, instance, value):
        if value is None:
            instance._positive_value = None
        else:
            arr = np.array(value)
            value = arr.view(PILArray)
            if len(value) != 2:
                raise ValueError("Sizes must be two-dimensional, but got {} dimensions.".format(len(value)))
            if not np.all(value > 0):
                raise ValueError("Sizes must be strictly greater than zero, but got {}".format(value))
            instance._positive_value = value
