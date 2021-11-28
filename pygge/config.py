# coding: utf-8
# Copyright (c) Liam Huber
# Distributed under the terms of "New BSD License", see the LICENSE file.

from abc import ABCMeta
from pathlib import Path
from typing import Union

"""
From here default starting paths for the assets and output can be specified which are globally available for this 
python instance.
"""

__author__ = "Liam Huber"
__copyright__ = "Copyright 2021, Liam Huber"
__maintainer__ = "Liam Huber"
__email__ = "liam.huber@gmail.com"
__status__ = "development"
__date__ = "Nov 28, 2021"


class Singleton(ABCMeta):
    """
    Implemented with suggestions from
    http://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Config(metaclass=Singleton):
    def __init__(self):
        self._assets = None
        self._out = None
        self.out = Path('./out').expanduser().resolve().absolute()

    @staticmethod
    def ensure_directory(path: str) -> Union[Path, None]:
        if path is None:
            return None
        else:
            path = Path(path).expanduser().resolve().absolute()
            if path.is_file():
                raise ValueError(f'{path} exists and is a file.')
            path.mkdir(exist_ok=True)
            return path

    @property
    def assets(self) -> Path:
        """Root path for reading assets."""
        return self._assets

    @assets.setter
    def assets(self, new_path: str):
        self._assets = self.ensure_directory(new_path)

    @property
    def out(self) -> Path:
        """Root path for saving images."""
        return self._out

    @out.setter
    def out(self, new_path: str):
        self._out = self.ensure_directory(new_path)


config = Config()
