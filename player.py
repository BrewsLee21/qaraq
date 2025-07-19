class Player:
    def __init__(self, number: str, player_sock, player_addr, center_coordinates):
        self.number = number

        self.player_sock = player_sock
        self.player_addr = player_addr
    
        self.player_x, self.player_y = center_coordinates

        # Used to move player back to last tile in case they lose a fight
        self.last_player_x = None
        self.last_player_y = None
        
        self.hp = 5
        self.base_moves = 4

        self.weapons = [None, None] # For weapons, increases power by fixed amount
        self.consumables = [None, None, None] # One use items, e.g. potions, scrolls, etc.
        self.gear = [None, None] # Keys (to open chests), shoes (to increase moves amount)

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

        self.last_player_x = self.player_x
        self.last_player_y = self.player_y

        self.player_x = new_x
        self.player_y = new_y

        # Add player to new tile
        map_grid[self.player_y][self.player_x].players_present.append(self.number)
        
        return 0

    def get_inventory(self):
        """Returns a dictionary containing the inventory of the player"""
        inventory = {
            "weapons": self.weapons,
            "consumables": self.consumables,
            "gear": self.gear
        }
        return inventory
