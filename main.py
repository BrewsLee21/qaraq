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
    
    # Main game loop
    while True:
        player_view = get_player_view(map_grid, p1.player_x, p1.player_y)
        ui.update_player_view(player_view)
        inp = str(ui.bot_win.getch())
        print_to_stderr(inp)
    
if __name__ == "__main__":
    wrapper(partial(main, map_size=c.MAP_SIZE))
