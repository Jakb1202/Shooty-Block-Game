import sys
print("Appending pyglet path...")
sys.path.append("\\\\tws-fs02\\intake15$\\15JWhite\\Desktop\\")
from datetime import datetime, timedelta
import random
import math
import matplotlib as mpl
import matplotlib.pyplot as plot
import pyglet
from pyglet.window import key
import time

M = 4294967296
A = 1664525
C = 1

Z1 = math.floor(random.random() * M)


def rand():
    Z = (A * Z1 + C) % M
    return Z / M - 0.5


def interpolate(pa, pb, px):
    ft = px * math.pi
    f = (1 - math.cos(ft)) * 0.5
    return pa * (1 - f) + pb * f


def interpolate_linear(pa, pb, px):
    return a * (1 - x) + b * x


def generate_noise():
    y = 0
    start_height = 20
    w = 300
    amp = 10
    wl = 20
    fq = 1 / wl
    a = random.random()
    b = random.random()
    
    x_vals = []
    y_vals = []
    
    for x in range(w):
        
        if (x % wl == 0):
            a = b
            b = random.random()
            y = start_height / 2 + a * amp
        else:
            y = start_height / 2 + interpolate(a, b, (x % wl) / wl) * amp
        y = round(y) + 15
        y_vals.append(y)
        x_vals.append(x)
        #x += 1
    return x_vals, y_vals

"""
x_vals, y_vals = generate_noise()
print(len(x_vals))
print(len(y_vals))
plot.plot(x_vals, y_vals, marker="x")
plot.ylim(0, 50)
plot.xlim(0, 300)
plot.show()

"""
window = pyglet.window.Window(width=1080, height=720)
squares_batch = pyglet.graphics.Batch()


class Terrain:
    def __init__(self):
        self.squares_list = self.generate_terrain()

    def generate_terrain(self):
        x_vals, y_vals = generate_noise()
        squares_list = []
        for index, y_val in enumerate(y_vals):
            x_val = index +1

            if index+1 == len(y_vals):
                color = (0, 0, 255)
            elif index % 2 == 0:
                color = (255, 0, 0)
            else:
                color = (20, 255, 20)
            
            new_square = pyglet.shapes.Rectangle(x=x_val*5, y=y_val*5, width=5, height=5, color=color, batch=squares_batch)
            squares_list.append(new_square)
        return squares_list


@window.event
def on_draw():
    window.clear()
    squares_batch.draw()


def function(dt):
    global squares_list
    squares_list = Terrain().squares_list

squares_list = Terrain().squares_list
pyglet.clock.schedule_interval(function, 1/60)    # schedule at 60fps
pyglet.app.run()

