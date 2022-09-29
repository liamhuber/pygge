# coding: utf-8
# Copyright (c) Liam Huber
# Distributed under the terms of "New BSD License", see the LICENSE file.
from __future__ import annotations

from pygge.data_types import is_2d, TwoTuple
from traitlets import TraitType
from abc import ABC, abstractmethod
import numpy as np
from PIL import Image
from pathlib import Path


class TwoTuppleTrait(TraitType, ABC):
    def validate(self, obj, value):
        if is_2d(value):
            try:
                return TwoTuple(self._cast_value(value))
            except TypeError:
                self.error(obj, value)
        self.error(obj, value)

    @abstractmethod
    def _cast_value(self, value):
        pass


class Int2d(TwoTuppleTrait):
    info_text = "A two-tuple of integers"
    default_value = (0, 0)

    def _cast_value(self, value):
        return int(value[0]), int(value[1])


class Float2d(TwoTuppleTrait):
    info_text = "A two-tuple of floats"
    default_value = (0., 0.)

    def _cast_value(self, value):
        return float(value[0]), float(value[1])


class PositiveInt(Int2d):
    info_text = "A two-tuple of positive integers"
    default_value = (1, 1)

    @staticmethod
    def _is_positive(value):
        if np.any(np.array(value) <= 0):
            raise ValueError(f"Only strictly positive values allowed, but got {value}")

    def _cast_value(self, value):
        self._is_positive(value)
        return super()._cast_value(value)


class ImageTrait(TraitType):
    info_text = "The image"
    allow_none = True
    default_value = None

    def validate(self, obj, value):
        if isinstance(value, Image.Image):
            return value
        self.error(obj, value)

    def from_string(self, s):
        if self.allow_none and s == "None":
            return None
        return Image.open(s)


class FileTrait(TraitType):
    def validate(self, obj, value):
        if Path(value).is_file():
            return value
        self.error(obj, value)


class FlagTrait(TraitType, ABC):
    def validate(self, obj, value):
        if value in self.allowables:
            return value
        self.error(obj, value)

    @property
    @abstractmethod
    def allowables(self) -> list[str]:
        pass


class Anchor(FlagTrait):
    default_value = "upper left"

    @property
    def allowables(self) -> list[str]:
        return ["upper left"]


class CoordinateFrame(FlagTrait):
    default_value = "upper left"

    @property
    def allowables(self) -> list[str]:
        return ["upper left", "center"]


class FontTrait(FileTrait):
    default_value = str(Path(f"{__file__}").absolute().parent.parent.joinpath("resources/fonts/Roboto-Regular.ttf"))

    def validate(self, obj, value):
        value = self.default_value if value is None else value
        return super().validate(obj, value)
