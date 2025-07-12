import curses
from curses.textpad import Textbox, rectangle

from tile import Tile
from utils import validate_ipaddr, validate_port
import config as c



class UI:
    def __init__(self, stdscr):

        # class variables:
        #   stdscr - standard screen
        #   top_win - top window
        #   bot_win - bottom window
        #   player_view_win - a window containing the grid of visible tiles
        #   player_view_tile_grid - a 2D grid of windows inside player_view_win each representing one tile
        #   player_colors - a dictionary of player_number : player_color pair values
        #   entity_colors - a dictionary of entity : entity_color pair 
        
        curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        
        self.player_colors = {
            1: curses.color_pair(1),
            2: curses.color_pair(2),
            3: curses.color_pair(3),
            4: curses.color_pair(4)
        }
        
        curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_RED, curses.COLOR_BLACK)
        
        self.entity_colors = {
            "chest": curses.color_pair(5),
            "enemy": curses.color_pair(6)
        }
        
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

    def refresh_all(self):
        """Refreshes both top and bottom windows"""
        self.top_win.refresh()
        self.bot_win.refresh()

    def update_player_view(self, player_view: list):
        """Updates the player view window with new data and refreshes it to display the results. caller is the number of the player who called this function to update their player_view"""
        for row in range(c.PLAYER_VIEW_Y):
            for col in range(c.PLAYER_VIEW_X):
                # For each tile in the player_view_tile_grid
                for i, line in enumerate(player_view[row][col].lines):
                    self.player_view_tile_grid[row][col].insstr(i, 0, line)
                    if player_view[row][col].entity and player_view[row][col].entity in self.entity_colors:
                        self.player_view_tile_grid[row][col].insstr(i, 0, line, self.entity_colors[player_view[row][col].entity])
                    if player_view[row][col].players_present:
                        # FIX THIS FOR WHEN THERE'S MORE PLAYERS ON ONE TILE
                        if len(player_view[row][col].players_present) > 1:
                            if caller in player_view[row][col].players_present:
                                self.player_view_tile_grid[row][col].insstr(i, 0, line, self.player_colors[player_view[row][col].players_present[0]])
                        self.player_view_tile_grid[row][col].insstr(i, 0, line, self.player_colors[player_view[row][col].players_present[0]])
                    self.player_view_tile_grid[row][col].refresh()

    def update_bottom_window(self):
        pass

    def get_server_info(self):
        """Used to display the input fields for information used to connect to the server"""
        curses.curs_set(1)
        height, width = self.top_win.getmaxyx()

        input_win_height = height - 2
        input_win_width = width // 2

        top_offset = 1
        left_offset = (width - input_win_width) // 2

        input_win = self.top_win.subwin(input_win_height, input_win_width, top_offset, left_offset)
        input_win.addstr(top_offset, 0, c.LOGO)
        top_offset += c.LOGO_HEIGHT

        input_win.addstr(top_offset, 1, "Server IP address:")
        top_offset += + 1
        ipaddr_win = input_win.derwin(1, input_win_width - 1, top_offset, 1)
        top_offset += 3

        input_win.addstr(top_offset, 1, "Server port:")
        top_offset += 1
        port_win = input_win.derwin(1, input_win_width - 1, top_offset, 1)

        input_win.box()
        input_win.refresh()
        ipaddr_win.refresh()
        port_win.refresh()

        
        ip_box = Textbox(ipaddr_win)
        while True:
            ipaddr_win.move(0, 0)
            ip_box.edit()

            server_addr = ip_box.gather().strip()
            if validate_ipaddr(server_addr):
                break
            self.bot_win.addstr(1, 2, "Entered IP address is invalid")
            self.bot_win.refresh()

            # Clear the invalid input
            ipaddr_win.clear()
            ipaddr_win.refresh()
            
        self.bot_win.clear()
        self.bot_win.box()
        
        port_box = Textbox(port_win)
        while True:
            port_win.move(0, 0)
            port_box.edit()

            server_port = port_box.gather().strip()
            if validate_port(server_port):
                break
            self.bot_win.addstr(1, 2, "Entered port number is invalid")
            self.bot_win.refresh()

            # Clear the invalid input
            port_win.clear()
            port_win.refresh()
        self.bot_win.clear()
        self.bot_win.box()

        curses.curs_set(0)

        self.top_win.clear()
        self.top_win.box()
        self.top_win.refresh()
        return server_addr, server_port
                
    def wait(self):
        """Used for debugging and testing"""
        inp = self.stdscr.getch()
