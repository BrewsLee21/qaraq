import socket
import pickle

import config as c

def send_init_msg(sock):
    """Sends a 1 byte message containing the LENGTH_PREFIX_SIZE to the connected client specified by sock"""
    try:
        data = c.LENGTH_PREFIX_SIZE.to_bytes(1, "big")
        bytes_sent = sock.send(data)
    except Exception:
        return -1

    return bytes_sent

def send_msg(msg, sock):
    """Sends the message specified by msg to the socket connection specified by sock. Returns the number of bytes sent on success or -1 on failure """
    # Status messages are strings
    if type(msg) == str:
        msg_encoded = msg.encode()
        try:
            msg_encoded_size = len(msg_encoded).to_bytes(c.LENGTH_PREFIX_SIZE, "big")
        except OverflowError:
            return -1
        except Exception:
            return -1

        data = msg_encoded_size + msg_encoded
        bytes_sent = sock.send(data)
        
        return bytes_sent
    
    # Used when sending player_view grids to players
    elif type(msg) == list:
        pickled_msg = pickle.dumps(msg)
        try:
            pickled_msg_size = len(pickled_msg).to_bytes(c.LENGTH_PREFIX_SIZE, "big")
        except OverflowError:
            return -1
        except Exception:
            return -1

        data = pickled_msg_size + pickled_msg
        bytes_sent = sock.send(data)

        return bytes_sent

    else:
        return -1

def broadcast(msg, players: list):
    """Sends a message specified by msg to all player sockets in the players list"""
    for player in players:
        bytes_sent = send_msg(msg, player.player_socket)

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
    
