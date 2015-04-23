from os.path import exists, join

import pyglet.resource
from cocos import director
from cocos.scene import Scene
from cocos.layer import MultiplexLayer
from Menus import MainMenu


if exists(join('src', 'SamePop.py')):  # When launched from src dir
    pyglet.resource.path = ['..']
    pyglet.resource.reindex()

director.director.init(width=800, height=650, caption="Pop The Same")

scene = Scene()
scene.add(MultiplexLayer(
    MainMenu()
    #,OptionsMenu(),
    #ScoresLayer(),
),
    z=1)

director.director.run(scene)