# coding: utf-8
# Copyright (c) Liam Huber
# Distributed under the terms of "New BSD License", see the LICENSE file.

import unittest
from pygge.core import Graphic


class TestGraphicAndChildren(unittest.TestCase):

    def test_instantiation(self):
        Graphic([1, 1])  # Should instantiate fine
        self.assertRaises(ValueError, Graphic, [1, 2, 3])
        self.assertRaises(ValueError, Graphic, [0, 0])

    def test_child_listing(self):
        foo = Graphic((20, 20))
        bar = Graphic((10, 10))
        baz = Graphic((5, 5))

        foo.children.b1 = bar
        foo.children.b2 = baz
        self.assertEqual(str(foo.children), "['b1', 'b2']")

        foo.children.b1.remove()
        self.assertEqual(str(foo.children), "['b2']")
