import enum

from resources import *

class ProjectileType(enum.Enum):
    arrow = {"v": 80, "sprite": sprite_arrow16, "damage": 35, "ttl": 30}
    bullet = {"v": 140, "sprite": sprite_bullet16, "damage": 60, "ttl": 30}
    bomb = {"v": 40, "sprite": sprite_bomb16, "damage": 100, "ttl": 10}
