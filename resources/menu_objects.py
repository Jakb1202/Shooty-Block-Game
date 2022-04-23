import pyglet
from pyglet import font
from pyglet.window import key

from resources import *

from datetime import datetime
import os
import random


font.add_file("resources/Retro Gaming.ttf")
retro_font = font.load("Retro Gaming")


class Button:
    def __init__(self, text, width=200, x=0, y=0):
        self.width = width
        self.height = int(width/21*9)
        self.rect = pyglet.shapes.Rectangle(x=x, y=y, width=width, height=self.height, color=(255,0,0), batch=menu_buttons)
        self.anchor()
        self.label = pyglet.text.Label(text, x=x, y=y, anchor_x='center', anchor_y='center', bold=True, batch=menu_text)

    def update_position(self, x, y):
        self.rect.x, self.rect.y = x, y
        self.label.x, self.label.y = x, y

    def resize(self, width):
        self.rect.width = width
        self.rect.height = int(width/21*9)
        self.anchor()

    def anchor(self):
        self.rect.anchor_x, self.rect.anchor_y = self.rect.width//2, self.rect.height//2

    def delete(self):
        self.rect.delete()
        self.label.delete()


class TextButton(Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text_buffer = []
        Settings.button_buffer = None
        
    def on_text(self, text):
        if len(self.text_buffer) < 16:
            self.text_buffer.append(text)
        self.label.text = ''.join(self.text_buffer)
        Settings.button_buffer = self.label.text

    def on_key_press(self, button, modifier):
        if button == key.BACKSPACE:
            self.text_buffer.clear()
            self.label.text = ""
            Settings.button_buffer = None


class ButtonPress:
    def __init__(self, window):
        self.window = window
        self.x_center = self.window.width//2
        self.y_center = self.window.height//2
        
        self.action_dict = {
            "Back": self.base,
            "Play Game": self.play_game,
            "Highscores": self.highscores,
            "Options": self.options,
            "Quit": self.quit_menu,
            "Cancel": self.base,
            "Yes": self.close_window,
            "New Game": self.new_game,
            "Randomise value": self.random_seed,
            "Start world": self.start_world,
            "Peaceful": self.peaceful,
            "Easy": self.easy,
            "Medium": self.medium,
            "Hard": self.hard,
            "Load Game": self.load_game,
            "Load Save": self.load_save,
            "Submit Score": self.submit_score,
            "New User": self.new_user,
            "Existing User": self.existing_user,
            "Create User": self.create_user,
            "Update User": self.update_user
            }

    def base(self, menu_objects):
        # base main menu structure
        # if the game has already started then the options to start a new game should be removed and elements are realligned
        if Settings.game_started:
            text = "Menu"
            x_vals =  [self.x_center, self.x_center, self.x_center, self.x_center, self.x_center]
            y_vals = [525, 1000, 425, 300, 175]
            menu_objects.append(pyglet.text.Label(
                    "Press TAB to return to the game", x=self.x_center, y=15 , anchor_x='center', anchor_y='center',  font_size=10, font_name="Retro Gaming", batch=menu_text
            ))
        else:
            text = "Shooty block game!"
            x_vals = [self.x_center, self.x_center, self.x_center, self.x_center-125, self.x_center+125]
            y_vals = [575, 450, 300, 150, 150]

        menu_objects.append(pyglet.text.Label(
            text, x=x_vals[0], y=y_vals[0] , anchor_x='center', anchor_y='center', font_size=50, font_name="Retro Gaming", batch=menu_text
        ))
        menu_objects.append(Button("Play Game", x=x_vals[1], y=y_vals[1]))
        menu_objects.append(Button("Highscores", x=x_vals[2], y=y_vals[2]))
        menu_objects.append(Button("Options", x=x_vals[3], y=y_vals[3]))
        menu_objects.append(Button("Quit", x=x_vals[4], y=y_vals[4]))
    
    def play_game(self, menu_objects):
        menu_objects.append(Button("New Game", x=self.x_center, y=450))
        menu_objects.append(Button("Load Game", x=self.x_center, y=300))
        menu_objects.append(Button("Back", x=125, y=75))

    def highscores(self, menu_objects):
        scores = Highscores.select_all_scores()
        menu_objects.append(pyglet.text.Label(
            f"Name:    Score:    Kills:", x=self.x_center, y=(675)-(len(scores)*2.5), anchor_x='center', anchor_y='center',  font_size=12, batch=menu_text
            ))
        for index, s in enumerate(scores):
            menu_objects.append(pyglet.text.Label(
            f"{s[0]}        {s[1]}        {s[2]}", x=self.x_center, y=(650)-(index*25)-(len(scores)*2.5), anchor_x='center', anchor_y='center',  font_size=12, batch=menu_text
            ))
        
        menu_objects.append(pyglet.text.Label(
            "Highscores:", x=self.x_center, y=700-(len(scores)*2.5), anchor_x='center', anchor_y='center', font_size=18, font_name="Retro Gaming", color=(0,255,0,255), batch=menu_text
        ))
        menu_objects.append(Button("Back", x=125, y=75))
        menu_objects.append(Button("Submit Score", x=955, y=75))

    def submit_score(self, menu_objects):
        if Settings.game_started:
            menu_objects.append(Button("New User", x=self.x_center, y=450))
            menu_objects.append(Button("Existing User", x=self.x_center, y=300))
        else:
            menu_objects.append(pyglet.text.Label(
            "You can only submit scores when in a game.", x=self.x_center, y=self.y_center, anchor_x='center', anchor_y='center', font_size=18, font_name="Retro Gaming", color=(0,255,0,255), batch=menu_text
        ))
        menu_objects.append(Button("Back", x=125, y=75))

    def new_user(self, menu_objects):
        menu_objects.append(Button("Back", x=125, y=75))
        menu_objects.append(pyglet.text.Label(
            "Enter username", x=self.x_center, y=(self.y_center)+175 , anchor_x='center', anchor_y='center', font_size=15, font_name="Retro Gaming", batch=menu_text
        ))
        if not any(isinstance(x, TextButton) for x in menu_objects):
            menu_objects.append(TextButton("", x=self.x_center, y=450))
        menu_objects.append(Button("Create User", x=955, y=75))
    
    def create_user(self, menu_objects):
        if Settings.button_buffer is None:
            menu_objects.append(TextButton("", x=self.x_center, y=450))
            self.new_user(menu_objects)
        else:
            user_id = Highscores.insert_user(Settings.button_buffer)
            Highscores.insert_score(user_id, Settings.score, Settings.kills)
            self.highscores(menu_objects)
    
    def existing_user(self, menu_objects):
        menu_objects.append(Button("Back", x=125, y=75))
        users = Highscores.select_names()
        
        menu_objects.append(pyglet.text.Label(
            "User ID:    Name:", x=self.x_center, y=700-(len(users)*2.5), anchor_x='center', anchor_y='center', font_size=18, font_name="Retro Gaming", color=(0,255,0,255), batch=menu_text
        ))
        for index, u in enumerate(users):
            menu_objects.append(pyglet.text.Label(
            f"{u[0]}        {u[1]}", x=self.x_center, y=(650)-(index*25)-(len(users)*2.5), anchor_x='center', anchor_y='center',  font_size=12, batch=menu_text
        ))

        menu_objects.append(pyglet.text.Label(
            "Enter user ID to update", x=self.x_center, y=150 , anchor_x='center', anchor_y='center', font_size=15, font_name="Retro Gaming", batch=menu_text
        ))
        if not any(isinstance(x, TextButton) for x in menu_objects):
            menu_objects.append(TextButton("", x=self.x_center, y=75))
        menu_objects.append(Button("Update User", x=955, y=75))

    def update_user(self, menu_objects):
        if Settings.button_buffer is None or not Settings.button_buffer.isdigit():
            menu_objects.append(TextButton("", x=self.x_center, y=75))
            self.existing_user(menu_objects)
        else:
            user_id = int(Settings.button_buffer)
            Highscores.update_score(user_id, Settings.score, Settings.kills)
            self.highscores(menu_objects)
    
    def options(self, menu_objects):
        menu_objects.append(Button("Back", x=125, y=75))
        menu_objects.append(pyglet.text.Label(
            "Selected difficulty:", x=self.x_center, y=self.y_center+75 , anchor_x='center', anchor_y='center', font_size=20, font_name="Retro Gaming", batch=menu_text
        ))
        menu_objects.append(Button([diff for diff in list(Settings.difficulty_dict.keys()) if Settings.difficulty_dict[diff] == Settings.difficulty][0], x=self.x_center, y=self.y_center))

    def peaceful(self, menu_objects):
        Settings.difficulty = 1
        self.options(menu_objects)
        
    def easy(self, menu_objects):
        Settings.difficulty = 2
        self.options(menu_objects)
        
    def medium(self, menu_objects):
        Settings.difficulty = 3
        self.options(menu_objects)

    def hard(self, menu_objects):
        Settings.difficulty = 0
        self.options(menu_objects)

    def quit_menu(self, menu_objects):
        menu_objects.append(pyglet.text.Label(
            "Are you sure you want to quit the game?", x=self.x_center, y=(self.y_center)+120 , anchor_x='center', anchor_y='center',  font_size=15, font_name="Retro Gaming", batch=menu_text
        ))
        menu_objects.append(pyglet.text.Label(
            "All progress will be saved.", x=self.x_center, y=(self.y_center)+80 , anchor_x='center', anchor_y='center',  font_size=15, font_name="Retro Gaming", batch=menu_text
        )) 
        menu_objects.append(Button("Yes", x=(self.x_center)+150, y=self.y_center))
        menu_objects.append(Button("Cancel", x=(self.x_center)-150, y=self.y_center))

    def close_window(self, menu_objects):
        menu_objects.append(pyglet.text.Label(
            "Game saving, please wait...", x=self.x_center, y=self.y_center , anchor_x='center', anchor_y='center',  font_size=20, font_name="Retro Gaming", batch=menu_text
        ))
        Settings.game_quit = True
        
    def new_game(self, menu_objects):
        menu_objects.append(Button("Back", x=125, y=75))
        if not any(isinstance(x, TextButton) for x in menu_objects):
            menu_objects.append(TextButton("", x=self.x_center, y=450))
        menu_objects.append(pyglet.text.Label(
            "Enter World Seed Value", x=self.x_center, y=(self.y_center)+175 , anchor_x='center', anchor_y='center', font_size=15, font_name="Retro Gaming", batch=menu_text
        ))
        menu_objects.append(pyglet.text.Label(
            "Or", x=self.x_center, y=(self.y_center)+5 , anchor_x='center', anchor_y='center',font_size=15, font_name="Retro Gaming", batch=menu_text
        )) 
        menu_objects.append(Button("Randomise value", x=(self.x_center), y=(self.y_center)-75))
        menu_objects.append(Button("Start world", x=955, y=75))

    def random_seed(self, menu_objects):
        seed_number = random.randint(10000000, 99999999)
        Settings.seed_number = seed_number
        menu_objects.append(TextButton(str(seed_number), x=self.x_center, y=450))
        self.new_game(menu_objects)

    def start_world(self, menu_objects):
        if Settings.button_buffer is not None:
            Settings.seed_number = int(Settings.button_buffer)
        if Settings.seed_number  is None:
            menu_objects.append(TextButton("", x=self.x_center, y=450))
            self.new_game(menu_objects)
        else:
            Settings.game_started = True
            # override selected_save to None incase the load screen was selected before starting a new world
            Settings.selected_save = None

    def load_game(self, menu_objects):
        if not os.path.exists(os.getcwd()+"/saves"):
            os.makedirs(os.getcwd()+"/saves")
        saves = [[datetime.fromtimestamp(int(t)).strftime("%m/%d/%Y, %I:%M%p"), t]  for t in os.listdir(os.getcwd()+"/saves")]

        menu_objects.append(pyglet.text.Label(
            "Available saves:", x=self.x_center, y=700-(len(saves)*2.5), anchor_x='center', anchor_y='center', font_size=18, font_name="Retro Gaming", color=(0,255,0,255), batch=menu_text
        ))
        menu_objects.append(Button("Back", x=125, y=75))
        for index, s in enumerate(saves):
            menu_objects.append(pyglet.text.Label(
            f"{index+1}: {s[0]}", x=self.x_center, y=(650)-(index*25)-(len(saves)*2.5), anchor_x='center', anchor_y='center',  font_size=12, batch=menu_text
            ))
        menu_objects.append(pyglet.text.Label(
            "Enter save to play:", x=self.x_center, y=150, anchor_x='center', anchor_y='center', font_size=18, font_name="Retro Gaming", batch=menu_text
        ))
        if not any(isinstance(x, TextButton) for x in menu_objects):
            menu_objects.append(TextButton("", x=self.x_center, y=75))
        menu_objects.append(Button("Load Save", x=955, y=75))

    def load_save(self, menu_objects):
        saves = [[datetime.fromtimestamp(int(t)).strftime("%m/%d/%Y, %I:%M%p"), t]  for t in os.listdir(os.getcwd()+"/saves")]
        if Settings.button_buffer is not None and Settings.button_buffer.isdigit():
            Settings.selected_save = int(Settings.button_buffer)

        if Settings.selected_save is None or (Settings.selected_save-1 not in range(len(saves))):
            menu_objects.append(TextButton("", x=self.x_center, y=75))
            self.load_game(menu_objects)
        else:
            Settings.save_creation = saves[Settings.selected_save-1][1]
            Settings.game_started = True
