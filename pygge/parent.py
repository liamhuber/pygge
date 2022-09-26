from __future__ import annotations


class Adder:
    def __init__(self, parent: HasChildren):
        self._parent = parent

    def __call__(self, name: str, child):
        self._parent.children[name] = child


class HasChildren:
    def __init__(self):
        self._children = {}
        self._adder = Adder(self)

    @property
    def children(self):
        return self._children

    @property
    def add(self):
        return self._adder

    def remove(self, key):
        return self._children.pop(key)
