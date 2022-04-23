import math
import random

import pyglet

from resources import *


class Vector:
    """
    Dataclass that holds an X and Y value to act as a vector representation
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Terrain:
    def __init__(self, seed=None):
        # generate seed starting value if one was not given
        self.seed = seed if seed is not None else random.randint(1000,9999)

        self.heights = self.terrain_heights()
        self.columns = self.generate_columns()

    def terrain_heights(self):
        """
        Generates a heights list of perlin generated values to then be passed to generate terrain columns
        """

        # holds a list of y values that are the topmost height what will be each terrain column
        heights = []

        # generates 500 Y values from inputted start point + 500
        for i in range(self.seed, self.seed+500):

            # generate and floor y_val to receive integer value and increase it by 50; generated value is too low down
            y_val = math.floor(self.generate_y_val(i)) + 50
            
            heights.append(y_val)
            
        return heights

    def generate_columns(self):
        columns = []

        # iterate through the Y values generated alongside the index of each; row number
        # for each row:
        for row_index, y_val in enumerate(self.heights):
            squares_in_column = []

            # iterate from the highest Y value in the column down to 0; highest to lowest height in each column
            # for each square in the column:
            for i in range(y_val, 0, -1):
                """ # 15x15 at full zoom
                # Green for topmost square and then brown underneath with more red element as squares go down
                color = (0, 255, 0) if i - y_val == 0 else (79+int(79*(y_val-i)/y_val), 45, 8)

                # create pyglet square (rectangle) object with position based on row index and Y height
                squares_in_column.append(
                    pyglet.shapes.Rectangle(x=row_index*5, y=i*5, width=5, height=5, color=color, batch=main_batch)
                    )
                """
                # 24x24 at 0.5 at full zoom therefore
                # 48*48 at full zoom
                img = sprite_grass_top16 if i - y_val == 0 else sprite_grass_under16  if i - y_val == -1 else sprite_dirt16
                img_name = "top_grass"  if i - y_val == 0 else "under_grass"  if i - y_val == -1 else "dirt"
                square = pyglet.sprite.Sprite(img, x=row_index*5, y=i*5, batch=main_batch)
                square.scale = 0.3125 # 15/48 = 0.3125
                square.block_type = img_name
                squares_in_column.append(square)
                
            # make sure all columns are the same length
            # pad with None objects to act as 'empty' space we we can later use
            # player-placed blocks will need to override empty spaces
            none_list = [None]*(100-len(squares_in_column))
            none_list.extend(squares_in_column)
            columns.append(none_list)
        return columns

    def interpolate(self, a0: float, a1: float, weight: float) -> float:
        """
        Finds a point between a0 and a1 given a weight of how far along
        """
        return (a1 - a0) * (3.0 - weight * 2.0) * weight * weight + a0


    def random_gradient(self, ix: float, iy: float) -> Vector:
        """
        -Generates a vector with a random gradient seeded by ix and iy - pseudorandom number generator / hashing algorithm
        """
        random = 2920 * math.sin(ix * 21942 + iy * 171324 + 8912) * math.cos(ix * 23157 * iy * 217832 + 9758)
        return Vector( math.cos(random), math.sin(random) )


    # Finds a cosine of the angle between 2 vectors
    def dot_grid_gradient(self, ix: float, iy: float, x: float, y: float) -> float:
        """
        -Gets random vector
        -Finds difference between two inputted X and Y values to .... 
        
        -Returns to be used in perlin values
        """
        v_gradient = self.random_gradient(ix, iy)

        dx = x - ix
        dy = y - iy

        return (dx * v_gradient.x + dy * v_gradient.y)
        

    def perlin(self, x: float, y: float) -> float:
        x0 = math.floor(x)
        x1 = x0 + 1
        y0 = math.floor(y)
        y1 = y0 + 1

        sx = x - x0
        sy = y - y0

        n0 = self.dot_grid_gradient(x0, y0, x, y)
        n1 = self.dot_grid_gradient(x1, y0, x, y)
        ix0 = self.interpolate(n0, n1, sx)

        n0 = self.dot_grid_gradient(x0, y1, x, y)
        n1 = self.dot_grid_gradient(x1, y1, x, y)
        ix1 = self.interpolate(n0, n1, sx)

        value = self.interpolate(ix0, ix1, sy)
        return value


    def octave(self, iterations: int, x: float, y: float) -> float:
        amp_power = 0.33
        total = 0
        d = (iterations-1)**2
        for i in range(iterations):
            freq = i**2 / d
            amp = i**amp_power * 5
            total += self.perlin(x*freq, y*freq) * amp
        return total

    def generate_y_val(self, i):
        return (self.octave(32, i/50, i/50))


        
