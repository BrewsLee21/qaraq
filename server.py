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

    player_disconnected = False
    disconnected_player = None
    
    # Game Loop
    while True:
        # Check if a player has disconnected
        if player_disconnected:
            players.remove(player)
            player_disconnected = False
        
        # Each player plays on their turn
        for player in players:
            
            print(f"P{player.number}'s turn")

            # Tell every player who's turn it is
            broadcast_turn_taker(players, player)

            # Tell player that their turn started
            send_msg(sc.START, player.player_sock)

            # Process player's amount of moves
            player_moves = player.get_moves()
            i = 0
            while i < player_moves:
                print(f"move {i + 1}")

                # ==== Process The Received Move ====
                
                while True:
                    # Receive move from player
                    player_move = recv_msg(player.player_sock)
                    if not player_move:
                        print("Player disconnected")
                        player_disconnected = True
                        disconnected_player = player
                        break

                    # If player requested their inventory
                    if player_move == sc.INVREQUEST:
                        print("player requested inventory")
                        send_msg(player.get_inventory(), player.player_sock)
                        continue
                    
                    move_status = player.move_in_direction(map_grid, c.KEY_DIRECTIONS[player_move])

                    # If received move is valid
                    if move_status == 0:
                        break
                    # If move is invalid
                    else:
                        print("Received move is invalid")
                        send_msg(sc.NEXT, player.player_sock)
                        continue

                # End player's turn if they disconnected
                if player_disconnected:
                    break
                
                # Calculate new player_view
                new_player_view = get_player_view(map_grid, player.player_x, player.player_y, player.number)

                # Check if player stepped on entity
                if map_grid[player.player_y][player.player_x].entity:
                    # If the entity player stepped on is an enemy
                    if map_grid[player.player_y][player.player_x].entity.entity_type == "enemy":

                        # Send the new player view to player and ask them if they are sure of attacking
                        send_msg(sc.AYSREQUEST, player.player_sock)
                        send_msg(new_player_view, player.player_sock)
                        broadcast_player_view(map_grid, players, player)

                        player_response = recv_msg(player.player_sock)
                        print(f"Received response: {player_response}")
                        if player_response == True:
                            print("Player is sure")
                            fight_result = get_fight_result(player, map_grid[player.player_y][player.player_x].entity)
                            send_msg(fight_result, player.player_sock)
                            
                            # If fight was successful, add the new item to player's inventory
                            if fight_result["success"] == True:
                                map_grid[player.player_y][player.player_x].remove_entity()

                                new_player_view = get_player_view(map_grid, player.player_x, player.player_y, player.number)
                                send_msg(new_player_view, player.player_sock)
                                broadcast_player_view(map_grid, players, player)
                                
                                player.modify_inventory(fight_result["item"])
                            # If fight was not successful
                            else:
                                player.move_back(map_grid)
                                new_player_view = get_player_view(map_grid, player.player_x, player.player_y, player.number)
                                send_msg(new_player_view, player.player_sock)
                                broadcast_player_view(map_grid, players, player)
                            break # End player's turn
                        # If player changed their mind
                        else:
                            print("Player is not sure")
                            player.move_back(map_grid)
                            new_player_view = get_player_view(map_grid, player.player_x, player.player_y, player.number)
                            send_msg(new_player_view, player.player_sock)
                            broadcast_player_view(map_grid, players, player)

                            # Make this move not count
                            continue
                            
                    # If the entity is a healing place
                    elif map_grid[player.player_y][player.player_x].entity.entity_type == "heal":
                        pass

                        
                # ==== Send The Results ====
                
                # Send new player_view to player
                send_msg(new_player_view, player.player_sock)
                # Broadcast the player's moves to other players to update their player_views
                broadcast_player_view(map_grid, players, player)

                # Send turn_status to player
                if i == (player_moves - 1): # If this is was player's last move
                    send_msg(sc.STOP, player.player_sock)
                    break
                else:
                    send_msg(sc.CONTINUE, player.player_sock)
                    i += 1
                    continue

            if player_disconnected:
                break

if __name__ == "__main__":
    main(c.MAP_SIZE)
