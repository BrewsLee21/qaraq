import socket

from utils import *
from network import *
from player import Player
import config as c

PORT = 8080
addr = socket.gethostbyname(socket.gethostname())

# a list of Player objects
players = []

def main(map_size):
    server_socket = create_socket(addr, PORT)

    map_grid = generate_map_grid(map_size)
    if map_grid == -1:
        print("MAP_SIZE must be larger than 0!")
        return

    max_players = input("Max players: ")

    while len(players) != max_players:
        new_conn, new_addr = server_socket.accept()

        players.append(Player(len(players), new_conn, new_addr, get_center(map_grid)))
        bytes_send = send_init_msg(new_conn)

    broadcast("/START")
        
    
        

if __name__ == "__main__":
    main(c.MAP_SIZE)
