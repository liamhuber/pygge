from __future__ import annotations

from abc import ABC, abstractmethod
from traitlets import HasTraits
from pygge.traitlets import PositiveInt, ImageTrait


class MetaTraited(type(HasTraits), type(ABC)):
    pass


class Traited(HasTraits, ABC, metaclass=MetaTraited):
    def __init__(self, *args, **kwargs):
        HasTraits.__init__(self, *args, **kwargs)
        for klass in self.__class__.__mro__:
            try:
                klass.initialize(self)
            except AttributeError:
                pass

    def initialize(self):
        pass


class IsGraphic(Traited, ABC):
    """For typing"""
    size = PositiveInt()
    _image = ImageTrait()

    @property
    def image(self):
        if self._image is None:
            self.render()
        return self._image

    @abstractmethod
    def render(self):
        pass
