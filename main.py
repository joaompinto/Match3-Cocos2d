import cocos
from cocos.director import director
from cocos.actions import *
from random import randint

class PlayTable:
    def __init__(self, rows, cols):
        self.rows, self.cols = rows, cols
        self.data = []
        for x in range(rows):
            new_row = []
            for y in range(cols):
               new_row.append(None)
            self.data.append(new_row)

    def set(self, x, y, value):
        self.data[x][y] = value

    def get(self, x, y):
        return self.data[x][y]

class PlayBoard(cocos.layer.ColorLayer):

    def __init__(self):
        super(PlayBoard, self).__init__(64, 64, 224, 0)

        self.starting_object = self.ending_object = None
        playtable = self.playTable = PlayTable(8, 8)
        for x in range(8):
            for y in range(8):
                object_type = randint(1, 5)
                sprite = cocos.sprite.Sprite('images/fruit_%d.png' % object_type)
                sprite.position = 50+x*100, 50+y*100
                sprite.scale = 2
                playtable.set(x, y, (object_type, sprite))
                self.add(sprite)

    def on_mouse_press(self, x, y):
        self.starting_object = x/100, y/100


    def on_mouse_drag(self, x, y):
        if not self.starting_object:
            return
        start_x, start_y = self.starting_object
        self.ending_object = new_x, new_y = x/100, y/100
        delta = abs(new_x-start_x) + abs(new_y-start_y)
        print delta
        if new_x >= 0 and new_y >= 0 and delta == 1:
            object_type, sprite = self.playTable.get(start_x, start_y)
            sprite.do(MoveTo((50+new_x*100, 50+new_y*100), duration=0.4))
            object_type, sprite = self.playTable.get(new_x, new_y)
            sprite.do(MoveTo((50+start_x*100, 50+start_y*100), duration=0.4) + CallFuncS(self.on_move_completed))
            self.initial_object = self.starting_object
            self.starting_object = None

    def on_move_completed(self, sprite):
        print "Completed"
        start_x, start_y = self.initial_object
        end_x, end_y = self.ending_object
        tmp_type, tmp_sprite = self.playTable.get(start_x, start_y)
        self.playTable.set(start_x, start_y, self.playTable.get(end_x, end_y))
        self.playTable.set(end_x, end_y, (tmp_type, tmp_sprite))

class MouseDisplay(cocos.layer.Layer):

    is_event_handler = True     #: enable director.window events

    def __init__(self, mousehandler):
        super( MouseDisplay, self ).__init__()

        self.mousehandler = mousehandler

    def on_mouse_press(self, x, y, buttons, modifiers):
        self.posx, self.posy = director.get_virtual_coordinates (x, y)
        self.mousehandler.on_mouse_press(x, y)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.posx, self.posy = director.get_virtual_coordinates (x, y)
        self.mousehandler.on_mouse_drag(x, y)

cocos.director.director.init(width=800, height=600, caption="Pop The Same")


player_layer = PlayBoard()
main_scene = cocos.scene.Scene(player_layer, MouseDisplay(player_layer))
cocos.director.director.run(main_scene)