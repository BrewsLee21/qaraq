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
        self.lang = ""
        
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.stdscr.keypad(True)

        self.stdscr.refresh()

        height, width = self.stdscr.getmaxyx()

        self.screen_height = height
        self.screen_width = width

        # Create the top window
        top_height = ((height * c.UI_TOP_HEIGHT) // c.UI_HEIGHT)
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
        self.message_win.vline(0, 0, curses.ACS_VLINE, c.MESSAGE_WIN_HEIGHT) # This line throws an error
        self.message_win.vline(0, width - 1, curses.ACS_VLINE, c.MESSAGE_WIN_HEIGHT)
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

    def clear_msg_win(self):
        self.print_msg("")

    def display_item_desc(self, item):
        if not item or type(item) == str:
            self.clear_msg_win()
        else:
            # Print the description of the item
            self.print_msg(self.messages["items"][item.category][item.name + "_desc"])

    def display_end_screen(self, msg):

        end_screens = {
            "die": c.END_SCREENS["YOU_DIED"],
            "win": c.END_SCREENS["YOU_WIN"]
        }

        if msg not in end_screens:
            return -1
        
        self.top_win.clear()

        height, width = self.top_win.getmaxyx()

        if self.lang == "en":
            message = end_screens[msg]["en"]
        elif self.lang == "cs":
            message = end_screens[msg]["cs"]
        else:
            return -1

        message_width = 0
        for line in message:
            if len(line) > message_width:
                message_width = len(line)

        top_offset = 10
        left_offset = (width - message_width) // 2

        self.top_win.addstr(top_offset, left_offset, message)

        self.top_win_border()
    
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

        def run(self):
            """Returns -1 if exit was selected, othewise modifies the current_menu variable and returns 1"""
    
            # If the Exit button is pressed
            if self.position == len(self.items) - 1:
                return -1   
            else:
                self.caller_UI.current_menu = self.items[self.position][1]
                self.caller_UI.current_menu.position = 0
                return 1

    class InventoryMenu(Menu):
        def update(self, player_inventory):
            # player_inventory - dictionary
            # self.items - a list of Item class instances
            
            inventory_items = [item for sublist in player_inventory.values() for item in sublist]
            
            self.items = inventory_items
            self.items.append("exit")
            
            self.menu.top()
            self.menu.show()
            self.menu_window.clear()

            left_offset = 2
            index = 0
            for key in player_inventory:
                line = 1
                self.menu_window.addstr(line, left_offset, self.caller_UI.messages["items"]["categories"][key])
                line += 1
                max_item_len = len(self.caller_UI.messages["items"]["categories"][key])
                for item in player_inventory[key]:
                    if item:
                        if len(self.caller_UI.messages["items"][key][item.name]) > max_item_len:
                            max_item_len = len(self.caller_UI.messages["items"][key][item.name])
                    if index == self.position:
                        mode = curses.A_REVERSE
                    else:
                        mode = curses.A_NORMAL
                        
                    if not item:
                        item = '_'
                        self.menu_window.addstr(line, left_offset + 1, item, mode)
                    else:
                        self.menu_window.addstr(line, left_offset + 1, self.caller_UI.messages["items"][key][item.name], mode)
                    index += 1
                    line += 1
                left_offset += max_item_len + 2
            if index == self.position:
                mode = curses.A_REVERSE
            else:
                mode = curses.A_NORMAL
            self.menu_window.addstr(1, left_offset + 2, self.caller_UI.messages["menu_options"]["exit"], mode)
                
            panel.update_panels()
            curses.doupdate()
            
            # Fix the border
            UI.bot_win_border(self.caller_UI)

        def run(self):
            # If the Exit button is pressed
            if self.position == len(self.items) - 1:
                return -1
            else:
                # Return None if inventory slot is empty
                if not self.items[self.position]:
                    return None
                # Return the index of the selected item
                return self.position

    class AreYouSureMenu(Menu):
        def update(self):
            self.items = [
                (self.caller_UI.messages["menu_options"]["yes"], True),
                (self.caller_UI.messages["menu_options"]["no"], False)
            ]

            self.menu.top()
            self.menu.show()
            self.menu_window.clear()

            left_offset = 3
            
            for index, item in enumerate(self.items):
                if index == self.position:
                    mode = curses.A_REVERSE
                else:
                    mode = curses.A_NORMAL

                self.menu_window.addstr(3, left_offset, item[0], mode)
                left_offset += 5

            panel.update_panels()
            curses.doupdate()
            
            # Fix the border
            UI.bot_win_border(self.caller_UI)

        def run(self):
            return self.items[self.position][1]

    class InfoMenu(Menu):
        def update(self):    
            self.menu.top()
            self.menu.show()
            self.menu_window.clear()

            left_offset = 3
            
            self.menu_window.addstr(3, left_offset, "OK", curses.A_REVERSE)

            panel.update_panels()
            curses.doupdate()
            
            # Fix the border
            UI.bot_win_border(self.caller_UI)

        def run(self):
            return True

    class FightResultInfoMenu(InfoMenu):
        def update(self, fight_result):
            self.menu.top()
            self.menu.show()
            self.menu_window.clear()

            top_offset = 1
            left_offset = 1

            self.menu_window.addstr(top_offset, left_offset, self.caller_UI.messages["status_messages"]["power"] + str(fight_result["power"]))
            top_offset += 1
            self.menu_window.addstr(top_offset, left_offset, self.caller_UI.messages["status_messages"]["extra_power"] + str(fight_result["extra_power"]))
            if fight_result["success"] == True:
                top_offset += 1
                self.menu_window.addstr(top_offset, left_offset, self.caller_UI.messages["status_messages"]["new_item"] + self.caller_UI.messages["items"][fight_result["item"].category][fight_result["item"].name])
                top_offset += 2
            else:
                top_offset += 3

            left_offset = 3
            self.menu_window.addstr(top_offset, left_offset, "OK", curses.A_REVERSE)

            panel.update_panels()
            curses.doupdate()

            UI.bot_win_border(self.caller_UI)
                
    def initialize_panel_menu(self):
        """Initializes the Menu class to create some menus"""
        self.inventory_menu = self.InventoryMenu([], self.bot_win, self)
        self.ays_menu = self.AreYouSureMenu([], self.bot_win, self)
        self.info_menu = self.InfoMenu([], self.bot_win, self)
        self.fight_result_info_menu = self.FightResultInfoMenu([], self.bot_win, self)
        
        main_menu_items = [
            (self.messages["menu_options"]["items"], self.inventory_menu),
        ]
        self.main_menu = UI.Menu(main_menu_items, self.bot_win, self)
        self.main_menu.update()
        self.current_menu = self.main_menu

    def are_you_sure(self, msg_action):
        """Print a 'are you sure?' message. Returns True if the user was sure and False if the user wasn't"""
        self.print_msg(self.messages["menu_options"]["are_you_sure"] + self.messages["menu_options"]["actions"][msg_action])
        self.ays_menu.position = 1
        self.ays_menu.update()
        while True:
            my_move = self.stdscr.getkey()

            if my_move == '\t':
                self.ays_menu.navigate(1)
            elif my_move == "KEY_BTAB":
                self.ays_menu.navigate(-1)
            elif my_move == '\n':
                return self.ays_menu.run()
                    
            self.ays_menu.update()

    def display_info_menu(self, msg):
        """Display a message into message_win and wait for use to select OK"""
        self.print_msg(msg)
        self.info_menu.position = 0
        self.info_menu.update()
        while True:
            my_move = self.stdscr.getkey()
            if my_move == '\n':
                return self.info_menu.run()
                
    def display_fight_result_info_menu(self, fight_result):
        """Displays the result of the fight in the bot_win, not in the msg_win"""
        fight_status = self.messages["status_messages"]["success"] if fight_result["success"] == True else self.messages["status_messages"]["fail"]
        self.print_msg(fight_status)
        self.fight_result_info_menu.position = 0
        self.fight_result_info_menu.update(fight_result)
        while True:
            my_move = self.stdscr.getkey()
            if my_move == '\n':
                return self.fight_result_info_menu.run()
        
    def flush_window_input(self, win):
        """Used to flush all the input that the user may have buffered by pressing keys when not playing their turn"""
        win.nodelay(True)
        while win.getch() != -1:
            pass
        win.nodelay(False)

    def print_msg(self, msg):
        """Used to print messages into the message_win"""
        # Clear the window first
        self.message_win.move(0, 0)
        self.message_win.clrtoeol()
        self.message_win.vline(0, 0, curses.ACS_VLINE, c.MESSAGE_WIN_HEIGHT) # This line throws an error
        self.message_win.vline(0, self.screen_width - 1, curses.ACS_VLINE, c.MESSAGE_WIN_HEIGHT)
        
        self.message_win.addstr(0, 2, msg)
        self.message_win.refresh()

    def update_player_stats(self, player_stats):
        """Prints the player stats specified by the player_stats dictionary"""

        self.message_win.move(1, 0)
        self.message_win.clrtoeol()
        self.message_win.vline(0, 0, curses.ACS_VLINE, c.MESSAGE_WIN_HEIGHT) # This line throws an error
        self.message_win.vline(0, self.screen_width - 1, curses.ACS_VLINE, c.MESSAGE_WIN_HEIGHT)

        power_stat = f"{self.messages['player_stats']['power']}: +{player_stats['extra_power']} | "
        moves_stat = f"{self.messages['player_stats']['moves']}: {player_stats['base_moves']}+{player_stats['extra_moves']} | "
        health_stat = f"{self.messages['player_stats']['health']}: {player_stats['health']}"

        stats_msg = power_stat + moves_stat + health_stat

        self.message_win.addstr(c.MESSAGE_WIN_HEIGHT - 1, 2, stats_msg)
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
