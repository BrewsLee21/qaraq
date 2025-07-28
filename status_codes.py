# ==== Game Synchronization ===
PVUPDATE = "/PVUPDATE" # Sent by server to client during broadcasting to update their player views based on the moves of the player who's turn it currently is (only received when not my turn)

PLAYERS = { # Send by server to all players to indicate which player is now taking their turn
    1: "/P1",
    2: "/P2",
    3: "/P3",
    4: "/P4"
}

DEAD = "/DEAD" # Sent by server to client when client's health goes down to 0
WIN = "/WIN" # Sent tby server to the client that has won the game

# ==== Making Moves ==== 
NEXT = "/NEXT" # Sent by server to client when a move they made is invalid so they don't lose a move
START = "/START" # Sent by server to client to signalize start of their turn
CONTINUE = "/CONTINUE" # Sent by server to client to signalize that they can still play their turn (they have moves left)
STOP = "/STOP" # Sent by server to client to signalize that they have no moves left (indicates end of their turn)

# ==== Client Requests ====
INVREQUEST = "/INVREQUEST" # Sent by client to server to request their inventory
ITEMREQUEST = "/ITEMREQUEST" # Sent by client to server to use (or destroy) an item
STATREQUEST = "/STATREQUEST" # Sent by client to server to request player's stats (power, moves, health, etc.)

# ==== Server Requests ====
AYSREQUEST = "/AYSREQUEST" # Are You Sure Request. Sent by server to client when asking client if they want to perform an action
