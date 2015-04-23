from cocos.layer import Layer
from cocos.actions import *

# Game State Values
WAITING_PLAYER_MOVEMENT = 1
PLAYER_DOING_MOVEMENT = 2
SWAPPING_TILES = 3
IMPLODING_TILES = 4
DROPPING_TILES = 5

class GameController(Layer):

    is_event_handler = True #: enable pyglet's events

    def __init__(self, model):
        super(GameController, self).__init__()
        self.model = model

    def on_mouse_press(self, x, y, buttons, modifiers):
        if self.model.can_play():
            self.model.swap_start_pos = self.model.to_model_pos((x, y))
            self.model.game_state = PLAYER_DOING_MOVEMENT

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        print self.model.game_state
        if self.model.game_state != PLAYER_DOING_MOVEMENT:
            return

        start_x, start_y = self.model.swap_start_pos
        self.model.swap_end_pos = new_x, new_y = self.model.to_model_pos((x, y))

        distance = abs(new_x - start_x) + abs(new_y - start_y)  # horizontal + vertical grid steps

        # Ignore movement if not at 1 step away from the initial position
        if new_x < 0 or new_y < 0 or distance != 1:
            return

        # Start swap animation for both objects
        tile_type, sprite = self.model.tile_grid[self.model.swap_start_pos]
        sprite.do(MoveTo(self.model.to_display(self.model.swap_end_pos), 0.4))
        tile_type, sprite = self.model.tile_grid[self.model.swap_end_pos]
        sprite.do(MoveTo(self.model.to_display(self.model.swap_start_pos), 0.4) + CallFunc(self.model.on_tiles_swap_completed))

        # Swap elements at the board data grid
        self.model.swap_elements(self.model.swap_start_pos, self.model.swap_end_pos)
        self.model.game_state = SWAPPING_TILES