# coding: utf-8
# Copyright (c) Liam Huber
# Distributed under the terms of "New BSD License", see the LICENSE file.

from . rectangle import Rectangle
from .. descriptors import Positive

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


class Square(Rectangle):

    _size = Positive('_size')

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, new_size):
        if hasattr(new_size, '__len__'):
            if new_size[0] != new_size[1]:
                raise ValueError("Squares must have equal side lengths, but got a size of {}".format(new_size))
            else:
                self._size = new_size
        else:
            self._size = (new_size, new_size)
