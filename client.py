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
            ui.print_msg(str(e))
            my_sock.close()
            continue
        break

    ui.print_msg("Successfully connected to server!")

    # Receive length_prefix_size form server
    length_prefix_size = int.from_bytes(my_sock.recv(1), "big")

    # Receive my player number from server
    my_number = recv_msg(my_sock, length_prefix_size)

    # Receive my player view
    my_view = recv_msg(my_sock, length_prefix_size)
    ui.update_player_view(my_view)


    # Game Loop
    while True:
        msg = recv_msg(my_sock, length_prefix_size)

        # If it is not my turn and I'm getting a message saying who's turn it is
        if msg in sc.PLAYERS.values():
            p = msg[1:]
            ui.print_msg(f"{p}'s turn")
        
        # If it is my turn
        elif msg == sc.START:
            ui.clear_bot_win()
            ui.print_msg("Turn start")
            while True: # Do until server tells me to STOP
                ui.flush_window_input(ui.stdscr)
                my_move = ui.stdscr.getkey()
                send_msg(my_move, my_sock, length_prefix_size)

                move_result = recv_msg(my_sock, length_prefix_size)
                # If a status message was received
                if type(move_result) == str:
                    # If my move was invalid
                    if move_result == sc.NEXT:
                        ui.clear_bot_win()
                        ui.print_msg("Invalid move!")
                        continue
                    else:
                        # SOMETHING WENT WRONG
                        print_to_log_file("move_result received unexpected str value")
                        continue
                
                # If a player_view grid was received
                elif type(move_result) == list:
                    # Update my player_view with the received new one
                    ui.update_player_view(move_result)
                else:
                    # SOMETHING WENT WRONG
                    print_to_log_file("move_result is of unexpected type")
                    continue
                    
                # If my move was valid
                turn_status = recv_msg(my_sock, length_prefix_size)
                if turn_status == sc.CONTINUE:
                    continue
                elif turn_status == sc.STOP:
                    ui.clear_bot_win()
                    ui.print_msg("End of turn")
                    break
        # If it is not my turn and I'm getting updates based on other players' moves
        elif msg == sc.PVUPDATE:
            player_view_update = recv_msg(my_sock, length_prefix_size)
            ui.update_player_view(player_view_update)

if __name__ == "__main__":
    wrapper(main)
