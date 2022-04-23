from datetime import datetime
import json
import math
import os
import random
import sys
import time

print("Appending pyglet path...")
sys.path.append("N:\Desktop\\")

import pyglet
from pyglet.window import key
from resources import * 


# change game's file path based on if it was run from a compiled .exe version
#  - app path ends up in a temp folder whilst the program is being executed if so and breaks saving/loading/resources
if getattr(sys, 'frozen', False):
    APP_PATH = os.path.dirname(sys.executable)
else:
    APP_PATH = os.path.dirname(__file__)


# initialise window and FPS counter
window = pyglet.window.Window(width=1080, height=720, caption="Shooty block game!")
window.set_location(420, 200)
fps_display = pyglet.window.FPSDisplay(window)
fps_display.label.y, fps_display.label.batch = window.height - 60, overlay_batch


class Game:
    def __init__(self, window):
        # game setup
        self.window = window
        self.main_camera = Camera(min_zoom=0.5, max_zoom=3)

        self.entity_list = list()
        self.game_started = False

        # store when the last enemy was added and a random duration until a new one can be added
        self.last_added_enemy = 0
        # make enemies spawn faster if the difficulty has been set higher by the player
        self.new_enemy_wait = random.randint(3, (20 if Settings.difficulty == 1 else 10 if Settings.difficulty == 2 else 5))

        self.last_quicksaved = time.time()
        
    def load_overlays(self):
        self.options_label = pyglet.text.Label(
            "Press TAB to access options", x=10, y=60, anchor_x='left', anchor_y='center', bold=True, color=(255,255,255,255), font_name="Retro Gaming", font_size=12, batch=overlay_batch
            )
        self.seed_label = pyglet.text.Label(
            f"Seed: {Settings.seed_number}", x=10, y=15, anchor_x='left', anchor_y='center', bold=True, color=(255,255,255,255), font_name="Retro Gaming", font_size=10, batch=overlay_batch
            )
        self.seed_label = pyglet.text.Label(
            f"Save created: {datetime.fromtimestamp(int(Settings.save_creation)).strftime('%m/%d/%Y, %I:%M%p')}", x=10, y=35, anchor_x='left', anchor_y='center', bold=True, color=(255,255,255,255),
            font_name="Retro Gaming", font_size=10, batch=overlay_batch
            )

    def start_new_game(self):
        Settings.save_creation = int(datetime.utcnow().timestamp())
        
        self.columns = Terrain(Settings.seed_number).columns

        self.player = Player(self.window, self.main_camera, 100, self.columns, self.entity_list, batch=entity_batch)
        self.entity_list.append(self.player)

        self.window.push_handlers(self.player.key_handler)

        self.load_overlays()
        
    def load_saved_game(self):
        self.columns, player_data, enemy_data = self.load_game()

        score, kills, hp, item_count, x, y = player_data["score"], player_data["kills"], player_data["hp"], player_data["item_count"], player_data["pos"]["x"], player_data["pos"]["y"]
        self.player = Player(self.window, self.main_camera, hp, self.columns, self.entity_list, batch=entity_batch, score=score, kills=kills, item_count=item_count, x=x, y=y)
        self.entity_list.append(self.player)
        self.window.push_handlers(self.player.key_handler)
        
        for e in enemy_data:
            e.rstrip("\n")
            data = e.split(',')
            x, y, speed, hp = float(data[0]), float(data[1]), float(data[2]), float(data[3])
            self.entity_list.append(Enemy(self.player, self.window, self.columns, hp, x=x, y=y, speed=speed, batch=entity_batch))

        self.load_overlays()

    def create_enemy(self):
        # only create a new enemy if enough random time has passed and there are not too many enemies
        # spawnrate and total enemy count is controlled by the selected difficulty 
        if time.time() > (self.last_added_enemy + self.new_enemy_wait) and len(self.entity_list)-1 < (Settings.difficulty * 15):
            self.entity_list.append(Enemy(self.player, self.window, self.columns, 100, batch=entity_batch))
            self.last_added_enemy = time.time()
            self.new_enemy_wait = random.randint(3, (20 if Settings.difficulty == 1 else 10 if Settings.difficulty == 2 else 5))
            
    def update(self, dt):
        if Settings.game_started and not self.game_started:
            # only runs once on the game first running
            self.game_started = True
            if Settings.selected_save is None:
                self.start_new_game()
            else:
                self.load_saved_game()

        for e in list(self.entity_list):
            if e.shootable and not e.visible:
                # if e is an enemy and not visible it must be dead so remove
                self.entity_list.remove(e)
                # an enemy will only be dead if the player kills it, so increase score
                self.player.increase_score()
                # can't update the entity if it was removed so continue to the next
                continue
            e.update(dt)

        self.create_enemy()

        if (time.time()-self.last_quicksaved) >= 300:
            # 300 seconds have passed since the last quicksave
            print(f"\nQuicksaving {datetime.utcnow()}")
            self.save_game()
            self.last_quicksaved = time.time()

    def draw(self):
        with game.main_camera:
            # main camera moves with gameplay; static screen elements should be drawn without it
            main_batch.draw()
            entity_batch.draw()
            item_batch.draw()

        overlay_batch.draw()

    def save_game(self):
        directory = f"{APP_PATH}/saves/{Settings.save_creation}/"
        try:
            os.makedirs(os.path.dirname(directory))
        except FileExistsError:
            # directory already exists
            pass
        
        # player data
        print("Constructing player data...")
        player_dict = {"hp": self.player.health, "score": self.player.score, "kills": self.player.kills, "pos": {"x": self.player.x, "y": self.player.y}, "item_count": len(self.player.items)}

        # enemy data
        print("Constructing enemy data...")
        enemies = list()
        for e in self.entity_list:
            if type(e) == Enemy:
                enemies.append([str(e.x), str(e.y), str(e.speed), str(e.health)])

        # terrain data
        print("Constructing terrain data...")
        terrain_types = {None: "0", "top_grass": "1", "under_grass": "2", "dirt": "3", "wood": "4"}
        columns_rle = [[]] * len(self.columns)

        for c_index, c in enumerate(self.columns):
            consecutive = 1
            temp = list()
            # for each column, 1-500
            for b_index, block in enumerate(c):
                # for each block in the column, 1-100
                if b_index+1 != len(c):
                    # if the end of the column subarray was not reached in the iteration
                    if (c[b_index] is None and c[b_index+1] is None) or ((c[b_index] is not None and c[b_index+1] is not None) and (c[b_index].block_type == c[b_index+1].block_type)):
                        # if consecutive elements in the column are the same block type
                        consecutive += 1
                    else:
                        temp.append((str(consecutive), terrain_types[None if c[b_index] is None else c[b_index].block_type]))
                        consecutive = 1
                else:
                    # handle final element(s) in column when end of column is reached
                    temp.append((str(consecutive), terrain_types[None if c[b_index] is None else c[b_index].block_type]))
            columns_rle[c_index] = temp       
        
        # write terrain data
        print("Writing terrain data...")
        with open(directory+"terrain.txt", "w") as f:
            # first line will be the seed number
            f.write(f"{Settings.seed_number}\n")
            for index, c in enumerate(columns_rle):
                column_data = list()
                for rle_data in c:
                    # for each count and block type, separate it with a colon and add to column data
                    column_data.append(':'.join(rle_data))
                f.write(f"{','.join(column_data)}\n")
                #print(f"Column {index+1}/{len(columns_rle)} saved")

        # write player data
        print("Writing player data...")
        with open(directory+"player.json", "w") as f:
            json.dump(player_dict, f)

        # write enemy data
        print("Writing enemy data...")
        with open(directory+"enemies.txt", "w") as f:
            for e_info in enemies:
                f.write(f"{','.join(e_info)}\n")

    def load_game(self):
        directory = f"{APP_PATH}/saves/{Settings.save_creation}/"

        # read terrain data
        with open(directory+"terrain.txt", "r") as f:
            terrain_lines = f.readlines()

        # process terrain data
        terrain_types = {"0": None, "1": "top_grass", "2": "under_grass", "3": "dirt", "4": "wood"}
        columns = list()
        for index, c in enumerate(terrain_lines):
            if index == 0:
                Settings.seed_number = c.rstrip("\n")
                continue
            count = 0
            temp = list()
            rle_data = c.rstrip("\n").split(',')
            for data in rle_data:
                split = data.split(':')
                amount, b_code = int(split[0]), split[1]
                for i in range(amount):
                    count += 1
                    b_type = terrain_types[b_code]
                    if b_type is None:
                        temp.append(None)
                    else:
                        img = sprite_grass_top16 if b_type == "top_grass" else sprite_grass_under16  if b_type == "under_grass" else sprite_dirt16 if b_type == "dirt" else sprite_wood16
                        square = pyglet.sprite.Sprite(img, x=(index-1)*5, y=(101-count)*5, batch=main_batch)
                        square.scale = 0.3125 # 15/48 = 0.3125
                        square.block_type = b_type
                        temp.append(square)
                        
            columns.append(temp)

        # read player data
        with open(directory+"player.json", "r") as f:
            player_dict = json.load(f)

        # read enemy data
        with open(directory+"enemies.txt", "r") as f:
            enemy_lines = f.readlines()

        return columns, player_dict, enemy_lines


