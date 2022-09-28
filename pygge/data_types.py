# coding: utf-8
# Copyright (c) Liam Huber
# Distributed under the terms of "New BSD License", see the LICENSE file.

import numpy as np


def is_2d(x):
    return hasattr(x, '__len__') and len(x) == 2


class TwoTuple:
    """
    In principle, works as a two-length tuple with any two elements, but comes with a bunch of bells and whistles to do
    math with other two-length objects as long as this object and that object both have scalar elements.
    """
    def __init__(self, x, y=None):
        if y is None:
            if is_2d(x):
                self._x, self._y = x
            else:
                raise TypeError(f"Expected x to be 2D when y is None, but got {x}")
        else:
            self._x = x
            self._y = y

        self._setting_error = TypeError("Cannot set components individually.")

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, new_x):
        raise self._setting_error

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, new_y):
        raise self._setting_error

    def __getitem__(self, item):
        if item == 0:
            return self.x
        elif item == 1:
            return self.y
        else:
            raise KeyError("Only 0 and 1 indexes (x and y) are taken")

    def __setitem__(self, key, value):
        raise self._setting_error

    def __len__(self) -> int:
        return 2

    def __repr__(self):
        return f"({self.x}, {self.y})"

    def __eq__(self, other):
        if is_2d(other):
            return np.isclose(other[0], self.x) and np.isclose(other[1], self.y)
        else:
            raise TypeError(f"Expected comparison to something with length 2, but got {other}")

    def __lt__(self, other):
        if is_2d(other):
            return np.array([self.x < other[0], self.y < other[1]])
        else:
            return self.x < other and self.y < other

    def __le__(self, other):
        if is_2d(other):
            return np.array([self.x <= other[0], self.y <= other[1]])
        else:
            return self.x <= other and self.y <= other

    def __gt__(self, other):
        if is_2d(other):
            return np.array([self.x > other[0], self.y > other[1]])
        else:
            return self.x > other and self.y > other

    def __ge__(self, other):
        if is_2d(other):
            return np.array([self.x >= other[0], self.y >= other[1]])
        else:
            return self.x >= other and self.y >= other

    def __add__(self, other):
        if is_2d(other):
            return self.__class__(self.x + other[0], self.y + other[1])
        else:
            return self.__class__(self.x + other, self.y + other)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if is_2d(other):
            return self.__class__(self.x - other[0], self.y - other[1])
        else:
            return self.__class__(self.x - other, self.y - other)

    def __rsub__(self, other):
        if is_2d(other):
            return self.__class__(other[0] - self.x, other[1] - self.y)
        else:
            return self.__class__(other - self.x, other - self.y)

    def __mul__(self, other):
        if is_2d(other):
            return self.__class__(self.x * other[0], self.y * other[1])
        else:
            other = float(other)
            return self.__class__(self.x * other, self.y * other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if is_2d(other):
            return self.__class__(self.x / other[0], self.y / other[1])
        else:
            other = float(other)
            return self.__class__(self.x / other, self.y / other)

    def __rtruediv__(self, other):
        if is_2d(other):
            return self.__class__(other[0] / self.x, other[1] / self.y)
        else:
            other = float(other)
            return self.__class__(other / self.x, other / self.y)

    def __floordiv__(self, other):
        if is_2d(other):
            return self.__class__(self.x // other[0], self.y // other[1])
        else:
            other = float(other)
            return self.__class__(self.x // other, self.y // other)

    def astuple(self) -> tuple:
        return self.x, self.y

    def asarray(self) -> np.ndarray:
        return np.array([self.x, self.y])

    def aslist(self) -> list:
        return [self.x, self.y]

    def clamp(self, min_=None, max_=None):
        if min_ is None and max_ is None:
            raise ValueError("Please provide at least one of min_ or max_ clamp values")
        clamped = self.astuple()
        if min_ is not None:
            clamped = (max(clamped[0], min_[0]), max(clamped[1], min_[1]))
        if max_ is not None:
            clamped = (min(clamped[0], max_[0]), min(clamped[1], max_[1]))
        return self.__class__(clamped)
