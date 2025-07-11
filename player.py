class Player:
    def __init__(self, number: str, player_sock, player_addr, center_coordinates):
        self.name = 'p' + str(number)

        self.player_sock = player_sock
        self.player_addr = player_addr
    
        self.player_x, self.player_y = center_coordinates
        
        self.hp = 5
        self.base_moves = 4

    def move_in_direction(self, map_grid: list, direction: str):
        """Checks if movement in given direction is possible, returns the new tile if it is and -1 if it isn't
           Also updates player coordinates"""

        current_tile = map_grid[self.player_y][self.player_x]
        
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

        self.player_x = new_x
        self.player_y = new_y
        
        return map_grid[new_y][new_x]
