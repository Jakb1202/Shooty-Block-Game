import pyglet
import math

from resources import *

class Projectile(pyglet.sprite.Sprite):
    count = 0

    def __init__(self, columns, proj_name, angle, dx, entity_list, *args, **kwargs):
        Projectile.count += 1

        self.proj_name = proj_name
        proj_type = ProjectileType[proj_name]
        v = proj_type.value["v"]
        self.damage = proj_type.value["damage"]
        # time to live; how long until the projectile disappears 
        self.ttl = proj_type.value["ttl"]
        
        kwargs['img'] = proj_type.value["sprite"]
        
        super().__init__(*args, **kwargs)
        
        self.columns = columns
        self.entity_list = entity_list

        self.horizontal_v = (math.cos(angle))*v
        self.vertical_v = (math.sin(angle))*v

        # can the projectile give damage? Allows deactivating projectiles after collision
        self.damaging = True
        # has the projectile exploded? Prevents further movement after collision and explosion
        self.exploded = False
        # time; how long the projectile has been alive for
        self.time = 0
        self.dx = dx

        self.start_x = self.x
        self.start_y = self.y

    def explode(self):
        self.damaging = False
        self.exploded = True

        # set the sprite image to the explosion effect
        self.image = sprite_explosion32
        # have the explosion effect exist for the same amount of time each explosion
        # not resetting the projectile's lifetime results in varying explosion effect life
        self.time = 0
        self.ttl = 1
        
        for e in list(self.entity_list):
            if return_distance((self.x, self.y), (e.x, e.y)) <= 35:
                e.damage(self.damage)
        
        for row in range(1, 6):
            # -5n + 15
            y_offset = ((-5)*row)+15
            for column in range(1, 6):
                if row in (1,5) and column in (1, 5):
                    # top and bottom rows are missing first and end piece
                    continue
                # 5n - 15
                x_offset = (5*column)-15

                x, y = int((x_offset+self.x)/5), int((y_offset+self.y)/5)
                if x in range(len(self.columns)) and y in range(len(self.columns[x])+1):
                    if y not in (0, 1):
                        # prevent destroying bottom most terrain
                        self.columns[x][-y] = None
                    

    def terrain_collision(self):
        if int(self.x/5) in range(len(self.columns)) and int(self.y/5) in range(len(self.columns[int(self.x/5)])+1):
            if self.columns[int(self.x/5)][-(int(self.y/5))] is not None:
                self.damaging = False
                return True
        return False

    def entity_collision(self):
        # iterate over a copy of the list so we can remove from it
        for e in list(self.entity_list):
            if e.shootable:
                if (e.x <= self.x < e.x+10) and (e.y <= self.y < e.y+20):
                    # if the projectile is inside the bounds of the entity rectangle
                    e.damage(self.damage)
                    if self.proj_name == "bomb":
                        self.explode()
                    else:
                        self.visible = False
                        self.damaging = False
                    return

    def update(self, dt):
        # increment time with each frame
        self.time += 0.1

        if self.damaging:
            # the projectile is able to do damage; check for collision with entities to kill
            self.entity_collision()
        
        if not (self.terrain_collision() or self.time >= self.ttl or self.exploded):
            # if not colliding with terrain and not passed time to live
            
            # s = ut + 1/2at^2
            h_displacement = (self.horizontal_v * self.time)
            v_displacement = (self.vertical_v * self.time) - (10*(self.time*self.time))
           
            self.x = self.start_x + h_displacement
            self.y = self.start_y + v_displacement
            
            self.rotation = -to_degrees(math.atan2(v_displacement, h_displacement))+180+(self.time*5*(-1 if h_displacement < 0 else 1))
           
        else:
            if self.proj_name == "bomb" and not self.exploded:
                # only allow the bomb to explode once; prevents explosion effect killing enemies
                self.explode()

        if self.time >= self.ttl:
            self.visible = False
            
            

    
        
