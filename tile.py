import random
import config as c

ENTITIES = {
    "start": '♥', # The starting tile
    "chest": 'C',
    "enemy": 'e'
}

# Possible exit/entry directions of every tile
TILE_DIRECTIONS = {
    "crossroad_room": ("left", "up", "right", "down"),
    "crossroad": ("up", "right", "down", "left"),
    "empty": (),
    "horizontal_corridor_room": ("left", "right"),
    "horizontal_corridor": ("left", "right"),
    "L_junction_bot_left_room": ("left", "down"),
    "L_junction_bot_left": ("left", "down"),
    "L_junction_bot_right_room": ("right", "down"),
    "L_junction_bot_right": ("right", "down"),
    "L_junction_top_left_room": ("left", "up"),
    "L_junction_top_left": ("left", "up"),
    "L_junction_top_right_room": ("up", "right"),
    "L_junction_top_right": ("up", "right"),
    "T_junction_bot_left_top_room": ("down", "left", "up"),
    "T_junction_bot_left_top": ("down", "left", "up"),
    "T_junction_left_top_right_room": ("left", "up", "right"),
    "T_junction_left_top_right": ("left", "up", "right"),
    "T_junction_top_right_bot_room": ("up", "right", "down"),
    "T_junction_top_right_bot": ("up", "right", "down"),
    "T_junction_right_bot_left_room": ("right", "down", "left"),
    "T_junction_right_bot_left": ("right", "down", "left"),
    "vertical_corridor_room": ("up", "down"),
    "vertical_corridor": ("up", "down")
}

class Tile:
    # class variables
    #   tile_type
    #   coordinate_x
    #   coordinate_y
    #   directions - set containing all directions that the tile can be entered or exited from
    #   possible_directions - used during map generation, contains possible directions to generate new tiles
    #   tile  - string of the entire tile
    #   lines - list of lines of the tile
    #   is_room - if tile is a room (can contain entities)
    #   entity - the entity the tile contains
    #   entity_char - the printed character that represents the entity 
    #   players_present - list of players currently present on tile

    def clear_tile(self):
        """Clears the middle line of a tile"""
        self.lines[2] = self.lines[2][:1] + "   " + self.lines[2][4:]

    def refresh_tile(self):
        """Used after modifying the tile. Recalculates the self.tile and self.lines variables to render the tile correctly when printing"""

        if self.entity:
            entity_len = len(self.entity_char)
            
            # Clear the line that may have contained an enitity
            self.clear_tile()

            if self.entity == "start":
                self.lines[1] = self.lines[1][:1] + "♥ ♥" + self.lines[1][4:]
                self.lines[3] = self.lines[3][:1] + "♥ ♥" + self.lines[3][4:]
                self.tile = ''.join(self.lines)
                return
                
            if entity_len < 3:
                self.lines[2] = self.lines[2][:2] + self.entity_char + self.lines[2][2 + entity_len:]
            elif entity_len == 3:
                self.lines[2] = self.lines[2][:1] + self.entity_char + self.lines[2][4:]
            self.tile = ''.join(self.lines)
                
                
    
    def __init__(self, tile_type, tile_x, tile_y):
        
        self.coordinate_x = tile_x
        self.coordinate_y = tile_y
        
        with open(f"tiles/{tile_type}.txt", 'r') as f:
            self.tile_type = tile_type
            self.tile = f.read()
            self.lines = self.tile.splitlines()

        # Set directions based on tile_type
        self.directions = TILE_DIRECTIONS[tile_type]
        self.possible_directions  = list(TILE_DIRECTIONS[tile_type])

        # Is tile a room
        if "room" in tile_type:
            self.is_room = True
        else:
            self.is_room = False

        self.entity = None
        self.entity_char = ''

        self.players_present = []
        
        self.refresh_tile()

            
    def __str__(self):
        return f"""
{self.tile}\n
Directions: {self.directions}
Room: {self.is_room}
Entity: {self.entity}
\n
x: {self.coordinate_x}
y: {self.coordinate_y}"""  

    def add_entity(self, entity: str, entity_value = None):
        """Adds a given item into the tile and calls the refresh_tile function at the end"""

        if self.is_room == False and entity != "player":
            raise ValueError("Cannot assign non-player entity to a non-room tile")
        
        # Set item (if there is any)
        if entity:
            self.entity = entity
            self.entity_char = ENTITIES[entity]
            if entity == "enemy":
                self.entity_char += str(random.randrange(4, 15))

        self.refresh_tile()
 

