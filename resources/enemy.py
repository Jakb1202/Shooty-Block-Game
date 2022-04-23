import pyglet
import random
import time

from resources import *

class Enemy(BaseEntity):
    enemy_count = 0
    def __init__(self, player, window, columns, hp, x=None, y=None, speed=None, *args, **kwargs):
        Enemy.enemy_count += 1
        print("Enemies: ", Enemy.enemy_count)

        self.player = player 
        width, height, color = 10, 20, (32,128,64)
        if x is None:
            # assign the enemy a random spawn position but at the top of the terrain
            dx = random.randint(150, 400)
            x = player.x + random.choice((dx, -dx))
            
            while int(x/5) not in range(len(columns)):
                dx = random.randint(150, 400)
                x = player.x + random.choice((dx, -dx))
        else:
            x = x

        if y is None:
            # find the next non-None terrain piece in that column
            # add 15 spaces to  Y value to avoid spawning in terrain; enemy will fall to gravity on spawn
            print(x)
            y = next((i for i in columns[int(x/5)] if i is not None)).y + 15
        else:
            y = y

        super().__init__(window, columns, hp, x, y, width, height, color, *args, **kwargs)
        
        self.shootable = True
        
        self.dt_count = 0
        self.sees_player = False
        self.last_known_pos = None
        self.max_travel_time = 0

        self.speed = speed if speed is not None else round(random.uniform(1, 1.75), 2)

    def damage(self, amount):
        super().damage(amount)
        self.sees_player = True
    
    def update(self, dt):
        super().update(dt)

        self.dt_count += 1

        # every 60 frames check for the player
        # less intensive and adds 'brain lag'
        if self.dt_count == 60:
            if self.can_see(self.player):
                self.sees_player = True
            else:
                # the enemy just saw the player a moment ago
                if self.sees_player:
                    self.last_known_pos = self.player.x
                    self.max_travel_time = time.time() + 5
                self.sees_player = False
            self.dt_count = 0

        if self.sees_player:
            # state: target player's current position
            dx = self.x - self.player.x
            
        else:
            # target players' last known position if exists
            if self.last_known_pos is not None:
                # state: moving towards last known
                dx = self.x - self.last_known_pos
                if abs(dx) < 5 or time.time() > self.max_travel_time:
                    # return back to stationary state
                    self.last_known_pos = None
            else:
                # state: stationary
                dx = 0
                
        if abs(dx) > 5 and self.player.visible:
            # enemy has to be at least 5 spaces away from the player to get closer
            if dx < 0:

                if self.side_collision("right"):
                    self.jump()

                self.move_right(self.speed)
                        
            elif dx > 0:
                if self.side_collision("left"):
                    self.jump()

                self.move_left(self.speed)
        
           
        if self.sees_player and (0 < abs(dx) < 5) and self.player.visible and return_distance((self.player.x, self.player.y), (self.x, self.y)) < 5:
            self.player.damage(0.5)
