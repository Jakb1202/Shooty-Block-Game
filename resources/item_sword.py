from resources import *

class ItemSword(Item):
    def use(self, mouse_x, mouse_y):
        for e in list(self.player.entity_list):
            if e.shootable and (return_distance((self.x, self.y), (e.x, e.y)) < 50):
                # if the entity can be killed and within a short melee range of the player
                if (e.x <= mouse_x < e.x+10) and (e.y <= mouse_y < e.y+20):
                    # if the mouse click is inside the bounds of the entity rectangle
                    e.damage(75)
                    # return so only one enemy can be damaged at once
                    return
