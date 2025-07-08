import curses

from tile import Tile
import config as c

class UI:
    def __init__(self, stdscr):

        # class variables:
        #   stdscr - standard screen
        #   top_win - top window
        #   bot_win - bottom window
        #   player_view_win - a window containing the grid of visible tiles
        #   player_view_tile_grid - a 2D grid of windows inside player_view_win each representing one tile
        #
        #   RED_DEFAULT - the color pair used for screens contaning a tile with the player on them (player_present is True)
        

        self.stdscr = stdscr

        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.stdscr.keypad(True)

        self.stdscr.refresh()

        # Windows height ratios
        c.UI_TOP_HEIGHT = 3
        c.UI_BOT_HEIGHT = 1
        c.UI_HEIGHT = c.UI_TOP_HEIGHT + c.UI_BOT_HEIGHT

        height, width = self.stdscr.getmaxyx()

        # Create the top window
        top_height = (height * c.UI_TOP_HEIGHT) // c.UI_HEIGHT
        self.top_win = curses.newwin(top_height, width, 0, 0)
        self.top_win.box()
        self.top_win.refresh()

        # Create a window to display the player view grid
        player_view_win_width = 5 * c.PLAYER_VIEW_X # Because each tile is 5 characters tall and wide
        player_view_win_height = 5 * c.PLAYER_VIEW_Y
        
        left_offset = (width - player_view_win_width) // 2
        top_offset = (top_height - player_view_win_height) // 2

        self.player_view_win = self.top_win.subwin(player_view_win_height, player_view_win_width, top_offset, left_offset)

        # Create a derwin for each tile for the player_view
        self.player_view_tile_grid = [[None for _ in range(c.PLAYER_VIEW_X)] for _ in range(c.PLAYER_VIEW_Y)]
        
        for top_begin in range(0, c.PLAYER_VIEW_Y * 5, 5):
            for left_begin in range(0, c.PLAYER_VIEW_X * 5, 5):
                tile_win = self.player_view_win.derwin(5, 5, top_begin, left_begin)
                self.player_view_tile_grid[top_begin // 5][left_begin // 5] = tile_win
        self.player_view_win.refresh()
        
        # Create the bottom window
        bot_height = height - top_height
        self.bot_win = curses.newwin(bot_height, width, top_height, 0)
        self.bot_win.box()
        self.bot_win.refresh()

        # Create the color pair for players

        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
        self.RED_DEFAULT = curses.color_pair(1)
        

    def refresh_all(self):
        """Refreshes both top and bottom windows"""
        self.top_win.refresh()
        self.bot_win.refresh()

    def update_player_view(self, player_view: list):
        """Updates the player view window with new data and refreshes it to display the results"""
        for row in range(c.PLAYER_VIEW_Y):
            for col in range(c.PLAYER_VIEW_X):
                # For each tile in the player_view_tile_grid
                for i, line in enumerate(player_view[row][col].lines):
                    if player_view[row][col].player_present:
                        self.player_view_tile_grid[row][col].insstr(i, 0, line, self.RED_DEFAULT)
                    else:
                        self.player_view_tile_grid[row][col].insstr(i, 0, line)
                    self.player_view_tile_grid[row][col].refresh()
                    
    
    # Currently not used because I'm using wrapper() instead
    def close(self):
        """Terminates the ui and quits curses mode"""
        curses.echo()
        curses.nocbreak()
        self.stdscr.keypad(False) 
        curses.endwin()
        
    def wait(self):
        """Used for debugging and testing"""
        inp = self.stdscr.getch()
