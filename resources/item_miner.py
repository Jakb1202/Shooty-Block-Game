from resources import *


class ItemMiner(Item):
    def use(self, mouse_x, mouse_y):
        # make mouse position line up with 2D array terrain indexing
        index_x = int(mouse_x/5)
        index_y = int(mouse_y/5)
        if index_x in range(len(self.player.columns)+1) and index_y in range(len(self.player.columns[index_x])+1):
            if index_y not in (0, 1) and (return_distance((self.x, self.y), (mouse_x, mouse_y))) < 50:
                # if terrain is not the bottom most layer and is within melee range of the player
                self.player.columns[index_x][-index_y] = None
