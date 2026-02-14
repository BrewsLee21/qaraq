from items import WeaponItem
from utils import get_direction_opposite

class Player:
    def __init__(self, number: str, player_sock, player_addr, center_coordinates):
        self.number = number

        self.player_sock = player_sock
        self.player_addr = player_addr
    
        self.player_x, self.player_y = center_coordinates

        # Used to move player back to last tile in case they lose a fight
        self.last_direction = None
        
        self.health = 5
        self.base_moves = 4

        self.extra_power = 0
        self.extra_moves = 0

        self.is_dead = False
        self.disconnected = False

        self.inventory = {
            "weapons": [None, None], # For weapons, increases power by fixed amount
            "consumables": [None, None, None], # One use items, e.g. potions, scrolls, etc.
            "gear": [None, None] # Keys (to open chests), shoes (to increase moves amount)
        }

    def remove_extras(self):
        self.extra_power = 0
        self.extra_moves = 0
        
    def move_in_direction(self, map_grid: list, direction: str):
        """Checks if movement in given direction is possible, returns 0 on success and -1 on failure
           Also updates player coordinates and tile"""

        current_tile = map_grid[self.player_y][self.player_x]
    
        offsets = {
            "left":  (0, -1),
            "up":    (-1, 0),
            "right": (0, 1),
            "down":  (1, 0)
        }

        # given direction is not possible or invalid
        if direction not in current_tile.directions or direction not in offsets: 
            return -1
        
        dy, dx = offsets[direction]
        new_y = current_tile.coordinate_y + dy
        new_x = current_tile.coordinate_x + dx

        # Remove player from current tile
        map_grid[self.player_y][self.player_x].players_present.remove(self.number)

        self.last_direction = direction

        self.player_x = new_x
        self.player_y = new_y

        # Add player to new tile
        map_grid[self.player_y][self.player_x].players_present.append(self.number)
        
        return 0

    def move_back(self, map_grid: list):
        """Moves player back to previous tile"""
        direction = get_direction_opposite(self.last_direction)
        self.move_in_direction(map_grid, direction)
        self.last_direction = None

    def get_inventory(self):
        """Returns a dictionary containing the inventory of the player"""
        return self.inventory

    def get_item(self, index):
        """Returns the item from the player's inventory based on it's index"""
        items = [item for sublist in self.inventory.values() for item in sublist]

        if index > len(items):
            return -1
        
        return items[index]

    def modify_inventory(self, new_item):
        """Adds an item specified by new_item to the player's inventory. Reutrns 1 on success and -1 when inventory is full"""
        for index, item in enumerate(self.inventory[new_item.category]):
            if not item:
                self.inventory[new_item.category][index] = new_item
                return 1
        return -1

    def remove_item(self, item_index):
        """Removes the item specified by it's index item_index from the player's inventory"""
        for key in self.inventory:
            if item_index >= len(self.inventory[key]):
                item_index -= len(self.inventory[key])
                continue
            k = key
            break
        self.inventory[k][item_index] = None
                        

    def get_extra_power(self):
        """Returns an integer representing the extra power from items"""
        extra_power = 0
        for weapon in self.inventory["weapons"]:
            if weapon:
                extra_power += weapon.power
        return extra_power + self.extra_power

    def get_extra_moves(self):
        extra_moves = self.extra_moves
        for item in self.inventory["gear"]:
            if item and item.gear_type == "moves":
                extra_moves += item.moves
        return extra_moves
                
    def get_moves(self):
        """Returns the number of moves the player has at the beginning of each turn"""
        return self.base_moves + self.get_extra_moves()

    def use_item(self, item_index):
        """Uses a consumable item"""
        item = self.get_item(item_index)
        if item.category != "consumables":
            return -1

        if item.consumable_type == "heal":
            self.health += item.heal
            if self.health > 5:
                self.health = 5
        elif item.consumable_type == "speed":
            self.extra_moves += item.speed
        elif item.consumable_type == "power":
            self.extra_power += item.power
        else:
            return -1

        self.remove_item(item_index)
        return 1

    def get_stats(self):
        stats = {}

        stats.update({"extra_power": self.get_extra_power()})
        stats.update({"base_moves": self.base_moves})
        stats.update({"extra_moves": self.get_extra_moves()})
        stats.update({"health": self.health})

        return stats
