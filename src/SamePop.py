import sys
from cocos import director
from cocos.scene import Scene


sys.path.append('src')
from PlayBoard import PlayBoard

director.director.init(width=800, height=600, caption="Pop The Same")

platform = director.window.get_platform()
display = platform.get_default_display()
screen_width, screen_height = display.get_default_screen().width, display.get_default_screen().height
player_layer = PlayBoard()
main_scene = Scene(player_layer)

director.director.run(main_scene)