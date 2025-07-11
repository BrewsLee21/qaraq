import curses
from curses import wrapper
import socket

from utils import print_to_log_file
from network import *

from ui import UI

def main(stdscr):
    ui = UI(stdscr)
    server_addr, server_port = ui.get_server_info()

    server_addr = str(server_addr).strip()
    server_port = int(server_port)

    my_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_sock.connect((server_addr, server_port))
    
    ui.bot_win.addstr(1, 2, "Successfully connected to server!")
    ui.bot_win.refresh()
    
    length_prefix_size = int.from_bytes(my_sock.recv(1), "big")

    ui.wait()

    
    
    

if __name__ == "__main__":
    wrapper(main)
