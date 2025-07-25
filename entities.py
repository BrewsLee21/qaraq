import random
import config as c

TIER = {
    1: (3, 7),
    2: (7, 13),
    3: (13, 16)
}

class Enemy:
    likelihood = c.ENEMY_LIKELIHOOD
    
    def __init__(self, tier):
        self.entity_type = "enemy"
        self.tier = tier
        self.power = random.randrange(TIER[tier][0], TIER[tier][1])
        self.char = 'e' + str(self.power)

class Chest:
    likelihood = c.CHEST_LIKELIHOOD
    
    def __init__(self, tier):
        self.entity_type = "chest"
        self.tier = tier
        self.char = 'C'

class Heal:
    likelihood = c.HEAL_LIKELIHOOD
    
    def __init__(self):
        self.entity_type = "heal"
        self.char = '♥'

ENTITIES = [
    Enemy,
    Chest,
    Heal
]

ENTITY_LIKELIHOODS = [entity.likelihood for entity in ENTITIES]
