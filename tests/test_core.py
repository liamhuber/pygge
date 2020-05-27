# coding: utf-8
# Copyright (c) Liam Huber
# Distributed under the terms of "New BSD License", see the LICENSE file.

import unittest
from pygge.core import Graphic, Picture, Text
from pygge.descriptors import PILArray
import numpy as np
from PIL import Image
from os import remove as osremove


class CanCompareImagesToArrays(unittest.TestCase):

    def assertImageMatchesArray(self, image, array):
        self.assertTrue(np.all(np.array(image) == array))


class TestCanvas(CanCompareImagesToArrays):

    def setUp(self):
        self.graphic = Graphic((2, 2))
        self.parent_graphic = Graphic((5, 5))
        self.oversized = Graphic((self.parent_graphic.size + 5).inttuple, color='black')

        np_size = self.graphic.size.inttuple + (4,)  # Final dim is RBGA
        self.ref_transparent = np.zeros(np_size)
        self.ref_white = np.ones(np_size) * 255
        self.ref_black = np.zeros(np_size)
        self.ref_black[..., -1] = 255

    def test_init(self):
        self.assertRaises(ValueError, Graphic, [1, 2, 3])
        self.assertRaises(ValueError, Graphic, [0, 0])

    def test_copy(self):
        c1 = Graphic((2, 2))
        c1.render()
        c2 = c1.copy()
        c2.color = 'white'
        c2.render()
        self.assertImageMatchesArray(c1.image, self.ref_transparent)
        self.assertImageMatchesArray(c2.image, self.ref_white)

    def test_save(self):
        c1 = Graphic((2, 2), color='white')
        fname = 'tmp.png'
        c1.save(fname)
        img = Image.open(fname)
        self.assertImageMatchesArray(img, self.ref_white)
        osremove(fname)

    def test_to_pilarray(self):
        for data in [(1, 2), [1, 2], np.array([1, 2])]:
            self.assertIsInstance(Graphic.to_pilarray(data), PILArray)

    def test_render(self):
        # Starts transparent
        self.assertImageMatchesArray(self.graphic.image, self.ref_transparent)

        # Can set color if we re-render
        self.graphic.color = '#ffff'
        self.assertImageMatchesArray(self.graphic.image, self.ref_transparent)  # Shouldn't update just by setting color
        self.graphic.render()
        self.assertImageMatchesArray(self.graphic.image, self.ref_white)

        # Can set html color names too
        self.graphic.color = 'black'
        self.graphic.render()
        self.assertImageMatchesArray(self.graphic.image, self.ref_black)

        # Can't render if exactly one of parent and position is None
        self.graphic.position = (1, 1)
        self.assertRaises(ValueError, self.graphic.render)  # Only position set
        self.graphic.parent = self.parent_graphic
        self.graphic.render()  # Both set
        self.graphic.position = None
        self.assertRaises(ValueError, self.graphic.render)  # Only parent set

        # Can't render children bigger than their parents
        self.parent_graphic.children.oversize = self.oversized
        self.assertRaises(ValueError, self.parent_graphic.render)

    def test_render_box(self):
        self.graphic.color = 'white'
        image = self.graphic.image

        self.graphic.parent = self.parent_graphic
        self.graphic.position = (0, 0)
        self.assertEqual(self.graphic._get_render_box(image), (0, 0, 2, 2))

        self.graphic.coordinate_frame = 'center'
        self.assertEqual(self.graphic._get_render_box(image), (2, 2, 4, 4))

        self.graphic.anchor = 'center'
        self.assertEqual(self.graphic._get_render_box(image), (1, 1, 3, 3))

        # Ensure negative values get clipped
        self.graphic.coordinate_frame = 'upper left'
        self.assertEqual(self.graphic._get_render_box(image), (0, 0, 1, 1))

        # Ensure positive values get clipped
        oversized_image = self.oversized.image
        self.oversized.parent = self.parent_graphic
        self.oversized.position = (1, 1)
        self.assertEqual(self.oversized._get_render_box(oversized_image), (1, 1, 5, 5))

    def test_rotation_renderbox(self):
        c = Graphic((50, 50))
        g = Graphic((20, 30), color='white', anchor='center', coordinate_frame='center')

        g.angle = 45
        image45 = g.image
        g.angle = -5
        g.render()
        image5 = g.image

        g.parent = c
        g.position = (0, 0)

        self.assertEqual(g._get_render_box(image45), (7, 7, 43, 43))
        self.assertEqual(g._get_render_box(image5), (13, 9, 37, 41))

    def test_clamp_to_size(self):
        val1 = (-4, 5)
        val2 = (3, 3)
        size = (4, 4)
        self.assertIsInstance(self.graphic.clamp_to_size_tuple(val1, size), tuple)
        self.assertEqual(self.graphic.clamp_to_size_tuple(val1, size), (0, 4))
        self.assertEqual(self.graphic.clamp_to_size_tuple(val2, size), val2)


