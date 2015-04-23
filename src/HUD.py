from cocos.layer import *

from cocos.text import *
from cocos.actions import *

class Status( object ):
    def __init__( self ):

        # current score
        self.score = 0

        # next piece
        self.next_piece = None

        # current level
        self.level = None

        # current level idx
        self.level_idx = None

        # level lines completed
        self.lines = 0

        # total lines completed
        self.tot_lines = 0

    def reset( self ):
        self.score = 0
        self.next_piece = None
        self.level = None
        self.level_idx = None
        self.lines = 0
        self.tot_lines = 0

status = Status()

class BackgroundLayer(Layer):
    def __init__(self):
        super(BackgroundLayer, self).__init__()
        # self.img = pyglet.resource.image('background.png')

    def draw(self):
        pass
        # glPushMatrix()
        #self.transform()
        #self.img.blit(0,0)
        #glPopMatrix()


class ScoreLayer(ColorLayer):
    def __init__(self):
        w, h = director.get_window_size()
        super(ScoreLayer, self).__init__(64, 64, 224, 120)

        # transparent layer
        self.add(ColorLayer(32, 32, 32, 32, width=w, height=48), z=-1)

        self.position = (0, h - 48)

        self.score = Label('Score:', font_size=36,
                           font_name='Edit Undo Line BRK',
                           color=(255, 255, 255, 255),
                           anchor_x='left',
                           anchor_y='bottom')
        self.score.position = (0, 0)
        self.add(self.score)

        self.lines = Label('Lines:', font_size=36,
                           font_name='Edit Undo Line BRK',
                           color=(255, 255, 255, 255),
                           anchor_x='left',
                           anchor_y='bottom')
        self.lines.position = (235, 0)
        self.add(self.lines)

        self.lvl = Label('Lvl:', font_size=36,
                         font_name='Edit Undo Line BRK',
                         color=(255, 255, 255, 255),
                         anchor_x='left',
                         anchor_y='bottom')

        self.lvl.position = (450, 0)
        self.add(self.lvl)

    def draw(self):
        super(ScoreLayer, self).draw()
        self.score.element.text = 'Score:%d' % 0
        self.lines.element.text = 'Lines:%d' % 0

        lvl = status.level_idx or 0
        self.lvl.element.text = 'Lvl:%d' % lvl

        if status.next_piece:
            status.next_piece.draw()


class MessageLayer(Layer):
    def show_message(self, msg, callback=None):
        w, h = director.get_window_size()

        self.msg = Label(msg,
                         font_size=52,
                         font_name='Edit Undo Line BRK',
                         anchor_y='center',
                         anchor_x='center')
        self.msg.position = (w // 2.0, h)

        self.add(self.msg)

        actions = Accelerate(MoveBy((0, -h / 2.0), duration=0.5)) + \
                  Delay(1) + \
                  Accelerate(MoveBy((0, -h / 2.0), duration=0.5)) + \
                  Hide()

        if callback:
            actions += CallFunc(callback)

        self.msg.do(actions)


class HUD(Layer):
    def __init__(self):
        super(HUD, self).__init__()
        self.add(ScoreLayer())
        self.add(MessageLayer(), name='msg')

    def show_message(self, msg, callback=None):
        self.get('msg').show_message(msg, callback)