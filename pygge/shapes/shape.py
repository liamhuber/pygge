# coding: utf-8
# Copyright (c) Liam Huber
# Distributed under the terms of "New BSD License", see the LICENSE file.

import numpy as np
from .. core import Graphic, Text, Picture
from abc import abstractmethod
from PIL import Image, ImageDraw

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
        self._image = self._cut_out_shape(self.image)

    def _cut_out_shape(self, image):
        mask = Image.new('RGBA', self.size.inttuple)
        draw = ImageDraw.Draw(mask)
        draw.polygon(self.polygon, fill='#000')
        cut_image = Image.new('RGBA', self.size.inttuple)
        cut_image.paste(image, mask=mask)
        return cut_image

    def add_graphic(self, graphic_class, name, size, **graphic_kwargs):
        graphic = graphic_class(size, **graphic_kwargs)
        setattr(self.children, name, graphic)

    @staticmethod
    def _augment_kwargs(kwargs, new_kwargs, exclusive=True):
        for k, v in new_kwargs:
            if k in kwargs.keys() and exclusive:
                raise ValueError("'{}' is already defined and cannot be reset.".format(k))
            else:
                kwargs[k] = v
        return kwargs

    def add_centered_graphic(self, graphic_class, name, size, **graphic_kwargs):
        graphic_kwargs = self._augment_kwargs(graphic_kwargs, {'anchor': 'center', 'coordinate_frame': 'center'})
        self.add_graphic(graphic_class, name, size, **graphic_kwargs)

    def add_graphic_to_center(self, graphic_class, name, size, **graphic_kwargs):
        graphic_kwargs = self._augment_kwargs(graphic_kwargs, {'position': (0, 0)})
        self.add_centered_graphic(graphic_class, name, size, **graphic_kwargs)

    def add_graphic_to_face(self, graphic_class, name, size, face, buffer=0, **graphic_kwargs):
        angle = self.face_angles[face] + 180  # 180 so it's read from that face
        full_vector = self.face_vectors[face]
        unit_vector = full_vector / np.linalg.norm(full_vector)
        position = full_vector - buffer * unit_vector
        graphic_kwargs = self._augment_kwargs(graphic_kwargs, {'position': position, 'angle': angle})
        self.add_centered_graphic(graphic_class, name, size, **graphic_kwargs)

    def add_graphic_to_corner(self, graphic_class, name, size, face, buffer=0, **graphic_kwargs):
        angle = self.corner_angles[face] + 180  # 180 so it's read from that face
        full_vector = self.corner_vectors[face]
        unit_vector = full_vector / np.linalg.norm(full_vector)
        position = full_vector - buffer * unit_vector
        graphic_kwargs = self._augment_kwargs(graphic_kwargs, {'position': position, 'angle': angle})
        self.add_centered_graphic(graphic_class, name, size, **graphic_kwargs)

    def add_picture(self, name, size, **picture_kwargs):
        self.add_graphic(Picture, name, size, **picture_kwargs)

    def add_centered_picture(self, name, size, **picture_kwargs):
        self.add_centered_graphic(Picture, name, size, **picture_kwargs)

    def add_picture_to_center(self, name, size, **picture_kwargs):
        self.add_graphic_to_center(Picture, name, size, **picture_kwargs)

    def add_picture_to_face(self, name, size, face, **picture_kwargs):
        self.add_graphic_to_face(Picture, name, size, face, **picture_kwargs)

    def add_picture_to_corner(self, name, size, corner, **picture_kwargs):
        self.add_graphic_to_corner(Picture, name, size, corner, **picture_kwargs)

    def add_background(self, name, **picture_kwargs):
        self.add_picture_to_center(name, self.size, **picture_kwargs)

    def add_text(self, name, size, **text_kwargs):
        self.add_graphic(Text, name, size, **text_kwargs)

    def add_centered_text(self, name, size, **text_kwargs):
        self.add_centered_graphic(Text, name, size, **text_kwargs)

    def add_text_to_center(self, name, size, **text_kwargs):
        self.add_graphic_to_center(Text, name, size, **text_kwargs)

    def add_text_to_face(self, name, size, face, **text_kwargs):
        self.add_graphic_to_face(Text, name, size, face, **text_kwargs)

    def add_text_to_corner(self, name, size, corner, **text_kwargs):
        self.add_graphic_to_corner(Text, name, size, corner, **text_kwargs)

    def _ensure_textbox_kwargs(self, text_kwargs):
        return self._augment_kwargs(text_kwargs, {'wrapped_text': True})

    def add_textbox(self, name, size, **text_kwargs):
        self.add_text(name, size, **self._ensure_textbox_kwargs(text_kwargs))

    def add_centered_textbox(self, name, size, **text_kwargs):
        self.add_centered_text(name, size, **self._ensure_textbox_kwargs(text_kwargs))

    def add_textbox_to_center(self, name, size, **text_kwargs):
        self.add_text_to_center(name, size, **self._ensure_textbox_kwargs(text_kwargs))

    def add_textbox_to_face(self, name, size, face, **text_kwargs):
        self.add_text_to_face(name, size, face, **self._ensure_textbox_kwargs(text_kwargs))

    def add_textbox_to_corner(self, name, size, corner, **text_kwargs):
        self.add_text_to_corner(name, size, corner, **self._ensure_textbox_kwargs(text_kwargs))
