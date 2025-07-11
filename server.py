import socket

from network import *

PORT = 8080
addr = socket.gethostbyname(socket.gethostname())

# a list of Player objects
players = []

def main():
    server_socket = create_socket(addr, PORT)

    max_players = input("Max players: ")

    
        

if __name__ == "__main__":
    main()
