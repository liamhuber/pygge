# coding: utf-8
# Copyright (c) Liam Huber
# Distributed under the terms of "New BSD License", see the LICENSE file.

import unittest
import numpy as np
from pygge.datatypes import PILArray, TwoDee, Positive


class Foo:
    td = TwoDee()
    pos = Positive()

    def __init__(self, td, pos):
        self.td = td
        self.pos = pos


class TestDatatypes(unittest.TestCase):

    def setUp(self):
        self.foo = Foo((1.1, 2.2), [3.3, 4.4])

    def test_pilarray(self):
        foo = (10*np.random.rand(3)).view(PILArray)

        self.assertTrue(np.all(isinstance(n, int) for n in foo.inttuple))
        self.assertIsInstance(2.2 * foo, PILArray)
        self.assertIsInstance(foo + np.array([1, 2, 3]), PILArray)
        self.assertIsInstance(foo + [1, 2, 3], PILArray)
        self.assertIsInstance(foo + (1, 2, 3), PILArray)

        self.assertRaises(ValueError, getattr, np.random.rand(3, 3).view(PILArray), 'inttuple')

    def test_twodee(self):
        self.assertRaises(ValueError, setattr, self.foo, 'td', [1, 2, 3])

    def test_positive(self):
        self.assertRaises(ValueError, setattr, self.foo, 'pos', [1, 2, 3])
        self.assertRaises(ValueError, setattr, self.foo, 'pos', [1, 0])
        self.assertRaises(ValueError, setattr, self.foo, 'pos', [-1, 2])
