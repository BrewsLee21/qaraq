import curses
from curses import wrapper
import socket

from utils import load_language, print_to_log_file
from network import *
from ui import UI

import status_codes as sc

def main(stdscr):
    # Default language is English
    messages = load_language("en.json")
    ui = UI(stdscr, messages)

    lang_file = ui.get_language()
    if lang_file == '':
        lang_file = "en.json"
    messages = load_language(lang_file)
    ui.update_language(messages)
    ui.lang = lang_file.split('.')[0]

    i_am_dead = False
    
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

    ui.print_msg(messages["status_messages"]["connected"])

    # Receive length_prefix_size form server
    length_prefix_size = int.from_bytes(my_sock.recv(1), "big")

    # Receive my player number from server
    my_number = recv_msg(my_sock, length_prefix_size)

    # Receive my player view
    my_view = recv_msg(my_sock, length_prefix_size)
    ui.update_player_view(my_view)

    ui.initialize_panel_menu()
    ui.main_menu.update()

    # Game Loop
    while True:

        if i_am_dead:
            break
    
        msg = recv_msg(my_sock, length_prefix_size)

        # If it is not my turn and I'm getting a message saying who's turn it is
        if msg in sc.PLAYERS.values():
            p = msg[1:]
            ui.print_msg(messages["status_messages"]["player_turn"].format(p))

        # If I won the game
        elif msg == sc.WIN:
            ui.display_end_screen("win")
            ui.display_info_menu(messages["status_messages"]["you_win"])
            break
        
        # If it is my turn
        elif msg == sc.START:

            my_stats = recv_msg(my_sock, length_prefix_size)
            ui.update_player_stats(my_stats)
            
            ui.print_msg(messages["status_messages"]["turn_start"])
            while True: # Do until server tells me to STOP
                ui.flush_window_input(ui.stdscr)
                my_move = ui.stdscr.getkey()

                # ==== Menu Navigation ====

                # If Tab was pressed
                if my_move == '\t':
                    ui.current_menu.navigate(1)
                    # If inventory_menu was selected, request inventory contents
                    if ui.current_menu == ui.inventory_menu:
                        # Request my inventory from server
                        my_inventory = get_inventory(my_sock, length_prefix_size)
                        ui.current_menu.update(my_inventory)
                        item = ui.current_menu.items[ui.current_menu.position]
                        ui.display_item_desc(item)
                    else:
                        ui.current_menu.update()
                    continue

                # If Shift+Tab was pressed
                elif my_move == "KEY_BTAB":
                    ui.current_menu.navigate(-1)
                    if ui.current_menu == ui.inventory_menu:
                        # Request my inventory from server
                        my_inventory = get_inventory(my_sock, length_prefix_size)
                        ui.current_menu.update(my_inventory)
                        item = ui.current_menu.items[ui.current_menu.position]
                        ui.display_item_desc(item)
                    else:
                        ui.current_menu.update()
                    continue

                # If Enter was pressed
                elif my_move == '\n':
                    # I assume that menu hasn't changed
                    menu_changed = False
                    
                    old_menu = ui.current_menu
                    result = ui.current_menu.run()

                    # If a new menu was selected (ui.current_menu was updated)
                    if ui.current_menu != old_menu:
                        menu_changed = True

                    # If the Exit option was entered
                    if result == -1:
                        if ui.current_menu != ui.main_menu:
                            ui.current_menu = ui.main_menu
                            ui.current_menu.position = 0
                            ui.current_menu.update()
                        else:
                            if ui.are_you_sure("exit"):
                                my_sock.close()
                                return
                            else:
                                ui.current_menu.position = 0
                                ui.current_menu.update()

                    # If the inventory_menu was opened
                    if ui.current_menu == ui.inventory_menu and menu_changed:
                        # Request my inventory from server
                        my_inventory = get_inventory(my_sock, length_prefix_size)
                        # Display the inventory
                        ui.current_menu.update(my_inventory)
                        item = ui.current_menu.items[ui.current_menu.position]
                        ui.display_item_desc(item)
                        

                    # If an item in the inventory_menu was selected
                    if ui.current_menu == ui.inventory_menu and not menu_changed:
                        # If an empty inventory slot was selected
                        if not result:
                            continue

                        # send itemrequest to server
                        send_msg(sc.ITEMREQUEST, my_sock, length_prefix_size)
                        
                        # Send the items index
                        send_msg(str(result), my_sock, length_prefix_size)

                        server_response = recv_msg(my_sock, length_prefix_size)
                        if server_response == sc.AYSREQUEST:
                            action = recv_msg(my_sock, length_prefix_size)

                            response = ui.are_you_sure(action)

                            send_msg(response, my_sock, length_prefix_size)

                            if response == True:
                                new_stats = recv_msg(my_sock, length_prefix_size)
                                ui.update_player_stats(new_stats)
                            
                            ui.current_menu = ui.main_menu
                            ui.main_menu.update()
                    
                    continue

                # =======================
                
                send_msg(my_move, my_sock, length_prefix_size)

                move_result = recv_msg(my_sock, length_prefix_size)
                # If a status message was received
                if type(move_result) == str:
                    # If my move was invalid
                    if move_result == sc.NEXT:
                        ui.print_msg(messages["status_messages"]["invalid_move"])
                        continue
                    elif move_result == sc.AYSREQUEST:
                        new_player_view = recv_msg(my_sock, length_prefix_size)
                        ui.update_player_view(new_player_view)

                        response = ui.are_you_sure("attack")

                        send_msg(response, my_sock, length_prefix_size)
                        print_to_log_file(f"Sent my response: {response}")
                        if response == True:
                            fight_result = recv_msg(my_sock, length_prefix_size)
                            
                            fight_power = fight_result["power"]
                            fight_power_msg = messages["status_messages"]["fight_power"] + str(fight_power)
                            
                            fight_status = messages["status_messages"]["success"] if fight_result["success"] else messages["status_messages"]["fail"]
                            
                            new_item = fight_result["item"]
                            if new_item:
                                new_item_name = messages["items"][new_item.category][new_item.name]
                                new_item_msg = messages["status_messages"]["new_item"] + new_item_name
                                fight_msg = f"{fight_power_msg} | {fight_status} | {new_item_msg}"
                            else:
                                fight_msg = f"{fight_power_msg} | {fight_status}"
                            new_player_view = recv_msg(my_sock, length_prefix_size);

                            # If I died in battle
                            if new_player_view == sc.DEAD:
                                ui.display_end_screen("die")
                                ui.display_info_menu(messages["status_messages"]["you_died"])
                                i_am_dead = True
                                break
                                
                            
                            ui.update_player_view(new_player_view)
                            ui.display_info_menu(fight_msg)

                            new_stats = recv_msg(my_sock, length_prefix_size)
                            ui.update_player_stats(new_stats)

                            ui.main_menu.update()
                            break
                        # If I changed my mind
                        else:
                            new_player_view = recv_msg(my_sock, length_prefix_size);
                            ui.update_player_view(new_player_view)

                            ui.clear_msg_win

                            ui.main_menu.update()
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
                    ui.print_msg(messages["status_messages"]["turn_end"])
                    break
                
        # If it is not my turn and I'm getting updates based on other players' moves
        elif msg == sc.PVUPDATE:
            player_view_update = recv_msg(my_sock, length_prefix_size)
            ui.update_player_view(player_view_update)

if __name__ == "__main__":
    wrapper(main)
