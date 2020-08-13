# coding: utf-8
# Copyright (c) Liam Huber
# Distributed under the terms of "New BSD License", see the LICENSE file.

import unittest
from pygge.core import Graphic, Picture, Text
from pygge.descriptors import PILArray
import numpy as np
from PIL import Image
from os import remove as osremove
from os.path import dirname, join


class CanCompareImagesToArrays(unittest.TestCase):

    def assertImageMatchesArray(self, image, array):
        self.assertTrue(np.all(np.array(image) == array))


class TestGraphic(CanCompareImagesToArrays):

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
        self.assertRaises(AttributeError, Graphic, [1, 1], not_an_attribute='should_raise_error')
        self.assertRaises(ValueError, Graphic,[1, 1], anchor='not an anchor')

    def test_copy(self):
        self.graphic.render()
        g2 = self.graphic.copy()
        g2.color = 'white'
        g2.render()
        self.assertImageMatchesArray(self.graphic.image, self.ref_transparent)
        self.assertImageMatchesArray(g2.image, self.ref_white)

    def test_save(self):
        self.graphic.color = 'white'
        fname = 'tmp.png'
        self.graphic.save(fname)
        self.assertImageMatchesArray(Image.open(fname), self.ref_white)
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

    def test_crop_and_box(self):
        self.graphic.color = 'white'

        self.graphic.parent = self.parent_graphic
        self.graphic.position = (0, 0)
        self.assertEqual(self.graphic.crop_and_box()[1], (0, 0, 2, 2))

        self.graphic.coordinate_frame = 'center'
        self.assertEqual(self.graphic.crop_and_box()[1], (2, 2, 4, 4))

        self.graphic.anchor = 'center'
        self.assertEqual(self.graphic.crop_and_box()[1], (1, 1, 3, 3))

        # Ensure negative values get clipped
        self.graphic.coordinate_frame = 'upper left'
        self.assertEqual(self.graphic.crop_and_box()[1], (0, 0, 1, 1))

        # Ensure positive values get clipped
        self.oversized.parent = self.parent_graphic
        self.oversized.position = (1, 1)
        self.assertEqual(self.oversized.crop_and_box()[1], (1, 1, 5, 5))

    def test_rotation(self):
        c = Graphic((50, 50))
        g = Graphic((20, 30), color='white', anchor='center', coordinate_frame='center')
        g.parent = c
        g.position = (0, 0)

        g.angle = 45
        g.render()
        self.assertEqual(g.crop_and_box()[1], (7, 7, 43, 43))

        g.angle = -5
        g.render()
        self.assertEqual(g.crop_and_box()[1], (13, 9, 37, 41))

    def test_clamp_to_size(self):
        val1 = (-4, 5)
        val2 = (3, 3)
        size = (4, 4)
        self.assertIsInstance(self.graphic.clamp_to_size_tuple(val1, size), tuple)
        self.assertEqual(self.graphic.clamp_to_size_tuple(val1, size), (0, 4))
        self.assertEqual(self.graphic.clamp_to_size_tuple(val2, size), val2)

    def test_update_attributes_from_dict(self):
        self.graphic._update_attributes_from_dict({'color': 'green'})
        self.assertEqual(self.graphic.color, 'green')
        self.assertRaises(AttributeError, self.graphic._update_attributes_from_dict, {'notakey': 42})


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
        cls.content_color = np.array(image)[0, 0].tolist()

    @classmethod
    def tearDownClass(cls):
        osremove(cls.content)

    def setUp(self):
        self.p = Picture((200, 100))
        self.p.content = self.content

    def test_get_content_as_image(self):
        self.p.content = 42
        self.assertRaises(ValueError, self.p._get_content_as_image)
        self.p.content = 'not/a/path/to/anything'
        self.assertRaises(FileNotFoundError, self.p._get_content_as_image)

        self.p.content = Image.new('RGBA', (100, 100), 'blue')
        self.assertIsInstance(self.p._get_content_as_image(), Image.Image)
        self.p.content = self.content
        self.assertIsInstance(self.p._get_content_as_image(), Image.Image)

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
        self.assertTrue(np.all(self.p.image.size == (50, 100)))  # Content scaled down by 50% to fit inside height
        self.p.box = (0, 0, 100, 50)
        self.p.render()
        self.assertTrue(np.all(self.p.image.size == self.p.size))  # Content has same aspect ratio, so gets scaled up


class TestText(unittest.TestCase):

    lorem_ipsum = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut ' \
                  'labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris ' \
                  'nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate ' \
                  'velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non ' \
                  'proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'

    def setUp(self):
        resources_parent = dirname(dirname(__file__))
        font_path = join(resources_parent, 'resources/fonts/Roboto-Regular.ttf')
        self.t = Text((100, 20), font=font_path)
        self.t_box = Text((300, 200), font=font_path, wrap_text=True)

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
