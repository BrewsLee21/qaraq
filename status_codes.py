# ==== Player View ===
PVUPDATE = "/PVUPDATE" # Sent by server to client during broadcasting to update their player views based on the moves of the player who's turn it currently is (only received when not my turn)

# ==== Making Moves ==== 
NEXT = "/NEXT" # Sent by server to client when a move they made is invalid so they don't lose a move
START = "/START" # Sent by server to client to signalize start of their turn
CONTINUE = "/CONTINUE" # Sent by server to client to signalize that they can still play their turn (they have moves left)
STOP = "/STOP" # Sent by server to client to signalize that they have no moves left (indicates end of their turn)
