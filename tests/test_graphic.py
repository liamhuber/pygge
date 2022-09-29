from unittest import TestCase
from pygge.graphic import Graphic


class TestGraphic(TestCase):
    def void(self):
        g = Graphic((200, 100), color="white")
        g.children.add('title', Graphic(
            g.size * (0.9, 0.1),
            position=g.size * 0.05,
            text='The Title'
        ))
        g.add('mistake', Graphic(g.size * 0.5))
        g.remove('mistake')
        title = g.children.pop('title')
        g.add('title', title)  #?

    def test(self):
        g = Graphic(size=(50, 100), color="white")
        g.add('green', Graphic(size=(20, 20), position=(-10, -10), parent=g, color="green"))
        g.add('red', Graphic(size=(20, 20), position=(40, 90), parent=g, color="red"))
        g.text.text = "Foobar"
        g.text.position = (g.text.position.x, 0.5 * g.size.y)
        g.image.show()

