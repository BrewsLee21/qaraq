import curses
from curses import wrapper
import socket

from utils import print_to_log_file
from network import *
from ui import UI

import status_codes as sc

def main(stdscr):
    ui = UI(stdscr)
    while True:
        server_addr, server_port = ui.get_server_info()

        server_addr = str(server_addr).strip()
        server_port = int(server_port)

        my_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            my_sock.connect((server_addr, server_port))
        except Exception as e:
            ui.bot_win.addstr(1, 2, str(e))
            ui.bot_win.refresh()
            my_sock.close()
            continue
        break
    
    ui.bot_win.addstr(1, 2, "Successfully connected to server!")
    ui.bot_win.refresh()

    # Receive length_prefix_size form server
    length_prefix_size = int.from_bytes(my_sock.recv(1), "big")

    # Receive my player number from server
    my_number = recv_msg(my_sock, length_prefix_size)

    # Receive my player view
    my_view = recv_msg(my_sock, length_prefix_size)
    ui.update_player_view(my_view)

    # Game loop
    while True:
        msg = recv_msg(my_sock, length_prefix_size)
        # If it's my turn
        if msg == sc.START:
            my_move = ui.stdscr.getkey()
            while True: # Do until end of my turn
                send_msg(my_move, my_sock, length_prefix_size)
                player_view_update = recv_msg(my_sock, length_prefix_size)

                # If a status message was received
                if type(player_view_update) == str:
                    if player_view_update == sc.NEXT:
                        # UI - ivalid move!
                        my_move = ui.stdscr.getkey()
                        continue
                    elif player_view_update == sc.STOP:
                        break
                # If a player_view update was received
                elif type(player_view_update) == list:
                    ui.update_player_view(player_view_update)
                else:
                    pass # SOMETHING WENT WRONG!
                my_move = ui.stdscr.getkey()
        # If it's another player's turn and I'm getting updates of their movements
        elif msg == sc.PVUPDATE:
            player_view_update = recv_msg(my_sock, length_prefix_size)
            ui.update_player_view(player_view_update)
    
    

if __name__ == "__main__":
    wrapper(main)
