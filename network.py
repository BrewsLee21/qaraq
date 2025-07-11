import socket
import pickle

import config as c

def send_msg(msg):
    # Status messages are strings
    if type(msg) == str:
        try:
            msg_size_encoded = len(msg).to_bytes(4, "big")
        except OverflowError:
            return -1
        except Exception:
            return -1

        
    
    # Used when sending player_view grids to players
    elif type(msg) == list:
        
        

def create_socket(addr, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((addr, port))
        sock.listen(5)
    except Exception as e:
        print(e)
        return None

    return sock
    
