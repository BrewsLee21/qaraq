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

    print(f"address: {addr}\nport: {PORT}")
    max_players = int(input("Max players: "))

    center_x, center_y = get_center(map_grid)

    while len(players) != max_players:
        new_conn, new_addr = server_socket.accept()
        print("NEW CLIENT!")

        # Create new player object and append to list of player objects
        new_player = Player(len(players) + 1, new_conn, new_addr, (center_x, center_y))
        players.append(new_player)

        # Handle new connection and send important information
        handle_new_player_connection(map_grid, new_player, c.LENGTH_PREFIX_SIZE)
        
    # Game loop
    while True:
        # Players go one after another
        for player in players: 
            print(f"P{player.number}'s turn")
            # Each player has an amount of moves
            for _ in range(player.base_moves):
                while True:
                    # Receive the move from the player
                    player_move = recv_msg(player.player_sock)
                    move_status = player.move_in_direction(map_grid, c.KEY_DIRECTIONS[player_move])
                    if move_status == 0:
                        break
                    send_msg("/NEXT", player.player_sock)
                # Calculate the new player view
                new_player_view = get_player_view(map_grid, player.player_x, player.player_y, player.number)
                # Send the player view back to the player
                send_msg(new_player_view, player.player_sock)

if __name__ == "__main__":
    main(c.MAP_SIZE)
