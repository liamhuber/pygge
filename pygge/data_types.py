import numpy as np


def _is_2d(x):
    return hasattr(x, '__len__') and len(x) == 2


def _is_positive(x):
    if np.any(x <= 0):
        raise ValueError(f"Only strictly positive values allowed, but got {x}")


def is_positive(fnc):
    def wrapper(self, x):
        _is_positive(x)
        return fnc(self, x)
    return wrapper


class Float2d:
    def __init__(self, x, y=None):
        self._x = None
        self._y = None
        if _is_2d(x) and y is None:
            self.x, self.y = x
        else:
            self.x = x
            self.y = y

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, new_x):
        self._x = float(new_x)

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, new_y):
        self._y = float(new_y)

    def __len__(self):
        return 2

    def __repr__(self):
        return f"TwoDee({self.x}, {self.y})"

    def __getitem__(self, item):
        if item == 0:
            return self.x
        elif item == 1:
            return self.y
        else:
            raise KeyError("Only 0 and 1 indexes (x and y) are taken")

    def __eq__(self, other):
        if _is_2d(other):
            return np.isclose(other[0], self.x) and np.isclose(other[1], self.y)
        else:
            raise TypeError(f"Expected comparison to something with length 2, but got {other}")

    def __add__(self, other):
        if _is_2d(other):
            return self.__class__(self.x + other[0], self.y + other[1])
        else:
            return self.__class__(self.x + other, self.y + other)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if _is_2d(other):
            return self.__class__(self.x - other[0], self.y - other[1])
        else:
            return self.__class__(self.x - other, self.y - other)

    def __rsub__(self, other):
        if _is_2d(other):
            return self.__class__(other[0] - self.x, other[1] - self.y)
        else:
            return self.__class__(other - self.x, other - self.y)

    def __mul__(self, other):
        if _is_2d(other):
            return self.__class__(self.x * other[0], self.y * other[1])
        else:
            other = float(other)
            return self.__class__(self.x * other, self.y * other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if _is_2d(other):
            return self.__class__(self.x / other[0], self.y / other[1])
        else:
            other = float(other)
            return self.__class__(self.x / other, self.y / other)

    def __rtruediv__(self, other):
        if _is_2d(other):
            return self.__class__(other[0] / self.x, other[1] / self.y)
        else:
            other = float(other)
            return self.__class__(other / self.x, other / self.y)

    def __floordiv__(self, other):
        if _is_2d(other):
            return self.__class__(self.x // other[0], self.y // other[1])
        else:
            other = float(other)
            return self.__class__(self.x // other, self.y // other)


class Positive(Float2d):
    @Float2d.x.setter
    @is_positive
    def x(self, new_x):
        self._x = float(new_x)

    @Float2d.y.setter
    @is_positive
    def y(self, new_y):
        self._y = float(new_y)