class Menu:
    def __init__(self):
        # initialise the ButtonPress class that creates the menu structure
        self.button_press = ButtonPress(window)
        # define the menu_objects list that holds active menu objects; buttons, text input, text labels
        self.menu_objects = list()
        # start the menu structure by creating the base main menu with all options available
        self.button_press.base(self.menu_objects)

        self.game_started = False

    def update(self, dt):
        if Settings.game_started and not self.game_started:
            self.game_started = True
            Settings.menu_active = False
        

    def draw(self):
        # menu-specific batches
        menu_background.draw()
        menu_buttons.draw()
        menu_text.draw()
      
    def on_mouse_press(self, x, y, button, modifier):
        for obj in self.menu_objects:
            if not type(obj) == Button:
                continue
            if (obj.rect.x-(obj.rect.width/2) <= x <= obj.rect.x+(obj.rect.width/2)):
                if (obj.rect.y-(obj.rect.height/2) <= y <= obj.rect.y+(obj.rect.height/2)):
                    # if the mouse is within the bounds of the button and clicked
                    self.press_button(obj)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pass
    
    def on_mouse_motion(self, x, y, dx, dy):
        for obj in self.menu_objects:
            if not isinstance(obj, Button):
                continue
            # set all buttons to a default color and size whilst the mouse is not over it
            obj.rect.color = (255,0,0)
            obj.resize(200)
            if (obj.rect.x-(obj.rect.width/2) <= x <= obj.rect.x+(obj.rect.width/2)):
                if (obj.rect.y-(obj.rect.height/2) <= y <= obj.rect.y+(obj.rect.height/2)):
                    # if the mouse is within the bounds of the button then change the color and size
                    obj.rect.color = (0,255,0)
                    obj.resize(225)
    
    def on_text(self, text):
        for obj in self.menu_objects:
            if isinstance(obj, TextButton):
                obj.on_text(text)
    
    def on_key_press(self, button, modifier):
        if button == key.TAB and not self.menu_objects:
            self.button_press.base(self.menu_objects)
        
        for obj in self.menu_objects:
            if isinstance(obj, TextButton):
                obj.on_key_press(button, modifier)

    def press_button(self, button):
        for obj in self.menu_objects:
            obj.delete()

        self.menu_objects.clear()

        if button.label.text:
            self.button_press.action_dict[button.label.text](self.menu_objects)


