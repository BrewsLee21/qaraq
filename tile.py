import random
from copy import deepcopy

import config as c
from entities import Enemy, Dragon, Chest, Heal

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
    #   tier - value from 1 to 3, gets higher the farther away from the center the tile is
    #   entity - the entity the tile contains (will be an instance of an entity class specified in entities.py)
    #   players_present - list of players currently present on tile represented by their player numbers

    def clear_tile(self):
        """Clears the middle line of a tile"""
        self.lines[2] = self.lines[2][:1] + "   " + self.lines[2][4:]

    def refresh_tile(self):
        """Used after modifying the tile. Recalculates the self.tile and self.lines variables to render the tile correctly when printing"""

        if self.entity:
            entity_len = len(self.entity.char)
            
            # Clear the line that may have contained an enitity
            self.clear_tile()

            if type(self.entity) == Heal:
                self.lines[1] = self.lines[1][:1] + f"{self.entity.char} {self.entity.char}" + self.lines[1][4:]
                self.lines[3] = self.lines[3][:1] + f"{self.entity.char} {self.entity.char}" + self.lines[3][4:]
                self.tile = ''.join(self.lines)
                return
                
            if entity_len < 3:
                self.lines[2] = self.lines[2][:2] + self.entity.char + self.lines[2][2 + entity_len:]
            elif entity_len == 3:
                self.lines[2] = self.lines[2][:1] + self.entity.char + self.lines[2][4:]
            self.tile = ''.join(self.lines)
                
    def remove_entity(self):
        self.entity = None
        self.clear_tile()
        self.refresh_tile()
    
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

        self.tier = None

        self.entity = None

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

    def add_tier(self, tier):
        self.tier = tier

    def add_entity(self, entity):
        """Adds a given item into the tile and calls the refresh_tile function at the end""" 
        
        self.entity = entity
        

        self.refresh_tile()

    def copy(self):
        return deepcopy(self)
