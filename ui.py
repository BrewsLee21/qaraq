import curses
from curses import panel
from curses.textpad import Textbox

from tile import Tile
from entities import Enemy, Chest, Heal
from utils import validate_ipaddr, validate_port, validate_lang_file, get_lang_files, print_to_log_file
import config as c

class UI:
    def __init__(self, stdscr, messages):

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
            Chest: curses.color_pair(5),
            Enemy: curses.color_pair(6)
        }
        
        self.stdscr = stdscr
        self.messages = messages
        
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.stdscr.keypad(True)

        self.stdscr.refresh()

        height, width = self.stdscr.getmaxyx()

        self.screen_height = height
        self.screen_width = width

        # Create the top window
        top_height = ((height * c.UI_TOP_HEIGHT) // c.UI_HEIGHT) - c.MESSAGE_WIN_HEIGHT
        self.top_win = curses.newwin(top_height, width, 0, 0)

        # Add borders
        self.top_win.border(
            curses.ACS_VLINE,
            curses.ACS_VLINE,
            curses.ACS_HLINE,
            curses.ACS_HLINE,
            curses.ACS_ULCORNER,
            curses.ACS_URCORNER,
            curses.ACS_LTEE,
            curses.ACS_RTEE
        )
        
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

        # Create the message window
        self.message_win = curses.newwin(c.MESSAGE_WIN_HEIGHT, width, top_height, 0)
        self.message_win.vline(0, 0, curses.ACS_VLINE, 1) # This line throws an error
        self.message_win.vline(0, width - 1, curses.ACS_VLINE, 1)
        self.message_win.refresh()
        
        # Create the bottom window
        bot_height = height - (top_height + c.MESSAGE_WIN_HEIGHT)
        self.bot_win = curses.newwin(bot_height, width, top_height + c.MESSAGE_WIN_HEIGHT, 0)
        # Add borders
        self.bot_win.border(
            curses.ACS_VLINE,
            curses.ACS_VLINE,
            curses.ACS_HLINE,
            curses.ACS_HLINE,
            curses.ACS_LTEE,
            curses.ACS_RTEE,
            curses.ACS_LLCORNER,
            curses.ACS_LRCORNER
        )
        self.bot_win.refresh()

    def update_language(self, messages):
        self.messages = messages

    class Menu:
        def __init__(self, items, bot_win, caller):
            self.menu_window = bot_win
            self.menu = panel.new_panel(bot_win)
            self.menu.hide()
            panel.update_panels()

            self.position = 0
            self.items = items
            self.items.append((caller.messages["menu_options"]["exit"], "Exit"))

            self.caller_UI = caller

        def navigate(self, n):
            self.position += n
            if self.position < 0:
                self.position = len(self.items) - 1
            elif self.position == len(self.items):
                self.position = 0

        def update(self):
            self.menu.top()
            self.menu.show()
            self.menu_window.clear()

            menu_win_height, menu_win_width = self.menu_window.getmaxyx()
            menu_win_middle_height = menu_win_height // 2

            offset = 2
            
            for index, item in enumerate(self.items):
                if index == self.position:
                    mode = curses.A_REVERSE
                else:
                    mode = curses.A_NORMAL
                    
                self.menu_window.addstr(menu_win_middle_height, offset, item[0], mode)

                offset += len(item[0]) + 2

            panel.update_panels()
            curses.doupdate()
            
            # Fix the border
            UI.bot_win_border(self.caller_UI)

        # Call bot_win_border() after calling this function to fix the bot_win borders
        def display(self):
            self.menu.top()
            self.menu.show()
            self.menu_window.clear()

            self.update()

        def run(self):
            """Returns 0 if exit was entered, otherwise returns 1"""
            if self.position == len(self.items) - 1:
                return 0
            else:
                self.caller_UI.current_menu = self.items[self.position][1]
                self.caller_UI.current_menu.position = 0
                self.caller_UI.current_menu.display()
                return 1

    def initialize_panel_menu(self, player_inventory = None):
        """Initializes the Menu class to create some menus"""
        self.invetory_menu = self.Menu([("Beep", curses.beep)], self.bot_win, self)

        main_menu_items = [
            (self.messages["menu_options"]["items"], self.inventory_menu),
            #(self.messages["menu_options"]["abilities"], self.abilities_menu)
        ]
        self.main_menu = UI.Menu(main_menu_items, self.bot_win, self)
        self.main_menu.display()
        self.current_menu = self.main_menu

    def flush_window_input(self, win):
        """Used to flush all the input that the user may have buffered by pressing keys when not playing their turn"""
        print_to_log_file("Flushing...")
        win.nodelay(True)
        while win.getch() != -1:
            pass
        win.nodelay(False)

    def print_msg(self, msg):
        """Used to print messages into the message_win"""
        # Clear the window first
        self.message_win.move(0, 0)
        self.message_win.clrtoeol()
        self.message_win.vline(0, 0, curses.ACS_VLINE, 1) # This line throws an error
        self.message_win.vline(0, self.screen_width - 1, curses.ACS_VLINE, 1)

        self.message_win.addstr(0, 2, msg)
        self.message_win.refresh()

    def top_win_border(self):
        """Displays a border for the top window, makes sure it blends in with message_win"""
        self.top_win.border(
            curses.ACS_VLINE,
            curses.ACS_VLINE,
            curses.ACS_HLINE,
            curses.ACS_HLINE,
            curses.ACS_ULCORNER,
            curses.ACS_URCORNER,
            curses.ACS_LTEE,
            curses.ACS_RTEE)
        self.top_win.refresh()

    def bot_win_border(self):
        """Displays a border for the bottom window, makes sure it blends in with message_win"""
        self.bot_win.border(
            curses.ACS_VLINE,
            curses.ACS_VLINE,
            curses.ACS_HLINE,
            curses.ACS_HLINE,
            curses.ACS_LTEE,
            curses.ACS_RTEE,
            curses.ACS_LLCORNER,
            curses.ACS_LRCORNER)
        self.bot_win.refresh()

    def update_player_view(self, player_view: list):
        """Updates the player view window with new data and refreshes it to display the results. caller is the number of the player who called this function to update their player_view"""
        for row in range(c.PLAYER_VIEW_Y):
            for col in range(c.PLAYER_VIEW_X):
                # For each tile in the player_view_tile_grid
                for i, line in enumerate(player_view[row][col].lines):
                    self.player_view_tile_grid[row][col].insstr(i, 0, line)
                    # Color entity tiles
                    if player_view[row][col].entity and type(player_view[row][col].entity) in self.entity_colors:
                        self.player_view_tile_grid[row][col].insstr(i, 0, line, self.entity_colors[type(player_view[row][col].entity)])
                    # Color player tiles
                    if player_view[row][col].players_present:
                        if len(player_view[row][col].players_present) > 1:
                            if caller in player_view[row][col].players_present:
                                self.player_view_tile_grid[row][col].insstr(i, 0, line, self.player_colors[player_view[row][col].players_present[0]])
                        self.player_view_tile_grid[row][col].insstr(i, 0, line, self.player_colors[player_view[row][col].players_present[0]])
                    self.player_view_tile_grid[row][col].refresh()

    def get_language(self):
        curses.curs_set(1)
        height, width = self.top_win.getmaxyx()

        input_win_height = height - 2
        input_win_width = width // 2

        top_offset = 1 # One line from the top edge
        left_offset = (width - input_win_width) // 2 # To make sure input_win is in the middle of the screen

        input_win = self.top_win.subwin(input_win_height, input_win_width, top_offset, left_offset)

        lang_files = get_lang_files()
        input_win.addstr(top_offset, 1, self.messages["input_win_messages"]["available_languages"])
        top_offset += 1
        for lang_f in lang_files:
            input_win.addstr(top_offset, 1, lang_f)
            top_offset += 1
        top_offset += 1

        input_win.addstr(top_offset, 1, self.messages["input_win_messages"]["lang"])
        top_offset += + 1
        lang_win = input_win.derwin(1, input_win_width - 1, top_offset, 1)

        input_win.refresh()
        lang_win.refresh()

        lang_box = Textbox(lang_win)

        while True:
            lang_win.move(0, 0)
            lang_box.edit()

            lang_file = lang_box.gather().strip()
            if validate_lang_file(lang_file):
                break
            self.print_msg(self.messages["input_win_messages"]["invalid_lang"])

            # Clear the invalid input
            lang_win.clear()
            lang_win.refresh()

        input_win.clear()
        return lang_file

    def get_server_info(self):
        """Used to display the input fields for information used to connect to the server"""
        curses.curs_set(1)
        height, width = self.top_win.getmaxyx()

        input_win_height = height - 2
        input_win_width = width // 2

        top_offset = 1 # One line from the top edge
        left_offset = (width - input_win_width) // 2 # To make sure input_win is in the middle of the screen

        input_win = self.top_win.subwin(input_win_height, input_win_width, top_offset, left_offset)

        logo_win_height = c.LOGO_HEIGHT
        logo_win_width = c.LOGO_WIDTH

        left_offset = (input_win_width - logo_win_width) // 2
        
        logo_win = input_win.derwin(logo_win_height + 1, logo_win_width + 1, top_offset, left_offset)
        logo_win.addstr(c.LOGO)
        top_offset += c.LOGO_HEIGHT

        input_win.addstr(top_offset, 1, self.messages["input_win_messages"]["server_ip"])
        top_offset += + 1
        ipaddr_win = input_win.derwin(1, input_win_width - 1, top_offset, 1)
        top_offset += 3

        input_win.addstr(top_offset, 1, self.messages["input_win_messages"]["server_port"])
        top_offset += 1
        port_win = input_win.derwin(1, input_win_width - 1, top_offset, 1)
        
        input_win.refresh()
        logo_win.refresh()
        ipaddr_win.refresh()
        port_win.refresh()

        
        ip_box = Textbox(ipaddr_win)
        while True:
            ipaddr_win.move(0, 0)
            ip_box.edit()

            server_addr = ip_box.gather().strip()
            if validate_ipaddr(server_addr):
                break
            self.print_msg(self.messages["input_win_messages"]["invalid_ip"])

            # Clear the invalid input
            ipaddr_win.clear()
            ipaddr_win.refresh()
                
        port_box = Textbox(port_win)
        while True:
            port_win.move(0, 0)
            port_box.edit()

            server_port = port_box.gather().strip()
            if validate_port(server_port):
                break
            self.print_msg(self.messages["input_win_messages"]["invalid_port"])

            # Clear the invalid input
            port_win.clear()
            port_win.refresh()

        curses.curs_set(0)

        self.top_win.clear()
        self.top_win_border()
        return server_addr, server_port
                
    def wait(self):
        """Used for debugging and testing"""
        inp = self.stdscr.getch()