game = Game(window)
menu = Menu()


@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
    if not Settings.menu_active:
        game.main_camera.zoom += round(scroll_y*0.1, 1)
        game.main_camera.zoom = round(game.main_camera.zoom, 1)


@window.event
def on_mouse_press(x, y, button, modifier):
    # take input based on what is currently selected; game or menu
    if Settings.menu_active:
        menu.on_mouse_press(x, y, button, modifier)
    else:
        if game.entity_list:
            # make sure the player has initialised before taking input
            game.player.on_mouse_press(x, y, button, modifier)


@window.event
def on_mouse_motion(x, y, dx, dy):
    if Settings.menu_active:
        menu.on_mouse_motion(x, y, dx, dy)
    else:
        if game.entity_list:
            # make sure the player has initialised before taking input
            game.player.on_mouse_motion(x, y, dx, dy)

@window.event
def on_mouse_drag(x, y, dx, dy, button, modifier):
    if Settings.menu_active:
        menu.on_mouse_drag(x, y, dx, dy, button, modifier)
    else:
        if game.entity_list:
            # make sure the player has initialised before taking input
            game.player.on_mouse_drag(x, y, dx, dy, button, modifier)

@window.event
def on_key_press(button, modifier):
    if button == key.TAB:
        # toggle menu
        if Settings.game_started:
            # only allow toggling the menu once the game has already started; keep menu active otherwise
            Settings.menu_active = not Settings.menu_active

    # take input based on what is currently selected; game or menu
    if Settings.menu_active:
        menu.on_key_press(button, modifier)
    else:
        if game.entity_list:
            game.player.on_key_press(button, modifier)


@window.event
def on_text(text):
    if Settings.menu_active:
        menu.on_text(text)


@window.event
def on_draw():
    window.clear()

    # draw different scenes based on what is currently selected; game or menu
    if Settings.menu_active:
        menu.draw()
    else:
        game.draw()


def update(dt):
    # update different scenes based on what is currently selected; game or menu
    if Settings.menu_active:
         menu.update(dt)
    else:
        game.update(dt)

    if Settings.game_quit:
        if not Settings.game_started:
            window.close()
        else:
            if len(menu.menu_objects) == 1:
                # make sure menu displays right message before running intensive save function
                game.save_game()
                window.close()
                pyglet.app.exit()

if __name__ == "__main__":
    Highscores.check_schema()
    pyglet.clock.schedule_interval(update, 1/60) # schedule at 60fps
    pyglet.app.run() # blocking loop function that runs each frame of the game
