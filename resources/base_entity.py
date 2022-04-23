import pyglet

from resources import *

class BaseEntity(pyglet.shapes.Rectangle):
    def __init__(self, window, columns, hp, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.window = window
        self.columns = columns

        self.health = hp
        
        self.jump_v = 4
        self.is_jumping = False
        self.can_jump = True

        self.fall_v = 4

    def damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.kill()

    def kill(self):
        # stop displaying the entity and indicate it needs to be cleaned up
        self.visible = False
    
    def bottom_collision(self):
        # check for collision UNDER the entity
        # if 1 under the player is in the range of the height of the column the entity is standing on check if there is a rect obj

        # for left, middle, right of entity
        for pos in (self.x, self.x+5, self.x+8):
            if (int(self.y/5)-1) in range(len(self.columns[int(pos/5)])+1):
                 # if under the entity is inside the terrain array
                if self.columns[int(pos/5)][-(int(self.y/5)-1)] is not None:
                    # if under the entity is not empty space
                    return True
        return False

    def top_collision(self):
    # check for collision to the TOP of the entity

        for pos in (self.x, self.x+5, self.x+8):
            if (int((self.y+24)/5)) in range(len(self.columns[int(pos/5)])+1):
                # if above the entity is inside the terrain array
                if self.columns[int(pos/5)][-(int((self.y+24)/5))] is not None:
                    # if above the entity is not empty space
                    return True
        return False

    def side_collision(self, side):
        # check for collision to the side of the entity
        
        side = (self.x-2) if side == "left" else (self.x+10)

        collisions = []
        # for bottom, middle, top of entity
        for pos in (self.y, self.y+5, self.y+10, self.y+15):
            if int(pos/5) in range(len(self.columns[int((side)/5)])+1):
                # if to the SIDE of the entity is inside the terrain array
                if self.columns[int((side)/5)][-int(pos/5)] is not None:
                    # if to the SIDE of the entity is not empty space
                    collisions.append(pos)
        if collisions:
            # if the collision list is not empty
            if collisions[0] == self.y and len(collisions) == 1 and not self.top_collision():
                # if the only collision is at 1 block height from the player then autojump
                self.y += 5
                return False
            # there was another collision so prevent movement
            return True
        # no collision
        return False
        
    def dy_to_terrain(self):
        # find the top most piece of terrain that is under the entity
        # return the vertical distance to this terrain from the entity's position

        distances = []
        # for left, middle, right of entity
        for pos in (self.x, self.x+5, self.x+8):
            for rect in self.columns[int((pos)/5)]:
                if rect is not None and rect.y <= self.y:
                    # if it is not empty and is under the entity
                    distances.append((self.y-(rect.y+5)))
        # return the smallest distance to terrain to stop entity clipping into terrain on one side
        return min(distances)

    def dy_to_ceil(self):
        # find the distance between the next piece of terrain above the entity

        distances = []
        # for left, middle, right of entity
        for pos in (self.x, self.x+5, self.x+8):
            for rect in self.columns[int((pos)/5)]:
                if rect is not None and rect.y > self.y:
                    # if it is not empty and is above the entity
                    distances.append((rect.y-(self.y+20)))
        # return the smallest distance to terrain to stop entity clipping into terrain on one side
        # return 100 (large number) if there is no terrain above the player to allow regular unobstructed jump
        return 100 if not distances else min(distances)

    def dx_to_side(self, side):
        # find the distance between the next piece of terrain to the side of the entity

        side = (self.x-0.5) if side == "left" else (self.x+10.5)
        
        distances = []
        # for bottom, top, middle of entity
        for pos in (self.y, self.y+5, self.y+10, self.y+15):
            if int(pos/5) in range(len(self.columns[int(side/5)])):
                if self.columns[int(side/5)][int(pos/5)] is not None:
                    distances.append(self.columns[int(side/5)][int(pos/5)].x-self.x)
        return min(distances) if distances else None
                                     
    
    def move_left(self, dx=1.25):
        if int(self.x/5) < 0.5:
            # do not allow going out of world
            return
        
        if not self.side_collision("left"):
            # nothing is blocking left movement
            # get distance to next terrain piece on the left
            dx_to_left = self.dx_to_side("left")

            if dx_to_left is not None and dx > abs(dx_to_left):
                # if there is terrain and movning by dx will make us overshoot terrain
                self.x += dx_to_left
            else:
                self.x -= dx

    def move_right(self, dx=1.25):
        if len(self.columns)-2 - int(self.x/5) < 0.5:
            # do not allow going out of world
            return

        if not self.side_collision("right"):
            # nothing is blocking right movement
            # get distance to next terrain piece on the right
            dx_to_right = self.dx_to_side("right")

            if dx_to_right is not None and dx > dx_to_right:
                # if there is terrain and movning by dx will make us overshoot terrain
                self.x += dx_to_right
            else:
                self.x += dx

    def jump(self):
        # called by enemy and player to initiate jump state
        if self.can_jump and not self.top_collision():
            self.is_jumping = True
            self.can_jump = False
    
    def can_see(self, entity):
        if not entity.visible:
            # if the entity is not visible then it definitely cannot be seen
            return
        
        # check from their 'head'
        # points are taken from the bottom left
        p1 = [self.x+5, self.y+10]
        p2 = [entity.x+5, entity.y+10]

        dist = return_distance(p1, p2)
        # max 'eyesight' range
        if dist < 300:
            # gradient between points
            dydx = return_dydx(p1, p2)

            # handles gradient of 0 where entities are vertical and dx == 0
            # gradient of 0 means entity positions are directly vertical of eachother.
            # gradient of None or anything else means entity positions are horizontal from eachother or at an angle.
            
            # when the positions are directly vertical we want to traverse through the Y values in the raycast
            # otherwise, we need to add an X displacement and the gradient for that displacement to traverse an angled (or horizontal) line
            traversal_type = {0: 1, None: 0}

            # the position we are starting from must be less than where we are going to
            # if it is greater than then swap around the point we are traversing from
            if p1[traversal_type.get(dydx, 0)] > p2[traversal_type.get(dydx, 0)]:
                p1, p2 = p2, p1
            
            while p1[ traversal_type.get(dydx, 0) ] < p2[ traversal_type.get(dydx, 0) ]:
                    # incrementing by 1 would add 1 lot of dydx
                    # incrementing by 0.5 allows us more precision
                    p1[ traversal_type.get(dydx, 0) ] += 0.5
                    if traversal_type.get(dydx, 0) == 0:
                        # positions either horizontal or at an angle
                        p1[1] += 0 if dydx == None else (dydx/2)
                    if int(p1[1]/5) in range(len(self.columns[int(p1[0]/5)])+1):
                        # position is inside 2D terrain array
                        if self.columns[int(p1[0]/5)][-int(p1[1]/5)] is not None:
                            # position is inside a terrain piece
                            return False
        else:
            # too far away
             return False
        # in max viewing range and nothing in the way
        # can see the other entity
        return True
        
        
    
    def update(self, dt):

        # gravity
        if not self.bottom_collision():
            # if the entity is not colliding with the floor
            if not self.is_jumping:
                # if the entity is not jumping or colliding with floor
                # move the player downwards
                
                # calculate how much this next fall will take us down
                # if this dy is greater than max distance then do max to not overshoot
                dy = (-(self.fall_v*self.fall_v)+16)
                distance_to_terrain = self.dy_to_terrain()

                if dy > distance_to_terrain:
                    self.y -= distance_to_terrain
                else:
                    self.y -= dy

                if self.fall_v > 0:
                    # whilst the fall velocity has not reached max, increase
                    self.fall_v -= 1
                
                
        else:
            # colliding with floor :
            if self.y % 5 != 0:
                # collided with the floor but offset slightly
                # y pos at rest is always a multiple of 5
                self.y -= self.dy_to_terrain()

            if not self.is_jumping:
                # when the entity is not jumping and is colliding with floor, allow them to jump again
                self.can_jump = True
            # reset fall_v so fall accelerates again next time
            self.fall_v = 4
        
        # jump physics
        if self.is_jumping:
            if not self.top_collision():
                # if entity isn't hitting ceiling
                if self.jump_v > 0:
                    # if still in jump cycle

                    # distance the jump will move the entiy
                    jump_dy = (-(self.jump_v*self.jump_v)+16)
                    # distance the entity is from ceiling
                    distance_to_ceil = self.dy_to_ceil()

                    if jump_dy > distance_to_ceil:
                        # if the player will hit their head from jumping go max distance
                        self.y += distance_to_ceil
                        # cancel the rest of the jump
                        self.is_jumping = False
                    else:
                        # add jumping distance for current jump_v
                        self.y += (-(self.jump_v*self.jump_v)+16)
                        # decrement jump_v to continue jump cycle
                        self.jump_v -= 1

                    
                else:
                    # jump cycle is over, cancel jump and reset jump_v
                    self.is_jumping = False
                    self.jump_v = 4
            else:
                # the entity is hitting the ceiling, cancel jump
                self.is_jumping = False
