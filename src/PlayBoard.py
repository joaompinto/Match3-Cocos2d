import cocos
import pyglet.resource
from cocos.actions import *
from cocos.sprite import Sprite
from random import randint
from pprint import pprint


pyglet.resource.path = ['..']
pyglet.resource.reindex()

GRID_WIDTH = 100
GRID_HEIGHT = 100

ROWS_COUNT = 6
COLS_COUNT = 8

# Game State Values
WAITING_PLAYER_MOVEMENT = 1
PLAYER_DOING_MOVEMENT = 2
SWAPPING_TILES = 3
IMPLODING_TILES = 4
DROPPING_TILES = 5


class PlayBoard(cocos.layer.ColorLayer):

    is_event_handler = True  #: enable director.window events

    def __init__(self):
        super(PlayBoard, self).__init__(64, 64, 224, 0)
        self.playTable = {}        # Emulate a sparse matrix, the supplied tuple (x,y) is used as the key
        self.imploding_tiles = []  # List of tiles being imploded, used during IMPLODING_TILES
        self.dropping_tiles = []   # List of tiles dropping, used during DROPPING_TILES
        self.swap_start_pos = None # Position of first object clicked for swapping
        self.playTable = {}
        self.initial_object = None
        self.fill_random_objects()
        self.game_state = WAITING_PLAYER_MOVEMENT

    def tile_sprite(self, object_type, pos):
        sprite = Sprite('images/fruit_%d.png' % object_type)
        sprite.position = pos
        sprite.scale = 2
        return sprite

    def fill_random_objects(self):

        # Fill the data matrix with random tiles types
        while True:  # Loop until we have a valid table (no imploding lines)
            playtable = {}
            for x in range(COLS_COUNT):
                for y in range(ROWS_COUNT):
                    object_type, sprite = randint(1, 5), None
                    playtable[x, y] = object_type, sprite
            if len(self.get_same_type_lines(playtable)) == 0:
                break

        # Replace with real sprites
        for key, value in playtable.iteritems():
            object_type, sprite = value
            sprite = self.tile_sprite(object_type, self.to_display(key[0], key[1]))
            playtable[key] = object_type, sprite
            self.add(sprite)

        self.playTable = playtable

    def on_mouse_press(self, x, y, buttons, modifiers):
        if self.game_state == WAITING_PLAYER_MOVEMENT:
            self.swap_start_pos = x / GRID_WIDTH, y / GRID_HEIGHT
            self.game_state = PLAYER_DOING_MOVEMENT

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.game_state != PLAYER_DOING_MOVEMENT:
            return
        start_x, start_y = self.swap_start_pos
        new_x, new_y = x / GRID_WIDTH, y / GRID_HEIGHT
        distance = abs(new_x - start_x) + abs(new_y - start_y)
        if new_x >= 0 and new_y >= 0 and distance == 1:
            # Start swap animation for both objects
            object_type, sprite = self.playTable[start_x, start_y]
            sprite.do(MoveTo(self.to_display(new_x, new_y), 0.4))
            object_type, sprite = self.playTable[new_x, new_y]
            sprite.do(MoveTo(self.to_display(start_x, start_y), 0.4) + CallFunc(self.on_tile_swap_completed))
            # Swap them at the board data grid
            object_type, sprite = self.playTable[new_x, new_y]
            self.playTable[new_x, new_y] = self.playTable[start_x, start_y]
            self.playTable[start_x, start_y] = object_type, sprite
            self.initial_object = self.swap_start_pos
            self.game_state = SWAPPING_TILES

    def on_tile_swap_completed(self):
        self.game_state = DROPPING_TILES
        self.implode_lines()

    def to_display(self, row, col):
        """
        :param row:
        :param col:
        :return: (x, y) from display corresponding coordinates from the bi-dimensional ( row, col) array position
        """
        return GRID_WIDTH/2 + row * GRID_WIDTH, GRID_HEIGHT/2 + col * GRID_HEIGHT

    def get_same_type_lines(self, playtable, min_count=3):
        """
        Identify vertical and horizonal lines composed of min_count consecutive elements
        :param min_count: minimum consecutive elements to identify a line
        """
        all_line_members = []

        # Check for vertical lines
        for x in range(COLS_COUNT):
            same_type_list = []
            last_tile_type = None
            for y in range(ROWS_COUNT):
                tile_type, sprite = playtable[x, y]
                if last_tile_type == tile_type:
                    same_type_list.append((x, y))
                if tile_type != last_tile_type or y == ROWS_COUNT-1:  # Line end because of type change or edge reached
                    if len(same_type_list) >= min_count:
                        all_line_members.extend(same_type_list)
                    last_tile_type = tile_type
                    same_type_list = [(x, y)]

        # Check for horizontal lines
        for y in range(ROWS_COUNT):
            same_type_list = []
            last_tile_type = None
            for x in range(COLS_COUNT):
                tile_type, sprite = playtable[x, y]
                if last_tile_type == tile_type:
                    same_type_list.append((x, y))
                if tile_type != last_tile_type or x == COLS_COUNT-1:  # Line end because of type change or edge reached
                    if len(same_type_list) >= min_count:
                        all_line_members.extend(same_type_list)
                    last_tile_type = tile_type
                    same_type_list = [(x, y)]

        # Remove duplicates
        all_line_members = list(set(all_line_members))
        return all_line_members

    def implode_lines(self):
        """
        :return: Implodes lines with more than 3 elements of the same type
        """
        for x, y in self.get_same_type_lines(self.playTable):
            same_type, sprite = self.playTable[x, y]
            self.playTable[x, y] = None
            self.imploding_tiles.append(sprite)  # Track tiles being imploded
            sprite.do(ScaleTo(0, 0.5) | RotateTo(180, 0.5) + CallFuncS(self.on_tile_remove))  # Implode animation
        if len(self.imploding_tiles) > 0:
            self.game_state = IMPLODING_TILES  # Wait for the implosion animation end
        else:
            self.game_state = WAITING_PLAYER_MOVEMENT

    def drop_groundless_tiles(self):
        playtable = self.playTable
        for x in range(COLS_COUNT):
            gap_count = 0
            for y in range(ROWS_COUNT):
                if playtable[x, y] is None:
                    gap_count += 1
                else:
                    tile_type, sprite = playtable[x, y]
                    if gap_count > 0:
                        sprite.do(MoveTo(self.to_display(x, y-gap_count), 0.3*gap_count))
                    playtable[x, y-gap_count] = tile_type, sprite
            for n in range(gap_count):
                object_type = randint(1, 5)
                sprite = self.tile_sprite(object_type, self.to_display(x, y+n+1))
                playtable[x, y-gap_count+n+1] = object_type, sprite
                sprite.do(
                    MoveTo(self.to_display(x, y-gap_count+n+1), 0.3*gap_count) + CallFuncS(self.on_drop_completed))
                self.add(sprite)
                self.dropping_tiles.append(sprite)

    def on_drop_completed(self, sprite):
        self.dropping_tiles.remove(sprite)
        if len(self.dropping_tiles) == 0:  # All tiles stopped dropping
            self.implode_lines()       # Check for new lines

    def on_tile_remove(self, sprite):
        self.imploding_tiles.remove(sprite)
        self.remove(sprite)
        if len(self.imploding_tiles) == 0:
            self.drop_groundless_tiles()

    def dump_table(self):
        """
        :return: Prints the play table, for debug
        """
        for y in range(ROWS_COUNT-1, -1, -1):
            line_str = ''
            for x in range(COLS_COUNT):
                line_str += str(self.playTable[x, y][0])
            print line_str
