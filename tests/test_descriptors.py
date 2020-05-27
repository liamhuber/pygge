# coding: utf-8
# Copyright (c) Liam Huber
# Distributed under the terms of "New BSD License", see the LICENSE file.

import unittest
import numpy as np
from pygge.descriptors import PILArray, MangledDescriptor, TwoDee, Positive, IsOneOfThese


class Foo:
    man1 = MangledDescriptor('man1')
    man2 = MangledDescriptor('man2')
    td = TwoDee('td')
    pos = Positive('pos')
    allowable_values = [1, '2', [3, 4, 5], 'foo']
    isone = IsOneOfThese('isone', *allowable_values)

    def __init__(self, td=None, td2=None, pos=None, isone=None):
        self.td = td
        self.td2 = td2
        self.pos = pos
        self.isone = isone


class TestDescriptors(unittest.TestCase):

    def setUp(self):
        self.foo = Foo()

    def test_pilarray(self):
        r = (10*np.random.rand(3)).view(PILArray)

        # Make sure math casting works
        self.assertTrue(np.all(isinstance(n, int) for n in r.inttuple))
        self.assertIsInstance(2.2 * r, PILArray)
        self.assertIsInstance(r + np.array([1, 2, 3]), PILArray)
        self.assertIsInstance(r + [1, 2, 3], PILArray)
        self.assertIsInstance(r + (1, 2, 3), PILArray)

        self.assertRaises(ValueError, getattr, np.random.rand(3, 3).view(PILArray), 'inttuple')  # Wrong shape

    def test_mangled_descriptor(self):
        # Ensure descriptor can be used multiple times on multiple instances without overwriting itself
        self.bar = Foo()

        self.foo.man1 = 'f1'
        self.foo.man2 = 'f2'
        self.bar.man1 = 'b1'

        self.assertEqual(self.foo.man1, 'f1')
        self.assertEqual(self.foo.man2, 'f2')
        self.assertEqual(self.bar.man1, 'b1')

    def test_twodee(self):
        td = TwoDee('name')
        td = [1, 2]
        self.assertRaises(ValueError, setattr, self.foo, 'td', [1, 2, 3])  # Too long

    def test_positive(self):
        pos = Positive('name')
        pos = [1, 2]
        self.assertRaises(ValueError, setattr, self.foo, 'pos', [1, 2, 3])  # Too long
        self.assertRaises(ValueError, setattr, self.foo, 'pos', [1, 0])  # Has a zero
        self.assertRaises(ValueError, setattr, self.foo, 'pos', [-1, 2])  # Has a negative

    def test_isoneofthese(self):
        for v in self.foo.allowable_values:
            self.foo.isone = v
        self.assertRaises(ValueError, setattr, self.foo, 'isone', 'not_allowed')
        self.assertRaises(ValueError, setattr, self.foo, 'isone', 'FOO')  # Wrong case
