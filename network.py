import socket
import pickle

import config as c
import status_codes as sc
from utils import get_player_view

def send_init_msg(sock):
    """Sends a 1 byte message containing the LENGTH_PREFIX_SIZE to the connected client specified by sock"""
    try:
        data = c.LENGTH_PREFIX_SIZE.to_bytes(1, "big")
        bytes_sent = sock.send(data)
    except Exception:
        return -1

    return bytes_sent

def send_msg(msg, sock, length_prefix_size=c.LENGTH_PREFIX_SIZE):
    """Sends the message specified by msg to the socket connection specified by sock. Returns the number of bytes sent on success or -1 on failure """

    # Status messages are strings
    if type(msg) == str:
        msg_type = c.MSG_TYPE_STR.to_bytes(1, "big")
        msg_encoded = msg.encode()
        try:
            msg_encoded_size = len(msg_encoded).to_bytes(length_prefix_size, "big")
        except OverflowError:
            return -1
        except Exception:
            return -1

        data = msg_type + msg_encoded_size + msg_encoded
        try:
            bytes_sent = sock.send(data)
        except:
            return -1
        
        return bytes_sent
    
    # Used when sending player_view grids to players
    elif type(msg) == list or type(msg) == dict or type(msg) == tuple:
        msg_type = c.MSG_TYPE_OBJ.to_bytes(1, "big")
        pickled_msg = pickle.dumps(msg)
        try:
            pickled_msg_size = len(pickled_msg).to_bytes(length_prefix_size, "big")
        except OverflowError:
            return -1
        except Exception:
            return -1

        data = msg_type + pickled_msg_size + pickled_msg
        bytes_sent = sock.send(data)

        return bytes_sent

    elif type(msg) == bool:
        msg_type = c.MSG_TYPE_BIT.to_bytes(1, "big")
        msg_encoded = b"\x01" if msg else b"\x00"
        msg_encoded_size = len(msg_encoded).to_bytes(length_prefix_size, "big")

        data = msg_type + msg_encoded_size + msg_encoded

        bytes_sent = sock.send(data)

        return bytes_sent

    else:
        return -1

def recv_msg(sock, length_prefix_size=c.LENGTH_PREFIX_SIZE):
    """Receives a message and returns it as either a string or a 2D list, returns -1 on failure"""
    data_type = int.from_bytes(sock.recv(1), "big")
    
    data_len = int.from_bytes(sock.recv(length_prefix_size), "big")
    data = sock.recv(data_len)
    
    if data_type == c.MSG_TYPE_STR:
        return data.decode()
    elif data_type == c.MSG_TYPE_OBJ:
        return pickle.loads(data)
    elif data_type == c.MSG_TYPE_BIT:
        return True if data == b"\x01" else False if data == b"\x00" else -1
    else:
        return -1

def broadcast_turn_taker(players: list, sender):
    """Used to broadcast which player's turn it is"""
    print("Broadcasting turn_taker...")
    for player in players:
        if player != sender:
            bytes_sent = send_msg(sc.PLAYERS[sender.number], player.player_sock)

def broadcast_player_view(map_grid, players: list, sender):
    """Called everytime any player makes a move. Recalculates each player's player_view and sends it to them."""
    print("Broadcasting player_view...")
    for player in players:
        player_view = get_player_view(map_grid, player.player_x, player.player_y, player.number)
        if player != sender:
            bytes_sent = send_msg(sc.PVUPDATE, player.player_sock)
            bytes_sent = send_msg(player_view, player.player_sock)
            

def get_inventory(sock, length_prefix_size=c.LENGTH_PREFIX_SIZE):
    """Called by client to request their current inventory contents"""
    send_msg(sc.INVREQUEST, sock, length_prefix_size)
    my_inventory = recv_msg(sock, length_prefix_size)
    return my_inventory
    
def create_socket(addr, port):
    """Creates a socket, binds it to a given address and port and sets it to listen and then returns the created socket. Returns -1 on error."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((addr, port))
        sock.listen(5)
    except Exception as e:
        print(e)
        return -1

    return sock

def handle_new_player_connection(map_grid, player, length_prefix_size=c.LENGTH_PREFIX_SIZE):
    """Sends important information to newly connected player. Returns 0 on success and -1 on failure"""
    # Append the player to the players present on the center tile
    map_grid[player.player_y][player.player_x].players_present.append(player.number)

    # Send the length_prefix_size
    bytes_sent = send_init_msg(player.player_sock)
    # Send the new player's number
    bytes_sent = send_msg(str(player.number), player.player_sock, length_prefix_size)
    # Calculate and send the new player's view
    player_view = get_player_view(map_grid, player.player_x, player.player_y, player.number)
    send_msg(player_view, player.player_sock)

    return 0
