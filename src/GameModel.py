__all__ = ['GameModel']

import pyglet
from random import choice
from glob import glob
from cocos.sprite import Sprite
from cocos.actions import *

CELL_WIDTH, CELL_HEIGHT = 100, 100
ROWS_COUNT, COLS_COUNT = 6, 8

# Game State Values
WAITING_PLAYER_MOVEMENT = 1
PLAYER_DOING_MOVEMENT = 2
SWAPPING_TILES = 3
IMPLODING_TILES = 4
DROPPING_TILES = 5

class GameModel(pyglet.event.EventDispatcher):
    def __init__(self):
        super(GameModel, self).__init__()
        self.tile_grid = {}  # Dict emulated sparse matrix, key: tuple(x,y), value : tile_type
        self.imploding_tiles = []  # List of tile sprites being imploded, used during IMPLODING_TILES
        self.dropping_tiles = []  # List of tile sprites being dropped, used during DROPPING_TILES
        self.swap_start_pos = None  # Position of the first tile clicked for swapping
        self.swap_end_pos = None  # Position of the second tile clicked for swapping
        self.available_tiles = glob('images/*.png')
        self.game_state = WAITING_PLAYER_MOVEMENT

    def can_play(self):
        return self.game_state == WAITING_PLAYER_MOVEMENT

    def start(self):
        self.set_next_level()

    def set_next_level(self):
        self.fill_with_random_tiles()

    def fill_with_random_tiles(self):
        """
        Fills the tile_grid with random tiles
        """
        tile_grid = {}
        # Fill the data matrix with random tile types
        while True:  # Loop until we have a valid table (no imploding lines)
            for x in range(COLS_COUNT):
                for y in range(ROWS_COUNT):
                    tile_type, sprite = choice(self.available_tiles), None
                    tile_grid[x, y] = tile_type, sprite
            if len(self.get_same_type_lines(tile_grid)) == 0:
                break
            tile_grid = {}

        # Build the sprites based on the assigned tile type
        for key, value in tile_grid.iteritems():
            tile_type, sprite = value
            sprite = self.tile_sprite(tile_type, self.to_display(key))
            tile_grid[key] = tile_type, sprite
            self.view.add(sprite)

        self.tile_grid = tile_grid

    def swap_elements(self, elem1_pos, elem2_pos):
        tile_type, sprite = self.tile_grid[elem1_pos]
        self.tile_grid[elem1_pos] = self.tile_grid[elem2_pos]
        self.tile_grid[elem2_pos] = tile_type, sprite

    def implode_lines(self):
        """
        :return: Implodes lines with more than 3 elements of the same type
        """
        for x, y in self.get_same_type_lines(self.tile_grid):
            same_type, sprite = self.tile_grid[x, y]
            self.tile_grid[x, y] = None
            self.imploding_tiles.append(sprite)  # Track tiles being imploded
            sprite.do(ScaleTo(0, 0.5) | RotateTo(180, 0.5) + CallFuncS(self.on_tile_remove))  # Implode animation
        if len(self.imploding_tiles) > 0:
            self.game_state = IMPLODING_TILES  # Wait for the implosion animation to finish
        else:
            self.game_state = WAITING_PLAYER_MOVEMENT
        return self.imploding_tiles

    def drop_groundless_tiles(self):
        """
        Walk on all columns, from bottom to up:
            a) count gap or move down pieces for gaps already counted
            b) on top drop as much tiles as gaps counted
        :return:
        """
        tile_grid = self.tile_grid

        for x in range(COLS_COUNT):
            gap_count = 0
            for y in range(ROWS_COUNT):
                if tile_grid[x, y] is None:
                    gap_count += 1
                elif gap_count > 0:  # Move from y to y-gap_count
                    tile_type, sprite = tile_grid[x, y]
                    if gap_count > 0:
                        sprite.do(MoveTo(self.to_display((x, y - gap_count)), 0.3 * gap_count))
                    tile_grid[x, y - gap_count] = tile_type, sprite
            for n in range(gap_count):  # Drop as much tiles as gaps counted
                tile_type = choice(self.available_tiles)
                sprite = self.tile_sprite(tile_type, self.to_display((x, y + n + 1)))
                tile_grid[x, y - gap_count + n + 1] = tile_type, sprite
                sprite.do(
                    MoveTo(self.to_display((x, y - gap_count + n + 1)), 0.3 * gap_count) + CallFuncS(
                        self.on_drop_completed))
                self.view.add(sprite)
                self.dropping_tiles.append(sprite)

    def on_drop_completed(self, sprite):
        self.dropping_tiles.remove(sprite)
        if len(self.dropping_tiles) == 0:  # All tile dropped
            self.implode_lines()  # Check for new implosions

    def on_tile_remove(self, sprite):
        self.imploding_tiles.remove(sprite)
        self.view.remove(sprite)
        if len(self.imploding_tiles) == 0:  # Implosion complete, drop tiles to fill gaps
            self.drop_groundless_tiles()

    def set_controller( self, controller):
        self.controller = controller

    def set_view( self, view):
        self.view = view

    def tile_sprite(self, tile_type, pos):
        """
        :param tile_type: numeric id, must be in the range of available images
        :param pos: sprite position
        :return: sprite built form tile_type
        """
        sprite = Sprite(tile_type)
        sprite.position = pos
        sprite.scale = 1
        return sprite

    def on_tiles_swap_completed(self):
        self.game_state = DROPPING_TILES

        if len(self.implode_lines()) == 0:
            # No lines imploded, roll back the game play

            # Start swap animation for both objects
            tile_type, sprite = self.tile_grid[self.swap_start_pos]
            sprite.do(MoveTo(self.to_display(self.swap_end_pos), 0.4))
            tile_type, sprite = self.tile_grid[self.swap_end_pos]
            sprite.do(MoveTo(self.to_display(self.swap_start_pos), 0.4) + CallFunc(self.on_tiles_swap_back_completed))

            # Revert on the grid
            self.swap_elements(self.swap_start_pos, self.swap_end_pos)
            self.game_state = SWAPPING_TILES

    def on_tiles_swap_back_completed(self):
        self.game_state = WAITING_PLAYER_MOVEMENT

    def to_display(self, (row, col)):
        """
        :param row:
        :param col:
        :return: (x, y) from display corresponding coordinates from the bi-dimensional ( row, col) array position
        """
        return CELL_WIDTH / 2 + row * CELL_WIDTH, CELL_HEIGHT / 2 + col * CELL_HEIGHT

    def to_model_pos(self, (view_x, view_y)):
        return view_x / CELL_WIDTH, view_y / CELL_HEIGHT

    def get_same_type_lines(self, tile_grid, min_count=3):
        """
        Identify vertical and horizontal lines composed of min_count consecutive elements
        :param min_count: minimum consecutive elements to identify a line
        """
        all_line_members = []

        # Check for vertical lines
        for x in range(COLS_COUNT):
            same_type_list = []
            last_tile_type = None
            for y in range(ROWS_COUNT):
                tile_type, sprite = tile_grid[x, y]
                if last_tile_type == tile_type:
                    same_type_list.append((x, y))
                if tile_type != last_tile_type or y == ROWS_COUNT - 1:  # Line end because type changed or edge reached
                    if len(same_type_list) >= min_count:
                        all_line_members.extend(same_type_list)
                    last_tile_type = tile_type
                    same_type_list = [(x, y)]

        # Check for horizontal lines
        for y in range(ROWS_COUNT):
            same_type_list = []
            last_tile_type = None
            for x in range(COLS_COUNT):
                tile_type, sprite = tile_grid[x, y]
                if last_tile_type == tile_type:
                    same_type_list.append((x, y))
                if tile_type != last_tile_type or x == COLS_COUNT - 1:  # Line end because of type change or edge reached
                    if len(same_type_list) >= min_count:
                        all_line_members.extend(same_type_list)
                    last_tile_type = tile_type
                    same_type_list = [(x, y)]

        # Remove duplicates
        all_line_members = list(set(all_line_members))
        return all_line_members

    def dump_table(self):
        """
        :return: Prints the play table, for debug
        """
        for y in range(ROWS_COUNT - 1, -1, -1):
            line_str = ''
            for x in range(COLS_COUNT):
                line_str += str(self.tile_grid[x, y][0])
            print line_str

GameModel.register_event_type('on_move_tile')