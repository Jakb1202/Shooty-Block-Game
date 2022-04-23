import pyglet
from pyglet.window import key
import math
import random
import time

from resources import *

class Player(BaseEntity):
    def __init__(self, window, camera, hp, columns, entity_list, x=600, y=400, score=0, kills=0, item_count=3, *args, **kwargs):
        super().__init__(window, columns, hp, x, y, 10, 20, (255,0,0), *args, **kwargs)

        self.score = score 
        self.kills = kills 
        self.shootable = False
        self.last_died_time = 0
        self.entity_list = entity_list
        
        self.key_handler = key.KeyStateHandler()
    
        self.main_camera = camera
        
        self.last_pos = [self.x, self.y]
        self.facing_angle = 0
        self.last_damaged = 0
        self.last_healed = 0

        self.items = list()
        # ItemBlank, ItemMiner, ItemSword are all default items and don't need to be unlocked
        self.items.append(ItemBlank(img=sprite_blank1, player=self))
        self.items.append(ItemMiner(img=sprite_miner16, player=self, batch=item_batch))
        self.items.append(ItemSword(img=sprite_sword16, player=self, batch=item_batch))
        self.item_bow = ItemShooter("bow", player=self, batch=item_batch)
        self.item_pistol = ItemShooter("pistol", player=self, batch=item_batch)
        self.item_bomber = ItemShooter("bomber", player=self, batch=item_batch)

        # if the game was loaded and the player previously unlocked these items
        if item_count > 3:
            self.items.append(self.item_bow)
        if item_count > 4:
            self.items.append(self.item_pistol)
        if item_count > 5:
            self.items.append(self.item_bomber)

        self.selected_item = 0

        self.pos_label = pyglet.text.Label(
            "", x=60, y=window.height-20, anchor_x='center', anchor_y='center', batch=overlay_batch
            )
        self.health_label = pyglet.text.Label(
            "", x=window.width-220, y=120, anchor_x='left', anchor_y='center', bold=True, color=(64,255,16,255), font_name="Retro Gaming", font_size=20,
            batch=overlay_batch
            )
        self.score_label = pyglet.text.Label(
            "", x=window.width-220, y=90, anchor_x='left', anchor_y='center', bold=True, color=(64,255,16,255), font_name="Retro Gaming", font_size=20,
            batch=overlay_batch
            )
        self.kills_label = pyglet.text.Label(
            "", x=window.width-220, y=60, anchor_x='left', anchor_y='center', bold=True, color=(64,255,16,255), font_name="Retro Gaming", font_size=20,
            batch=overlay_batch
            )

        self.timed_text = list()
        self.timed_text.append(TimedText(
            30, "Use A & D to move Left & Right", x=self.window.width//2, y=675, anchor_x='center', anchor_y='center', bold=True, color=(255,255,255,255), font_size=16
        ))
        self.timed_text.append(TimedText(
            30, "Use Left Mouse to use items", x=self.window.width//2, y=650, anchor_x='center', anchor_y='center', bold=True, color=(255,255,255,255), font_size=16
        ))
        self.timed_text.append(TimedText(
            30, "Use Right Mouse to place blocks", x=self.window.width//2, y=625, anchor_x='center', anchor_y='center', bold=True, color=(255,255,255,255), font_size=16
        ))
        self.timed_text.append(TimedText(
            30, "Use number keys to change items", x=self.window.width//2, y=600, anchor_x='center', anchor_y='center', bold=True, color=(255,255,255,255), font_size=16
        ))
        
    def increase_score(self, score=10):
        self.score += score
        self.kills += 1
        self.unlock_items()

    def decrease_score(self, score=10):
        # constrain score so it doesn't go negative
        self.score = max(0, self.score-score)

    def unlock_items(self):
        if self.score >= 50 and self.item_bow not in self.items:
            self.items.append(self.item_bow)
            self.timed_text.append(TimedText(
                10, "Bow item unlocked!", x=self.window.width//2, y=550, anchor_x='center', anchor_y='center', bold=True, color=(0,255,0,255), font_size=20
            ))
            self.timed_text.append(TimedText(
                10, "Use number 4 to select this item", x=self.window.width//2, y=510, anchor_x='center', anchor_y='center', bold=True, color=(255,255,255,255), font_size=12
            ))
        if self.score >= 150 and self.item_pistol not in self.items:
            self.items.append(self.item_pistol)
            self.timed_text.append(TimedText(
                10, "Pistol item unlocked!", x=self.window.width//2, y=550, anchor_x='center', anchor_y='center', bold=True, color=(0,255,0,255), font_size=20
            ))
            self.timed_text.append(TimedText(
                10, "Use number 5 to select this item", x=self.window.width//2, y=510, anchor_x='center', anchor_y='center', bold=True, color=(255,255,255,255), font_size=12
            ))
        if self.score >= 300 and self.item_bomber not in self.items:
            self.items.append(self.item_bomber)
            self.timed_text.append(TimedText(
                10, "Bomber item unlocked!", x=self.window.width//2, y=550, anchor_x='center', anchor_y='center', bold=True, color=(0,255,0,255), font_size=20
            ))
            self.timed_text.append(TimedText(
                10, "Use number 6 to select this item", x=self.window.width//2, y=510, anchor_x='center', anchor_y='center', bold=True, color=(255,255,255,255), font_size=12
            ))
            
    
    # override
    def damage(self, amount):
        if self.visible:
            # if the player is not visible they are current respawning
            super().damage(amount)
            self.last_damaged = time.time()

    # override
    def kill(self):
        self.last_died_time = time.time()
        self.timed_text.append(TimedText(
            5, "You Died!", x=self.window.width//2, y=(self.window.height//2)+25, anchor_x='center', anchor_y='center', bold=True, color=(255,0,0,255), font_size=20
        ))
        
        print("i AM DEADED")
        self.visible = False
        self.decrease_score(50)

        # reset enemy seeing state on the player
        for e in self.entity_list:
            if e.shootable:
                e.sees_player = False
                e.last_known_pos = None

    def respawn(self):
        x = random.randint(100, (len(self.columns)-50)*5)
        while abs(x-self.x) < 200:
            # while the respawn location is too close to death
            x = random.randint(100, (len(self.columns)-50)*5)

        y = next((i for i in self.columns[int(x/5)] if i is not None)).y + 50
        self.x, self.y = x, y
        self.visible = True
        self.health = 100

    def heal(self):
        if self.health < 100:
            # if the player is not at full health
            now = time.time()
            if (( now-self.last_damaged ) > 5) and (( now - self.last_healed ) > 2.5):
                # if the player has gone 5 seconds without being damaged
                # if the player has gone 2.5 seconds without receiving healing
                self.health = min(self.health+5, 100)
                self.last_healed = now
    
    def on_key_press(self, symbol, modifiers):
        if not self.visible:
            # the player cannot take input when dead
            return

        # jump
        if symbol == key.SPACE:
            self.jump()
        # increment selected item index
        if symbol == key.E:
            self.selected_item = min(self.selected_item+1, len(self.items)-1)
        # decrement selected item index
        if symbol == key.Q:
            self.selected_item = max(self.selected_item-1, 0)
        if symbol in range(49, 55):
            # num keys 1-6
            index = symbol - 49
            # select the most recently acquired item if selecting an empty slot
            if index > len(self.items)-1:
                self.selected_item = len(self.items)-1
            else:
                self.selected_item = index

    def place_block(self, mouse_x, mouse_y):
        if (self.x <= mouse_x <= self.x+10) and (self.y <= mouse_y <= self.y+20):
            # prevent placing blocks within player position
            return
        
        x, y = int(mouse_x/5), int(mouse_y/5)
        if return_distance((self.x, self.y), (mouse_x, mouse_y)) < 50:
            # within range of the player
            if x in range(len(self.columns)-1):
                if y in range(len(self.columns[x])-1):
                    if self.columns[x][-y] is None:
                        square = pyglet.sprite.Sprite(sprite_wood16, x=x*5, y=y*5, batch=main_batch)
                        square.scale = 0.3125 # 15/48 = 0.3125
                        square.block_type = "wood"
                        self.columns[x][-y] = square
    
    def on_mouse_press(self, x, y, button, modifier):
        if not self.visible:
            # the player cannot take input when dead
            return

        offset_x, offset_y  = self.main_camera.position
        x = int((x) / self.main_camera.zoom) + int(offset_x)
        y = int((y) / self.main_camera.zoom) + int(offset_y)

        if button == 1:
           # Left mouse
            self.items[self.selected_item].use(x, y)
        if button == 4:
            # Right mouse
            self.place_block(x, y)

    def on_mouse_drag(self, x, y, dx, dy, button, modifier):
        if button == 1 and self.selected_item != 1:
            # only allow drag inputs on the miner item
            return
        self.on_mouse_press(x, y, button, modifier)

    def on_mouse_motion(self, x, y, dx, dy):
        offset_x, offset_y  = self.main_camera.position
        x = int((x) / self.main_camera.zoom) + int(offset_x)
        y = int((y) / self.main_camera.zoom) + int(offset_y)
        
        self.facing_angle = math.atan2(y-self.y, x-self.x)

    def overlays(self):
        # debug for the player's position
        self.pos_label.text = f"x,y: {self.x}, {self.y}"

        # health bar; take math.ceil() of the health to give an integer value
        self.health_label.text = f"Health : {math.ceil(self.health)}"

        # score count
        self.score_label.text = f"Score  : {self.score}"

        # kill count
        self.kills_label.text =  f"Kills     : {self.kills}"

        # TimedText manager
        for label in list(self.timed_text):
            if label.has_expired():
                self.timed_text.remove(label)
                
        
    def update(self, dt):
        # wait 5 seconds after death before respawning
        if not self.visible and (time.time()-self.last_died_time) > 5:
            self.respawn()

        # if an item is not selected then don't make it visible
        for index, item in enumerate(self.items):
            if index == self.selected_item and self.visible:
                item.visible = True
            else:
                item.visible = False
        # make sure all items are kept updated;
        # projectiles are created inside the item, we don't want floating projectiles
        for item in self.items:
            item.update(dt)

        self.last_pos = [self.x, self.y]
        
        # move left
        if self.key_handler[key.A] and self.visible:
            if self.key_handler[key.LSHIFT]:
                # sprint
                self.move_left(2.5)
            else:
                self.move_left()

        # move right 
        if self.key_handler[key.D] and self.visible:
            if self.key_handler[key.LSHIFT]:
                # sprint
                self.move_right(2.5)
            else:
                self.move_right()

        super().update(dt)

        # change main camera position in relation to the player
        # keeps the player's position central on the screen at all times
        # get the offset in how much the player has moved in both X and Y, multiple Y difference to get less harsh movement
        self.main_camera.move((self.x-self.last_pos[0]), ((self.y-self.last_pos[1])*0.25))
        # update cameras position in relation to player's position on screen and the current zoom level, don't offset Y so under terrain shows
        self.main_camera.position = ((self.x-((self.window.width//2)//self.main_camera.zoom)), max(1, self.main_camera.offset_y))

        # passive healing
        self.heal()
        self.overlays()

        Settings.kills = self.kills
        Settings.score = self.score
