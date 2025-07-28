# ==== GAME ====

# The width and height of the grid that represents the section of the map grid the player can see
#   Both should be an odd number to make sure there is a center tile
PLAYER_VIEW_X = 11 # Number of collumns
PLAYER_VIEW_Y = 5 # Number of rows

# Height ratio between the top and bottom window of the game UI
UI_TOP_HEIGHT = 3
UI_BOT_HEIGHT = 1
UI_HEIGHT = UI_TOP_HEIGHT + UI_BOT_HEIGHT

MESSAGE_WIN_HEIGHT = 2

# Size (both height and width) of the entire map
MAP_SIZE = 100
# Likelihood of a tile containing a room, the lower the number, the higher the chance of generation
ROOM_LIKELIHOOD = 3

ENEMY_LIKELIHOOD = 6 # Likelihood of the enemy entity appearing on a tile with a room
CHEST_LIKELIHOOD = 1 # Likelihood of the chest entity appearing
HEAL_LIKELIHOOD = 1  # Likelihood of the heal entity

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
MSG_TYPE_OBJ = 1 # Used to indicate that the upcoming message is a pickled list, dictionary or tuple
MSG_TYPE_BIT = 2 # Used to indicate that the upcoming message is a True/False value
#MSG_TYPE_INT = 3 # Used to indicate that the upcoming message is an integer

# ==== MISC ====

LANG_DIR = "lang/"

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

END_SCREENS = {
    "YOU_DIED": {
        "en": """
 __     __           _____  _          _ 
 \ \   / /          |  __ \(_)        | |
  \ \_/ /__  _   _  | |  | |_  ___  __| |
   \   / _ \| | | | | |  | | |/ _ \/ _` |
    | | (_) | |_| | | |__| | |  __/ (_| |
    |_|\___/ \__,_| |_____/|_|\___|\__,_|
""",
        "cs": """
  ______                       _     _     _ 
 |___  /                      | |   (_)   (_)
    / / ___ _ __ ___  _ __ ___| |    _ ___ _ 
   / / / _ \ '_ ` _ \| '__/ _ \ |   | / __| |
  / /_|  __/ | | | | | | |  __/ |   | \__ \ |
 /_____\___|_| |_| |_|_|  \___|_|   | |___/_|
                                   _/ |      
                                  |__/       
"""
    },
    "YOU_WIN": {
        "en": """
 __     __          __          ___       _ 
 \ \   / /          \ \        / (_)     | |
  \ \_/ /__  _   _   \ \  /\  / / _ _ __ | |
   \   / _ \| | | |   \ \/  \/ / | | '_ \| |
    | | (_) | |_| |    \  /\  /  | | | | |_|
    |_|\___/ \__,_|     \/  \/   |_|_| |_(_)
""",
        "cs": """
 __      __    _               _     _     _ _ 
 \ \    / /   | |             | |   (_)   (_) |
  \ \  / /   _| |__  _ __ __ _| |    _ ___ _| |
   \ \/ / | | | '_ \| '__/ _` | |   | / __| | |
    \  /| |_| | | | | | | (_| | |   | \__ \ |_|
     \/  \__, |_| |_|_|  \__,_|_|   | |___/_(_)
          __/ |                    _/ |        
         |___/                    |__/         
"""
    }
}
