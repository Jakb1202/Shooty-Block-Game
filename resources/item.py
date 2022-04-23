from abc import ABC, abstractmethod
import pyglet

from resources import *


class Item(pyglet.sprite.Sprite, ABC):
    def __init__(self, player, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.player = player
        
    def update(self, dt):

        # parent the item sprite to the player's position face the mouse cursor
        angle = to_degrees(self.player.facing_angle)
        
        if abs(angle) > 90:
            # left facing:
            self.x = self.player.x
            self.scale_x = 1
            self.rotation = -angle+180
        else:
            # right facing
            self.x = self.player.x+10
            self.scale_x = -1
            self.rotation = -angle

        self.y = self.player.y+10

    # implementations will override this abstract method with their own functionality
    @abstractmethod
    def use(self, mouse_x, mouse_y):
        pass
