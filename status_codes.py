# ==== Game Initialization ====
DONE  ="/DONE" # Sent by server to all clients when all players are connected and the game can start

# ==== Game Synchronization ===
PVUPDATE = "/PVUPDATE" # Sent by server to client during broadcasting to update their player views based on the moves of the player who's turn it currently is (only received when not my turn)

PLAYERS = { # Send by server to all players to indicate that a specific player is now taking their turn
    1: "/P1",
    2: "/P2",
    3: "/P3",
    4: "/P4"
}

# ==== Making Moves ==== 
NEXT = "/NEXT" # Sent by server to client when a move they made is invalid so they don't lose a move
START = "/START" # Sent by server to client to signalize start of their turn
CONTINUE = "/CONTINUE" # Sent by server to client to signalize that they can still play their turn (they have moves left)
STOP = "/STOP" # Sent by server to client to signalize that they have no moves left (indicates end of their turn)
