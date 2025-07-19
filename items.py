import random

class WeaponItem:

    WEAPON_NAMES = {
        1: "dagger",
        2: "sword",
        3: "axe"
    }
    
    def __init__(self, tier):
        self.tier = tier
        self.name = WEAPON_NAMES[tier]
        self.power = tier

# Make some more later
class ConsumableItem:
    tier1_options = ["heal_potion"]

    CONSUMABLE_NAMES = {
        1: random.choice([])
    }
