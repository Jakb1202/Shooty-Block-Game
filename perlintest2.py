import math
import pyglet


START = 4236
SCALE = 5

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def interpolate(a0: float, a1: float, weight: float) -> float:
    return (a1 - a0) * (3.0 - weight * 2.0) * weight * weight + a0


def random_gradient(ix: float, iy: float) -> Vector:
    random = 2920 * math.sin(ix * 21942 + iy * 171324 + 8912) * math.cos(ix * 23157 * iy * 217832 + 9758)
    return Vector( math.cos(random), math.sin(random) )


# Finds a cosine of the angle between 2 vectors
def dot_grid_gradient(ix: float, iy: float, x: float, y: float) -> float:
    v_gradient = random_gradient(ix, iy)

    dx = x - ix
    dy = y - iy

    return (dx * v_gradient.x + dy * v_gradient.y)
    

def perlin(x: float, y: float) -> float:
    x0 = math.floor(x)
    x1 = x0 + 1
    y0 = math.floor(y)
    y1 = y0 + 1

    sx = x - x0
    sy = y - y0

    n0 = dot_grid_gradient(x0, y0, x, y)
    n1 = dot_grid_gradient(x1, y0, x, y)
    ix0 = interpolate(n0, n1, sx)

    n0 = dot_grid_gradient(x0, y1, x, y)
    n1 = dot_grid_gradient(x1, y1, x, y)
    ix1 = interpolate(n0, n1, sx)

    value = interpolate(ix0, ix1, sy)
    return value


def octave(iterations: int, x: float, y: float) -> float:
    amp_power = 0.3
    total = 0
    d = (iterations-1)**2
    for i in range(iterations):
        freq = i**2 / d
        amp = i**amp_power * 5
        total += perlin(x*freq, y*freq) * amp
    return total


def generate_noise():
    global START
    for i in range(START, START+200):
        yield (octave(32, i/50, i/50))


def generate_y_val(i):
    return (octave(32, i/50, i/50))


class Terrain:
    def __init__(self):
        self.heights = self.terrain_heights()
        self.columns = self.generate_columns()

    def terrain_heights(self):
        heights = []
        for i in range(START, START+500):
            y_val = math.floor(generate_y_val(i)) + 50
            heights.append(y_val)
        return heights

    def generate_columns(self):
        columns = []
        for row_index, y_val in enumerate(self.heights):

            squares_in_column = []
            for i in range(y_val, 1, -1):  # go from the highest to the lowest height
                """if row_index % 2 == 0:
                     color = (255, 0, 0)
                else:
                    color = (20, 255, 20)"""
                color = (0, 255, 0) if i - y_val == 0 else (79+int(79*(y_val-i)/y_val), 45, 8)
                squares_in_column.append(
                    pyglet.shapes.Rectangle(
                        x=row_index*SCALE, y=i*SCALE, width=SCALE, height=SCALE,
                        color=color, batch=batch
                        )
                    )

            columns.append(squares_in_column)

        return columns

from camera import Camera
camera = Camera(min_zoom=0.5)

window = pyglet.window.Window(width=1080, height=720)
batch = pyglet.graphics.Batch()

@window.event
def on_draw():
    window.clear()
    with camera:
        batch.draw()

@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
    camera.zoom += scroll_y*0.1

columns = Terrain().columns

pyglet.app.run()
