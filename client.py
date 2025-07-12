import curses
from curses import wrapper
import socket

from utils import print_to_log_file
from network import *

from ui import UI

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
            ui.bot_win.addstr(1, 2, "Error while connecting to server...")
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
        my_move = ui.stdscr.getkey()
        send_msg(my_move, my_sock, length_prefix_size)
        my_view = recv_msg(my_sock, length_prefix_size)
        if type(my_view) == str:
            if my_view == "/NEXT": # REPLACE WITH ERROR CODE
                continue
        ui.update_player_view(my_view)
    
    

if __name__ == "__main__":
    wrapper(main)
