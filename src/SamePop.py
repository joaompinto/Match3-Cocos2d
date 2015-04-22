import pyglet.resource
from cocos import director
from cocos.scene import Scene

from os.path import exists, join, basename

if exists(join('src', 'SamePop.py')):  # When launched from src dir
    pyglet.resource.path = ['..']
    pyglet.resource.reindex()

from PlayBoard import PlayBoard

director.director.init(width=800, height=600, caption="Pop The Same")

#platform = director.window.get_platform()
#display = platform.get_default_display()
#screen_width, screen_height = display.get_default_screen().width, display.get_default_screen().height
player_layer = PlayBoard()
main_scene = Scene(player_layer)

director.director.run(main_scene)