from typing import Tuple, Optional

class Graphic:
    def __init__(
            self,
            size: Tuple[int, int],
            parent: Optional[Graphic],

    ):
        pass


graphic = Graphic(
    (100, 400),
    color='black'
)
graphic.add(
    'main'
)
graphic.add(
    'title',
    Graphic(
        ('90%', '10%'),
        position=('5%', '5%'),
        text='The Title'
    )
)