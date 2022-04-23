import enum

from resources import *


class ShooterType(enum.Enum):
    bow = {"projectile": "arrow", "sprite": sprite_bow16, "rate": 0.75}
    pistol = {"projectile": "bullet", "sprite": sprite_pistol16, "rate": 0.4}
    bomber = {"projectile": "bomb", "sprite": sprite_bomb16, "rate": 1}
