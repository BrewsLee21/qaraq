import random  

class WeaponItem:

    WEAPON_NAMES = {
        1: "dagger",
        2: "sword",
        3: "axe"
    }
    
    def __init__(self, tier):
        self.category = "weapons"
        self.tier = tier
        self.name = WeaponItem.WEAPON_NAMES[tier]
        self.power = tier

# =================================

class ConsumableItem:
    def __init__(self, tier):
        self.category = "consumables"
        self.tier = tier

class HealingPotion(ConsumableItem):
    def __init__(self, tier):
        super().__init__(tier)
        self.name = "heal_potion_1"
        self.consumable_type = "heal"
        self.heal = 1
class StrongHealingPotion(ConsumableItem):
    def __init__(self, tier):
        super().__init__(tier)
        self.name = "heal_potion_2"
        self.consumable_type = "heal"
        self.heal = 2
class SpeedPotion(ConsumableItem):
    def __init__(self, tier):
        super().__init__(tier)
        self.name = "speed_potion"
        self.consumable_type = "speed"
        self.speed = 1
class PowerScroll(ConsumableItem):
    def __init__(self, tier):
        super().__init__(tier)
        self.name = "power_scroll"
        self.consumable_type = "power"
        self.power = 1
        
# =====================================

class GearItem:
    def __init__(self, tier):
        self.category = "gear"
        self.tier = tier
        
class Crocs(GearItem):
    def __init__(self, tier):
        super().__init__(tier)
        self.name = "crocs"
        self.gear_type = "moves"
        self.moves = 1
class Sneakers(GearItem):
    def __init__(self, tier):
        super().__init__(tier)
        self.name = "sneakers"
        self.gear_type = "moves"
        self.moves = 2
class Key(GearItem):
    def __init__(self, tier):
        super().__init__(tier)
        self.name = "key"
        self.gear_type = "key"

ITEM_CLASSES = {
    1: [
        WeaponItem,
        HealingPotion,
        SpeedPotion,
        PowerScroll,
        Crocs
    ],
    2: [
        WeaponItem,
        HealingPotion,
        StrongHealingPotion,
        SpeedPotion,
        PowerScroll,
        Sneakers,
        Key
    ],
    3: [
        WeaponItem,
        StrongHealingPotion,
        Sneakers,
        Key
    ]
}

def generate_item(tier):
    """Returns an instance of an item class generated based on tile tier"""
    new_item = random.choice(ITEM_CLASSES[tier])
    return new_item(tier)
