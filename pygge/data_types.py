from __future__ import annotations
import numpy as np
from typing import Tuple, List
from abc import ABC, abstractmethod


def is_2d(x):
    return hasattr(x, '__len__') and len(x) == 2


class TwoTuple(ABC):
    def __init__(self, x, y=None):
        self._x = None
        self._y = None
        if is_2d(x) and y is None:
            self.x, self.y = x
        else:
            self.x = x
            self.y = y

    @property
    def x(self):
        return self._x

    @x.setter
    @abstractmethod
    def x(self, new_x):
        pass

    @property
    def y(self):
        return self._y

    @y.setter
    @abstractmethod
    def y(self, new_y):
        pass

    def __len__(self) -> int:
        return 2

    def __repr__(self):
        return f"{self.__class__.__name__}({self.x}, {self.y})"

    def __getitem__(self, item):
        if item == 0:
            return self.x
        elif item == 1:
            return self.y
        else:
            raise KeyError("Only 0 and 1 indexes (x and y) are taken")

    def __eq__(self, other):
        if is_2d(other):
            return np.isclose(other[0], self.x) and np.isclose(other[1], self.y)
        else:
            raise TypeError(f"Expected comparison to something with length 2, but got {other}")

    def __lt__(self, other):
        if is_2d(other):
            return np.array([self.x < other[0], self.y < other[1]])
        else:
            raise TypeError(f"Expected comparison to something with length 2, but got {other}")

    def __le__(self, other):
        if is_2d(other):
            return np.array([self.x <= other[0], self.y <= other[1]])
        else:
            raise TypeError(f"Expected comparison to something with length 2, but got {other}")

    def __gt__(self, other):
        if is_2d(other):
            return np.array([self.x > other[0], self.y > other[1]])
        else:
            raise TypeError(f"Expected comparison to something with length 2, but got {other}")

    def __ge__(self, other):
        if is_2d(other):
            return np.array([self.x >= other[0], self.y >= other[1]])
        else:
            raise TypeError(f"Expected comparison to something with length 2, but got {other}")


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

    def astuple(self) -> Tuple:
        return self.x, self.y

    def asarray(self) -> np.ndarray:
        return np.array([self.x, self.y])

    def aslist(self) -> List:
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


class Float2d(TwoTuple):

    @TwoTuple.x.setter
    def x(self, new_x):
        self._x = float(new_x)

    @TwoTuple.y.setter
    def y(self, new_y):
        self._y = float(new_y)


class Int2d(TwoTuple):
    @TwoTuple.x.setter
    def x(self, new_x):
        self._x = int(new_x)

    @TwoTuple.y.setter
    def y(self, new_y):
        self._y = int(new_y)


class Positive(TwoTuple, ABC):
    @staticmethod
    def _is_positive(x):
        if np.any(x <= 0):
            raise ValueError(f"Only strictly positive values allowed, but got {x}")

    @classmethod
    def is_positive(cls, fnc):
        def wrapper(self, x):
            cls._is_positive(x)
            return fnc(self, x)

        return wrapper


class PositiveFloat(Float2d, Positive):
    @Float2d.x.setter
    @Positive.is_positive
    def x(self, new_x):
        self._x = float(new_x)

    @Float2d.y.setter
    @Positive.is_positive
    def y(self, new_y):
        self._y = float(new_y)


class PositiveInt(Int2d, Positive):
    @Int2d.x.setter
    @Positive.is_positive
    def x(self, new_x):
        self._x = int(new_x)

    @Int2d.y.setter
    @Positive.is_positive
    def y(self, new_y):
        self._y = int(new_y)
