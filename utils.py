import random
import json
from os import listdir
from os.path import isfile

from tile import Tile, TILE_DIRECTIONS
import config as c
from entities import ENTITIES, ENTITY_LIKELIHOODS, Enemy, Chest, Heal
from items import generate_item

# ============= Debugging and Utility =============

def print_to_log_file(s: str):
    with open(c.DEBUG_FILE, 'a') as f:
        print(s, file=f)

def load_language(filename):
    """Returns messages in a certain language based on given json file"""
    with open(c.LANG_DIR + filename, 'r', encoding="utf-8") as f:
        messages = json.load(f)
    return messages

def get_center(map_grid):
    """Takes the generated map grid and returns the coordinates of the center tile as a tuple of x and y values"""
    return ((len(map_grid[0]) - 1) // 2, (len(map_grid) - 1) // 2)

def get_lang_files():
    """Returns a list of all files in the LANG_DIR directory"""
    lang_files = [f for f in listdir(c.LANG_DIR) if isfile(c.LANG_DIR + f)]
    return lang_files

def validate_lang_file(filename):
    """Checks if a language JSON file exists. Returns True if it does, False if it does not"""
    return isfile(c.LANG_DIR + filename) or filename == ''

def validate_ipaddr(ipaddr: str):
    """Returns True if given ipaddr is a valid IPv4 address, otherwise returns False"""
    # Check ipaddr length
    if not ipaddr or len(ipaddr) > 15 or len(ipaddr) < 7:
        print_to_log_file("bad length")
        return False
    # Check for invalid characters
    for c in ipaddr:
        if not c.isdigit() and c != '.':
            print_to_log_file("bad character")
            return False
    # Check for invalid octet sizes
    octets = ipaddr.split('.')
    if len(octets) != 4:
        return False
        
    for octet in octets:
        if not octet:
            return False
        if len(octet) > 1 and octet.startswith('0'):
            return False
        if int(octet) > 255:
            return False
        if len(octet) > 3 or not octet:
            print_to_log_file("Bad octet")
            return False
    return True

def validate_port(port: str):
    """Returns True if given port is valid, otherwise returns False"""

    if not port:
        return False

    for c in port:
        if not c.isdigit():
            return False
            
    if int(port) < 1024 or int(port) > 65535:
        return False

    return True

# ========================================================

# ============= Map Rendering and Generation =============

def get_direction_opposite(direction: str):
    """Returns the opposite of a given direction"""
    return "up" if direction == "down" else "down" if direction == "up" else "left" if direction == "right" else "right" if direction == "left" else "ERROR"

def check_adjacent_tiles(map_grid, tile_x, tile_y):
    """Returns a list containing the required exit directions the current tile needs to have in order to connect to the adjecent tiles"""
        
    required_directions = []

    # Check the left tile
    if tile_x > 0: # If current tile is not at the left edge
        left_tile = map_grid[tile_y][tile_x - 1]
        if left_tile: # If adjacent tile already exists
            if "right" in left_tile.directions:
                required_directions.append(get_direction_opposite("right"))
    # Check the top tile
    if tile_y > 0: # If current tile is not at the top edge
        top_tile = map_grid[tile_y - 1][tile_x]
        if top_tile:
            if "down" in top_tile.directions:
                required_directions.append(get_direction_opposite("down"))
    # Check the right tile
    if tile_x < (len(map_grid[0]) - 1): # If current tile is not at the right edge
        right_tile = map_grid[tile_y][tile_x + 1]
        if right_tile:
            if "left" in right_tile.directions:
                required_directions.append(get_direction_opposite("left"))
    # Check the bottom tile
    if tile_y < (len(map_grid) - 1): # If current tile is not at the bottom edge
        bottom_tile = map_grid[tile_y + 1][tile_x]
        if bottom_tile:
            if "up" in bottom_tile.directions:
                required_directions.append(get_direction_opposite("up"))
    return required_directions

def get_invalid_directions(map_grid: list, tile_x: int, tile_y: int):
    """Checks whether a tile is at the edge of the map and returns a list of invalid directions"""

    invalid_directions = []

    if tile_x == 0: # Tile is at the left edge
        invalid_directions.append("left")
    if tile_y == 0: # Tile is at the top edge
        invalid_directions.append("up")
    if tile_x == (len(map_grid[0]) - 1): # Tile is at the right edge
        invalid_directions.append("right")
    if tile_y == (len(map_grid) - 1): # Tile is at the bottom edge
        invalid_directions.append("down")

    return invalid_directions

def get_possible_new_tiles(required_directions, invalid_directions):
    """Returns a list of possible new tiles based on given required directions and invalid directions"""
    
    possible_tiles = []
    
    for tile_type, tile_directions in TILE_DIRECTIONS.items(): # test if each tile has all the required directions, if it does, add it to the possible_tiles list
        tile_is_valid = True
        for required_dir in required_directions: # check if each required direction is included in the tested tile
            if required_dir not in tile_directions:
                tile_is_valid = False
                break
        for invalid_dir in invalid_directions:
            if invalid_dir in tile_directions:
                tile_is_valid = False
                break
        if tile_is_valid: 
            possible_tiles.append(tile_type)
    return possible_tiles
            
                
def get_new_coordinates(map_grid: list, current_tile: Tile, direction: str):
    """Returns new coordinates after moving one tile in a given direction"""

    offsets = {
        "left":  (0, -1),
        "up":    (-1, 0),
        "right": (0, 1),
        "down":  (1, 0)
    }

    if direction not in offsets:
        raise ValueError("invalid direction")
    
    dy, dx = offsets[direction]
    new_y = current_tile.coordinate_y + dy
    new_x = current_tile.coordinate_x + dx

    if 0 <= new_y < len(map_grid) and 0 <= new_x < len(map_grid[0]):
        return (new_x, new_y)
    return None

def fix_possible_directions(map_grid, tile: Tile):
    """Takes a tile object and checks and fixes possible directions based on map edges and other already existing tiles,
       Returns a new list of possible directions"""

    possible_directions = tile.possible_directions
    
    tile_x = tile.coordinate_x
    tile_y = tile.coordinate_y


    # Check for map grid edges
    if tile_x == 0 and "left" in possible_directions: # If tile is at the left edge
        possible_directions.remove("left")
    if tile_x == (len(map_grid[0]) - 1) and "right" in possible_directions: # If tile is at the right edge
        possible_directions.remove("right")
    if tile_y == 0 and "up" in possible_directions: # IF tile is at the top edge
        possible_directions.remove("up")
    if tile_y == (len(map_grid) - 1) and "down" in possible_directions: # If tile is at the bottom edge
        possible_directions.remove("down")

    # Check for adjacent tiles
    required_directions = check_adjacent_tiles(map_grid, tile_x, tile_y)

    for required_dir in required_directions:
        if required_dir in possible_directions:
            possible_directions.remove(required_dir)

    return possible_directions

def get_distance_from_center(map_grid, tile):
    """Returns the distance of a given tile from the center tile in the map grid as a tuple of x and y values"""
    center_x, center_y = get_center(map_grid)
    tile_x = tile.coordinate_x
    tile_y = tile.coordinate_y

    return (abs(tile_x - center_x), abs(tile_y - center_y))

def get_tier(map_grid, tile):
    dx, dy = get_distance_from_center(map_grid, tile)

    # Half the map dimensions (because center is middle)
    half_width = len(map_grid[0]) // 2  # 20
    half_height = len(map_grid) // 2    # 20

    # Define thirds based on distance from center
    third_x = half_width // 3     # 20 // 3 = 6
    third_y = half_height // 3    # 20 // 3 = 6

    if dx <= third_x and dy <= third_y:
        return 1
    elif dx <= third_x * 2 and dy <= third_y * 2:
        return 2
    else:
        return 3

def generate_random_entity():
    return random.choices(ENTITIES, weights=ENTITY_LIKELIHOODS, k=1)
    
def backtrack(map_grid: list, steps: list):
    """Backtracks based on coordinates specified in the steps list of tuples
       Returns the new steps list with steps from the beginning up to the first tile that still has possible_directions"""
    
    while True:
        last_step = steps[-1]
        last_x, last_y = last_step
        last_tile = map_grid[last_y][last_x]
        if last_tile.possible_directions: # If tile has possible directions
            return steps
        steps = steps[:-1] # Remove last step (backtrack to the previous step)

def generate_map_grid(size: int):
    """Returns a 2D grid of a given size"""

    print("Generating map...")
    
    if size <= 0:
        return -1

    # Create an empty 2D grid for the map
    map_grid = [[None for _ in range(size)] for _ in range(size)]

    # Set the starting tile
    center_x, center_y = ((size - 1) // 2, (size - 1) // 2)
    map_grid[center_y][center_x] = Tile("crossroad_room", center_x, center_y)

    current_tile = map_grid[center_y][center_x]
    current_tile.add_entity(Heal())

    # List to store steps during grid generation to use when backtracking
    steps = [(center_x, center_y)]

    # Map generation

    while map_grid[center_y][center_x].possible_directions:
        # Check and fix current tile's possible directions
        current_tile.possible_directions = fix_possible_directions(map_grid, current_tile)

        # If there are no possible directions, start backtracking
        if not current_tile.possible_directions:
            steps = backtrack(map_grid, steps)
            last_step = steps[-1]
            last_x, last_y = last_step
            current_tile = map_grid[last_y][last_x]
        
        # Pick a new direction
        new_direction = random.choice(current_tile.possible_directions)

        # Remove that direction from the possible directions to generate new tiles
        current_tile.possible_directions.remove(new_direction)

        # Get new coordinates
        new_coordinates = get_new_coordinates(map_grid, current_tile, new_direction)
        if not new_coordinates:
            continue
        else:
            new_x, new_y = new_coordinates
        steps.append((new_x, new_y))
            
        # Check around the new tile for different tiles (to figure out direction requirements)
        required_directions = check_adjacent_tiles(map_grid, new_x, new_y)

        # Get invalid direction based on tile position (in case tile is at the edge of the grid)
        invalid_directions = get_invalid_directions(map_grid, new_x, new_y)
                
        # Pick new tile type based on the required directions
        while True:
            possible_new_tiles = get_possible_new_tiles(required_directions, invalid_directions)
            new_tile = random.choice(possible_new_tiles)
            if "room" in new_tile:
                if random.randrange(c.ROOM_LIKELIHOOD) == 0:
                    break
                else:
                    possible_new_tiles.remove(new_tile)
                    continue
            break
                    
        # Create new tile
        map_grid[new_y][new_x] = Tile(new_tile, new_x, new_y)
        map_grid[new_y][new_x].possible_directions.remove(get_direction_opposite(new_direction))
        current_tile = map_grid[new_y][new_x]
        
        tier = get_tier(map_grid, current_tile)
        current_tile.add_tier(tier)
        if current_tile.is_room:
            random_entity = generate_random_entity()
            if random_entity[0] == Heal:
                current_tile.add_entity(random_entity[0]())
            else:
                current_tile.add_entity(random_entity[0](tier))
                

    # Make any tiles who are still None turn into empty tile types
    for i in range(len(map_grid)):
        for j in range(len(map_grid[0])):
            if map_grid[i][j] is None:
                map_grid[i][j] = Tile("empty", i, j)

    print("Done")
    return map_grid

# ===============================================

# ============= Game Loop Functions =============

def get_player_view(map_grid: list, player_x: int, player_y: int, caller: int):
    """Takes the map_grid and player's position and returns a 2D grid of tiles with the player in the center. caller is the number of the player whose view this function returns"""

    view_radius_x = c.PLAYER_VIEW_X // 2
    view_radius_y = c.PLAYER_VIEW_Y // 2
    offset_x = -view_radius_x
    offset_y = -view_radius_y
    
    player_view = [[None for _ in range(c.PLAYER_VIEW_X)] for _ in range(c.PLAYER_VIEW_Y)]

    for i, row in enumerate(player_view):
        offset_x = -view_radius_x
        for j, tile in enumerate(row):
            tile_x = player_x + offset_x
            tile_y = player_y + offset_y

            # if the tile would be out of bounds
            if (tile_x < 0 or tile_x > (len(map_grid[0]) - 1)) or (tile_y < 0 or tile_y > (len(map_grid) - 1)):
                player_view[i][j] = Tile("empty", tile_x, tile_y)
                offset_x += 1
                continue

            # Make a copy of the tile so that it's possible to only modify the copy and send it to the player
            tile = map_grid[tile_y][tile_x].copy()
            if tile.players_present and caller in tile.players_present:
                tile.players_present = [caller]
            else:
                tile.players_present = tile.players_present[:1]
            player_view[i][j] = tile
            offset_x += 1
        offset_y += 1
    return player_view

def get_fight_result(player, entity):
    """Returns a dictionary containing the attack power, fight result and in case of success, the name of a new item"""
    # Simulate throwing a dice twice and adding up the values
    base_power = random.randint(1, 6) + random.randint(1, 6)

    extra_power = player.get_extra_power()

    new_item = generate_item(entity.tier)

    if base_power + extra_power > entity.power:
        return {
            "power": base_power + extra_power,
            "success": True,
            "item": new_item
        }
    else:
        return {
            "power": base_power + extra_power,
            "success": False,
            "item": None
        }
  
# =============================================
