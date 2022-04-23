import math
import sys
print("Appending pyglet path...")
sys.path.append("N:\Desktop\\")
import pyglet
import time

from resources import * 


window = pyglet.window.Window(width=1080, height=720)

class Game:
    def __init__(self, window):
        self.window = window

        self.fps_display = pyglet.window.FPSDisplay(self.window)
        self.fps_display.label.y = self.window.height - 60
        self.fps_display.label.batch = overlay_batch

        self.columns = Terrain(4374).columns

        self.main_camera = Camera(min_zoom=0.5, max_zoom=3)
        self.entity_list = []

        self.player = Player(self.window, self.main_camera, self.columns, self.entity_list, batch=entity_batch)
        self.entity_list.append(self.player)

        self.window.push_handlers(self.player.key_handler)
        self.window.push_handlers(self.player)

    def create_enemy(self):
        self.entity_list.append(Enemy(self.player, self.window, self.columns, batch=entity_batch))

    def update(self, dt):
        for e in list(self.entity_list):
            if e.shootable and not e.visible:
                # if e is an enemy and not visible it must be dead so remove
                self.entity_list.remove(e)
                # an enemy will only be dead if the player kills it, so increase score
                self.player.increase_score()
                # can't update the entity if it was removed so continue to the next
                continue
            e.update(dt)


game = Game(window)

@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
    main_camera.zoom += round(scroll_y*0.1, 1)
    main_camera.zoom = round(main_camera.zoom, 1)


@window.event
def on_mouse_press(x, y, button, modifier):
    if button == 4:
        game.create_enemy()
    #TODO
    game.player.on_mouse_press(x, y, button, modifier)


@window.event
def on_draw():
    window.clear()
    
    with game.main_camera:
        main_batch.draw()
        entity_batch.draw()
        item_batch.draw()

    overlay_batch.draw()

pyglet.clock.schedule_interval(game.update, 1/60)    # schedule at 60fps
pyglet.app.run()
