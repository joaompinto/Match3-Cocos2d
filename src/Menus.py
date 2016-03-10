from cocos.menu import *
from cocos.director import director
from cocos.scenes.transitions import *
import pyglet


class MainMenu(Menu):
    def __init__(self):
        super(MainMenu, self).__init__('SamePop')

        # you can override the font that will be used for the title and the items
        # you can also override the font size and the colors. see menu.py for
        # more info
        self.font_title['font_name'] = 'Edit Undo Line BRK'
        self.font_title['font_size'] = 72
        self.font_title['color'] = (204, 164, 164, 255)

        self.font_item['font_name'] = 'Edit Undo Line BRK',
        self.font_item['color'] = (32, 16, 32, 255)
        self.font_item['font_size'] = 32
        self.font_item_selected['font_name'] = 'Edit Undo Line BRK'
        self.font_item_selected['color'] = (32, 100, 32, 255)
        self.font_item_selected['font_size'] = 46

        # example: menus can be vertical aligned and horizontal aligned
        self.menu_anchor_y = CENTER
        self.menu_anchor_x = CENTER

        items = []

        items.append(MenuItem('New Game', self.on_new_game))
        # items.append( MenuItem('Options', self.on_options) )
        # items.append( MenuItem('Scores', self.on_scores) )
        items.append(MenuItem('Quit', self.on_quit))

        self.create_menu(items, shake(), shake_back())

    def on_new_game(self):
        import GameView

        director.push(FlipAngular3DTransition(
            GameView.get_newgame(), 1.5))

    def on_options(self):
        self.parent.switch_to(1)

    def on_scores(self):
        self.parent.switch_to(2)

    def on_quit(self):
        pyglet.app.exit()
