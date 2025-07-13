import socket

from utils import *
from network import *
from player import Player

import config as c
import status_codes as sc

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

    # Game Loop
    while True:
        # Each player plays on their turn
        for player in players:
            print(f"P{player.number}'s turn'")

            # Tell player that their turn started
            send_msg(sc.START, player.player_sock)

            # Process player's amount of moves
            for i in range(player.base_moves):

                # ==== Process The Received Move ====
                
                while True:
                    # Receive move from player
                    player_move = recv_msg(player.player_sock)
                    move_status = player.move_in_direction(map_grid, c.KEY_DIRECTIONS[player_move])

                    # If received move is valid
                    if move_status == 0:
                        break
                    # If move is invalid
                    else:
                        send_msg(sc.NEXT, player.player_sock)
                        continue
                # Calculate new player_view
                new_player_view = get_player_view(map_grid, player.player_x, player.player_y, player.number)

                # ==== Send The Results ====
                
                # Send new player_view to player
                send_msg(new_player_view, player.player_sock)
                # Broadcast the player's moves to other players to update their player_views
                broadcast_player_view(map_grid, players, player)

                # Send turn_status to player
                if i == (player.base_moves - 1): # If this is was player's last move
                    send_msg(sc.STOP, player.player_sock)
                    break
                else:
                    send_msg(sc.CONTINUE, player.player_sock)
                    continue

if __name__ == "__main__":
    main(c.MAP_SIZE)