class TestChildren(CanCompareImagesToArrays):

    def setUp(self):
        self.parent_graphic = Graphic((3, 3))
        self.g1 = Graphic((2, 2))
        self.g2 = Graphic((1, 1))

    def test_child_listing(self):
        self.parent_graphic.children.g1 = self.g1
        self.parent_graphic.children.g2 = self.g2
        self.assertEqual(str(self.parent_graphic.children), "['g1', 'g2']")
        self.assertEqual(len(self.parent_graphic.children), 2)

        self.parent_graphic.children.g1.remove()
        self.assertEqual(str(self.parent_graphic.children), "['g2']")
        self.assertEqual(len(self.parent_graphic.children), 1)

    def test_depth(self):
        self.g1.children.g2 = self.g2
        self.parent_graphic.children.g1 = self.g1
        self.assertEqual(self.g2.depth, 2)
        self.assertEqual(self.g1.depth, 1)
        self.assertEqual(self.parent_graphic.depth, 0)

    def test_render(self):
        # Ensure that the images are ordered according to their layer values
        self.parent_graphic.children.g2 = self.g2
        self.g2.color = 'black'
        self.g2.position = (2, 2)
        self.g2.layer = 2

        self.parent_graphic.children.g1 = self.g1
        self.g1.color = 'white'
        self.g1.position = (1, 1)
        self.g1.layer = 1

        self.assertImageMatchesArray(self.parent_graphic.image, np.array([
           [[0, 0, 0, 0],  # Large transparent L
            [0, 0, 0, 0],
            [0, 0, 0, 0]],

           [[0, 0, 0, 0],
            [255, 255, 255, 255],  # Medium white L
            [255, 255, 255, 255]],

           [[0, 0, 0, 0],
            [255, 255, 255, 255],
            [0, 0, 0, 255]]  # Single pixel of black in the corner
        ]))

        self.g1.layer = 2
        self.g2.layer = 1
        self.parent_graphic.render()
        self.assertImageMatchesArray(self.parent_graphic.image, np.array([
            [[0, 0, 0, 0],
             [0, 0, 0, 0],
             [0, 0, 0, 0]],

            [[0, 0, 0, 0],
             [255, 255, 255, 255],
             [255, 255, 255, 255]],

            [[0, 0, 0, 0],
             [255, 255, 255, 255],
             [255, 255, 255, 255]]  # White covers over black now
        ]))


class TestPicture(unittest.TestCase):

    content = 'picture.png'

    @classmethod
    def setUpClass(cls):
        image = Image.new('RGBA', (100, 200), 'green')
        image.save(cls.content)

    @classmethod
    def tearDownClass(cls):
        osremove('picture.png')

    def setUp(self):
        self.p = Picture((200, 100))
        self.p.content = self.content

    def test_ensure_image(self):
        self.assertRaises(ValueError, self.p._ensure_image, 42)
        self.assertRaises(FileNotFoundError, self.p._ensure_image, 'not_a_path_to_anything')

        self.assertIsInstance(self.p._ensure_image(Image.new('RGBA', (100, 100), 'blue')), Image.Image)
        self.assertIsInstance(self.p._ensure_image(self.content), Image.Image)

    def test_rescale_with_locked_aspect_ratio(self):
        base_size = self.p.size
        diff_scale = max(1, int(base_size[0] * 0.1))
        diff = np.array((diff_scale, diff_scale))
        rescale = self.p._rescale_to_L1_norm_with_locked_aspect_ratio

        for m in [
            (-1, -1),
            (-1, 0),
            (0, -1),
            (1, -1),
            (-1, 1),
            (0, 1),
            (1, 0),
            (1, 1),
        ]:
            to_scale = base_size + m*diff
            rescaled = rescale(to_scale, base_size)

            self.assertTrue(np.all(rescaled <= base_size))
            self.assertAlmostEqual(to_scale[0]/to_scale[1], rescaled[0]/rescaled[1])

    def test_prepare_image(self):
        img = self.p.image
        self.assertTrue(np.all(img.size <= self.p.size))
        self.assertGreaterEqual(np.sum(img.size == self.p.size), 1)


class TestText(unittest.TestCase):

    lorem_ipsum = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut ' \
                  'labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris ' \
                  'nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate ' \
                  'velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non ' \
                  'proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'

    def setUp(self):
        self.t = Text((100, 20), font='../resources/fonts/Roboto-Regular.ttf')
        self.t_box = Text((300, 200), font='../resources/fonts/Roboto-Regular.ttf', wrap_text=True)

    def test_font_anchor(self):
        self.t.font_anchor = 'center'
        self.t.font_anchor = 'upper left'
        self.assertRaises(ValueError, setattr, self.t, 'font_anchor', 'NOT_AN_ANCHOR')

    def test_ensure_leq(self):
        self.t._ensure_leq((1, 2), (3, 4))
        self.assertRaises(ValueError, self.t._ensure_leq, (3, 4), (1, 2))

    def test_get_font_position(self):
        self.assertEqual(self.t._get_font_position((100, 20)), (0, 0))
        self.t.font_anchor = 'center'
        self.assertEqual(self.t._get_font_position((102, 22)), (-1, -1))

    def test_prepare_image(self):
        self.t.content = 'Some text'
        self.assertIsInstance(self.t.image, Image.Image)
        self.t.font_size = 30
        self.assertRaises(ValueError, self.t.render)

        self.t_box.content = self.lorem_ipsum
        self.assertIsInstance(self.t_box.image, Image.Image)
        self.t_box.font_size = 30
        self.t_box.render()
        self.assertIsInstance(self.t_box.image, Image.Image)
