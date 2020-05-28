# coding: utf-8
# Copyright (c) Liam Huber
# Distributed under the terms of "New BSD License", see the LICENSE file.

from . ellipse import Ellipse
from . square import Square

"""
A perfectly round shape, where faces and corners have the same meaning.
"""

__author__ = "Liam Huber"
__copyright__ = "Copyright 2020, Liam Huber"
__version__ = "0.0"
__maintainer__ = "Liam Huber"
__email__ = "liam.huber@gmail.com"
__status__ = "development"
__date__ = "May 28, 2020"


class Circle(Ellipse, Square):
    # Ellipse for the angles, vectors, and polygon, square for the definition of size
    pass
