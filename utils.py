import random

from tile import Tile, TILE_DIRECTIONS, ENTITIES
import config as c

def print_to_log_file(s: str):
    with open("log.txt", 'a') as f:
        print(s, file=f)

# ============= Map rendering and generation =============

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

def generate_random_entity():
    entities = list(ENTITIES)
    entities.remove("start")
    entities.remove("none")
    chosen_entity =  random.choice(entities)
    return chosen_entity
    
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
    if size <= 0:
        return -1

    # Create an empty 2D grid for the map
    map_grid = [[None for _ in range(size)] for _ in range(size)]

    # Set the starting tile
    center_x, center_y = ((size - 1) // 2, (size - 1) // 2)
    map_grid[center_y][center_x] = Tile("crossroad_room", center_x, center_y)

    current_tile = map_grid[center_y][center_x]
    current_tile.add_entity("start")

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

        if current_tile.is_room:
            current_tile.add_entity(generate_random_entity())
                

    # Make any tiles who are still None turn into empty tile types
    for i in range(len(map_grid)):
        for j in range(len(map_grid[0])):
            if map_grid[i][j] is None:
                map_grid[i][j] = Tile("empty", i, j)

    return map_grid

# ===============================================

# ============= Game loop functions =============

def move_in_direction(map_grid: list, current_tile: Tile, direction: str):
    """Checks if movement in given direction is possible, returns the new tile if it is and -1 if it isn't"""

    if direction not in current_tile.directions: # given direction is not possible
        return -1

    offsets = {
        "left":  (0, -1),
        "up":    (-1, 0),
        "right": (0, 1),
        "down":  (1, 0)
    }
    
    dy, dx = offsets[direction]
    new_y = current_tile.coordinate_y + dy
    new_x = current_tile.coordinate_x + dx

    return map_grid[new_y][new_x]
    

def get_player_view(map_grid: list, player_x, player_y):
    """Takes the map_grid and player's position and returns a 2D grid of tiles with the player in the center"""

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
            
            tile = map_grid[tile_y][tile_x]
            player_view[i][j] = tile
            offset_x += 1
        offset_y += 1
    
    return player_view

    

# ===========================================

# ============ Utility functions ============

def draw_grid(grid):
    """Prints a 3x3 tile grid with the player in the center, takes player position as input"""
    for grid_line in grid:
        for line_index in range(5):
            line = ""
            for tile in grid_line:
                line += tile.lines[line_index]
            print(line)

def get_center(map_grid):
    """Takes the generated map grid and returns the coordinates of the center tile as a tuple of x and y values"""
    return ((len(map_grid[0]) - 1) // 2, (len(map_grid) - 1) // 2)
    
# =============================================

# ============ Debugging functions ============

def print_to_stderr(s: str):
    with open(c.DEBUG_FILE, 'a') as f:
        print(s, file=f)
