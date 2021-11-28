# pygge

![Travis build status](https://travis-ci.com/liamhuber/pygge.svg?branch=master)
[![Coverage Status](https://coveralls.io/repos/github/liamhuber/pygge/badge.svg?branch=master)](https://coveralls.io/github/liamhuber/pygge?branch=master)

The overly-ambitiously-named Python general graphic editor -- pygge (pro. 'piggie') -- is built on top of the python 
image library -- pillow/PIL -- to provide a scriptable graphics editor.

The core idea is to allow what-you-type-is-what-you-get graphics editing in the python environment. To this end, there 
is a canvas object which can contain multiple components whose behaviour is controlled by code. The raw content for 
these components, be it an image file or text, is then interpreted by the component. This allows the programatic 
construction of template canvases which can be filled with content later, e.g. in a loop. 

In practice, this project was motivated by a need to rapidly prototype game piece art for the 
[tabletopia](www.tabletopia.com) platform, but the library should in principle be generic and useful for other tasks.


```python
from pygge import config, Text, Picture, games
from pygge.shapes import Square
from pygge.games.tabletopia import Card
import numpy as np
import yaml

print(config.assets)
> None
config.assets = './assets'
print(config.assets)
> /Users/liamhuber/EmergentGames/some_project/assets/
print(config.out)  # Default is out
> /Users/liamhuber/EmergentGames/some_project/out/

card_template = config.create.Card(fill='#964')

picture_box = Square(
    size=0.33 * min(card_template.size),
    anchor='upper center',
    position=(0, -60),
    fill='#fec'
)
picture = Picture(
    size=0.9 * picture_box.size,
)
picture_box.picture = picture

textbox_width = 0.9 * card_template.size.width
title = Text(
    size=(textbox_width, 50),
    font='fonts/some_font.fft'
)
text = Text(
    size=(textbox_width, 200),
    font='fonts/some_other_font.fft'
)

card_template.picture_box = picture_box
card_template.title = title
card_template.text = text

for card_type, d in yaml.load('cards.yaml', Loader=yaml.FullLoader).items():
    sub_template = card_template.copy()
    sub_template.fill = d.fill
    
    for card_name, dd in d.items():
        card = sub_template.copy()
        card.title.content = card_name
        card.text.content = dd.text
        card.picture_box.picture.content = dd.picture
        card.save(f'cards/{card_type}/{card_name}')
        
# And a card back


hex_template = games.tabletopia.Hex(
    style='stretch',  # fit | 
    lock_aspect=True  # Should be default anyhow
)

for hex_category, d in yaml.load('tiles.yaml', Loader=yaml.FullLoader):
    match hex_category:
        'basic':
            tile = hex_template.copy()
            tile.content = f'backgrounds/{d.background}'
```

