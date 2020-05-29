# coding: utf-8
# Copyright (c) Liam Huber
# Distributed under the terms of "New BSD License", see the LICENSE file.

import numpy as np
from pygge.core import Graphic, Text, Picture
from abc import abstractmethod
from PIL import Image, ImageDraw

from pygge.descriptors import Positive

"""
Convenience base class for making graphics with particular geometric shapes.
"""

__author__ = "Liam Huber"
__copyright__ = "Copyright 2020, Liam Huber"
__version__ = "0.0"
__maintainer__ = "Liam Huber"
__email__ = "liam.huber@gmail.com"
__status__ = "development"
__date__ = "May 27, 2020"


class Shape(Graphic):

    @property
    @abstractmethod
    def face_angles(self):
        """A dictionary mapping compass directions for each edge to a rotation in degrees"""
        raise NotImplementedError

    @property
    @abstractmethod
    def face_vectors(self):
        """
        A dictionary mapping compass directions for each edge to the vector from the center of the shape to the middle
        of that face.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def corner_angles(self):
        """A dictionary mapping compass directions for each corner to a rotation in degrees"""
        raise NotImplementedError

    @property
    @abstractmethod
    def corner_vectors(self):
        """
        A dictionary mapping compass directions for each corner to the vector from the center of the shape to that
        corner.
        """
        raise NotImplementedError

    def _all_values_to_pilarray(self, dict_of_tuples):
        # TODO: Refactor as decorator?
        pil_dict = {}
        for k, v in dict_of_tuples.items():
            pil_dict[k] = self.to_pilarray(v)
        return pil_dict

    @property
    @abstractmethod
    def polygon(self):
        """A tuple of coordinates giving the polygon of the shape."""
        raise NotImplementedError

    def _mapped_angle(self, angle):
        """Accepts either floats or compass directions as angles"""
        if isinstance(angle, str):
            try:
                return self.face_angles[angle.lower()]
            except KeyError:
                return self.corner_angles[angle.lower()]
        else:
            return angle

    def render(self):
        super().render()
        self._image = self.cut_out_shape(self.image)

    def cut_out_shape(self, image):
        mask = Image.new('RGBA', self.size.inttuple)
        draw = ImageDraw.Draw(mask)
        draw.polygon(self.polygon, fill='#000')
        cut_image = Image.new('RGBA', self.size.inttuple)
        cut_image.paste(image, mask=mask)
        return cut_image

    def add_graphic(self, graphic, name, **graphic_kwargs):
        if isinstance(graphic, Graphic):
            graphic._update_attributes_from_dict(graphic_kwargs)
        else:
            graphic = graphic(**graphic_kwargs)
        setattr(self.children, name, graphic)

    @staticmethod
    def _augment_kwargs(kwargs, new_kwargs, exclusive=True):
        for k, v in new_kwargs.items():
            if k in kwargs.keys() and exclusive:
                raise ValueError("'{}' is already defined and cannot be reset.".format(k))
            else:
                kwargs[k] = v
        return kwargs

    def add_centered_graphic(self, graphic, name, **graphic_kwargs):
        graphic_kwargs = self._augment_kwargs(graphic_kwargs, {'anchor': 'center', 'coordinate_frame': 'center'})
        self.add_graphic(graphic, name, **graphic_kwargs)

    def add_graphic_to_center(self, graphic, name, **graphic_kwargs):
        graphic_kwargs = self._augment_kwargs(graphic_kwargs, {'position': (0, 0)})
        self.add_centered_graphic(graphic, name, **graphic_kwargs)

    def add_graphic_to_face(self, graphic, name, face, buffer=0, **graphic_kwargs):
        angle = self.face_angles[face] + 180  # 180 so it's read from that face
        full_vector = self.face_vectors[face]
        unit_vector = full_vector / np.linalg.norm(full_vector)
        position = full_vector - buffer * unit_vector
        graphic_kwargs = self._augment_kwargs(graphic_kwargs, {'position': position, 'angle': angle})
        self.add_centered_graphic(graphic, name, **graphic_kwargs)

    def add_graphic_to_corner(self, graphic, name, face, buffer=0, **graphic_kwargs):
        angle = self.corner_angles[face] + 180  # 180 so it's read from that face
        full_vector = self.corner_vectors[face]
        unit_vector = full_vector / np.linalg.norm(full_vector)
        position = full_vector - buffer * unit_vector
        graphic_kwargs = self._augment_kwargs(graphic_kwargs, {'position': position, 'angle': angle})
        self.add_centered_graphic(graphic, name, **graphic_kwargs)

    def add_picture(self, name, size, **picture_kwargs):
        self.add_graphic(Picture, name, size=size, **picture_kwargs)

    def add_centered_picture(self, name, size, **picture_kwargs):
        self.add_centered_graphic(Picture, name, size=size, **picture_kwargs)

    def add_picture_to_center(self, name, size, **picture_kwargs):
        self.add_graphic_to_center(Picture, name, size=size, **picture_kwargs)

    def add_picture_to_face(self, name, size, face, **picture_kwargs):
        self.add_graphic_to_face(Picture, name, size, face, **picture_kwargs)

    def add_picture_to_corner(self, name, size, corner, **picture_kwargs):
        self.add_graphic_to_corner(Picture, name, size, corner, **picture_kwargs)

    def add_background(self, name, **picture_kwargs):
        self.add_picture_to_center(name, size=self.size, **picture_kwargs)

    def add_text(self, name, size, **text_kwargs):
        self.add_graphic(Text, name, size=size, **text_kwargs)

    def add_centered_text(self, name, size, **text_kwargs):
        self.add_centered_graphic(Text, name, size=size, **text_kwargs)

    def add_text_to_center(self, name, size, **text_kwargs):
        self.add_graphic_to_center(Text, name, size=size, **text_kwargs)

    def add_text_to_face(self, name, face, size, **text_kwargs):
        self.add_graphic_to_face(Text, name, face, size=size, **text_kwargs)

    def add_text_to_corner(self, name, corner, size, **text_kwargs):
        self.add_graphic_to_corner(Text, name, corner, size=size, **text_kwargs)

    def _ensure_textbox_kwargs(self, text_kwargs):
        return self._augment_kwargs(text_kwargs, {'wrap_text': True})

    def add_textbox(self, name, size, **text_kwargs):
        self.add_text(name, size, **self._ensure_textbox_kwargs(text_kwargs))

    def add_centered_textbox(self, name, size, **text_kwargs):
        self.add_centered_text(name, size, **self._ensure_textbox_kwargs(text_kwargs))

    def add_textbox_to_center(self, name, size, **text_kwargs):
        self.add_text_to_center(name, size, **self._ensure_textbox_kwargs(text_kwargs))

    def add_textbox_to_face(self, name, face, size, **text_kwargs):
        self.add_text_to_face(name, face, size, **self._ensure_textbox_kwargs(text_kwargs))

    def add_textbox_to_corner(self, name, corner, size, **text_kwargs):
        self.add_text_to_corner(name, corner, size, **self._ensure_textbox_kwargs(text_kwargs))


class Hex(Shape):

    @property
    def face_angles(self):
        return {
            'n': 0,
            'nw': 60,
            'sw': 120,
            's': 180,
            'se': 240,
            'ne': 300
        }

    @property
    def face_vectors(self):
        r, h = 0.5 * self.size
        x = np.sqrt(0.75) * r * np.cos(np.deg2rad(30))
        y = np.sqrt(0.75) * r * np.sin(np.deg2rad(30))
        return self._all_values_to_pilarray({
            'n': (0, h),
            'nw': (-x, y),
            'sw': (-x, -y),
            's': (0, -h),
            'se': (x, -y),
            'ne': (x, y)
        })

    @property
    def corner_angles(self):
        return {
            'nw': 30,
            'w': 90,
            'sw': 150,
            'se': 210,
            'e': 270,
            'ne': 330
        }

    @property
    def corner_vectors(self):
        r, h = 0.5 * self.size
        x = r * np.sin(np.deg2rad(30))
        return self._all_values_to_pilarray({
            'nw': (-x, h),
            'w': (-r, 0),
            'sw': (-x, -h),
            'se': (x, -h),
            'e': (r, 0),
            'ne': (x, h),
        })

    @property
    def polygon(self):
        w, h = self.size.inttuple
        cx, cy = (0.5 * self.size).inttuple
        xl = (0.25 * self.size).inttuple[0]
        xr = (0.75 * self.size).inttuple[0]
        return (
            (xl, 0),
            (xr, 0),
            (w, cy),
            (xr, h),
            (xl, h),
            (0, cy)
        )


class Rectangle(Shape):

    @property
    def face_angles(self):
        return {
            'n': 0,
            'w': 90,
            's': 180,
            'e': 270
        }

    @property
    def face_vectors(self):
        w, h = 0.5 * self.size
        return self._all_values_to_pilarray({
            'n': (0, h),
            'w': (-w, 0),
            's': (0, -h),
            'e': (w, 0)
        })

    @property
    def corner_angles(self):
        return {
            'nw': 45,
            'sw': 135,
            'se': 225,
            'ne': 315
        }

    @property
    def corner_vectors(self):
        w, h = 0.5 * self.size
        return self._all_values_to_pilarray({
            'nw': (-w, h),
            'sw': (-w, -h),
            'se': (w, -h),
            'ne': (w, h),
        })

    @property
    def polygon(self):
        w, h = self.size.inttuple
        return (
            (0, 0),
            (w, 0),
            (w, h),
            (0, h)
        )


class Square(Rectangle):

    _size = Positive('_size')

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, new_size):
        if hasattr(new_size, '__len__'):
            if new_size[0] != new_size[1]:
                raise ValueError("Squares must have equal side lengths, but got a size of {}".format(new_size))
            else:
                self._size = new_size
        else:
            self._size = (new_size, new_size)


class Ellipse(Shape):

    curve_resolution = 10000

    @property
    def face_angles(self):
        return {
            'n': 0,
            'w': 90,
            's': 180,
            'e': 270,
            'nw': 45,
            'sw': 135,
            'se': 225,
            'ne': 315
        }

    @property
    def face_vectors(self):
        w, h = 0.5 * self.size
        return self._all_values_to_pilarray({
            'n': (0, h),
            'w': (-w, 0),
            's': (0, -h),
            'e': (w, 0),
            'nw': (-w, h),
            'sw': (-w, -h),
            'se': (w, -h),
            'ne': (w, h),
        })

    @property
    def corner_angles(self):
        return self.face_angles

    @property
    def corner_vectors(self):
        return self.face_vectors

    @property
    def polygon(self):
        w, h = self.size.inttuple
        return tuple([
            (int(0.5 * w * (1 + np.sin(theta))), int(0.5 * h * (1 + np.cos(theta))))
            for theta in np.linspace(start=0, stop=2*np.pi, num=self.curve_resolution, endpoint=False)
        ])


class Circle(Ellipse, Square):
    # Ellipse for the angles, vectors, and polygon, square for the definition of size
    pass