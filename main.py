from functools import partial
import curses
from curses import wrapper

from utils import *
from ui import UI
from player import Player
import config as c

def main(stdscr, map_size):
    map_grid = generate_map_grid(map_size) # Returns a 2D list representing the map grid
    if map_grid == -1:
        print("grid size must be larger than 0!")

    p1 = Player("p1", get_center(map_grid))
    ui = UI(stdscr)

    key_directions = {
        "KEY_LEFT": "left",
        "KEY_UP": "up",
        "KEY_RIGHT": "right",
        "KEY_DOWN": "down"
    }

    map_grid[p1.player_y][p1.player_x].player_present = True
    
    # Main game loop
    while True:
        player_view = get_player_view(map_grid, p1.player_x, p1.player_y)
        ui.update_player_view(player_view)
        
        inp = stdscr.getkey()
        if inp in key_directions:
            map_grid[p1.player_y][p1.player_x].player_present = False
            p1.move_in_direction(map_grid, key_directions[inp])
            map_grid[p1.player_y][p1.player_x].player_present = True
                
if __name__ == "__main__":
    wrapper(partial(main, map_size=c.MAP_SIZE))
