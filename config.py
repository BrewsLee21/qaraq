# The width and height of the grid that represents the section of the map grid the player can see
#   Both should be an odd number to make sure there is a center tile
PLAYER_VIEW_X = 3 # Number of collumns
PLAYER_VIEW_Y = 3 # Number of rows

# Height ratio between the top and bottom window of the game UI
UI_TOP_HEIGHT = 3
UI_BOT_HEIGHT = 1
UI_HEIGHT = UI_TOP_HEIGHT + UI_BOT_HEIGHT

# Size (both height and width) of the entire map
MAP_SIZE = 20
# Likelihood of a tile containing a room, the lower the number, the higher the chance of generation
ROOM_LIKELIHOOD = 2

# log file used for debugging information during development
DEBUG_FILE = "debug.log"
# log file used for logging by the server
SERVER_LOG_FILE = "server.log"

KEY_DIRECTIONS = {
    "KEY_LEFT": "left",
    "KEY_UP": "up",
    "KEY_RIGHT": "right",
    "KEY_DOWN": "down"
}

# ==== NETWORKING ====

# Must be 1 byte in size (cannot be larger than 255)
LENGTH_PREFIX_SIZE = 4 

MSG_TYPE_STR = 0 # Used to indicate that the upcoming message is an encoded string
MSG_TYPE_GRID = 1 # Used to indicate that the upcoming message is a pickled 2D list


# ==== MISC ====

LOGO = """
  ____                        
 / __ \                       
| |  | | __ _ _ __ __ _  __ _ 
| |  | |/ _` | '__/ _` |/ _` |
| |__| | (_| | | | (_| | (_| |
 \___\_\\\__,_|_|  \__,_|\__, |
                           | |
                           |_|
"""

LOGO_HEIGHT = len(LOGO.splitlines())
LOGO_WIDTH = max([len(line) for line in LOGO.splitlines()])
