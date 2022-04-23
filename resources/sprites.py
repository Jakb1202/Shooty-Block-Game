import pyglet

from resources import *


def anchor(sprite):
    sprite.anchor_x = sprite.width // 2
    sprite.anchor_y = sprite.height // 2


sprite_blank1 = pyglet.image.load("resources/sprite_images/blank1x1.png")

sprite_bow16 = pyglet.image.load("resources/sprite_images/bow16x16.png")
anchor(sprite_bow16)

sprite_arrow16 = pyglet.image.load("resources/sprite_images/arrow16x16.png")
anchor(sprite_arrow16)

sprite_pistol16 = pyglet.image.load("resources/sprite_images/pistol16x16.png")
anchor(sprite_pistol16)

sprite_bullet16 = pyglet.image.load("resources/sprite_images/bullet16x16.png")
anchor(sprite_bullet16)

sprite_sword16 = pyglet.image.load("resources/sprite_images/sword16x16.png")
anchor(sprite_sword16)

sprite_miner16 = pyglet.image.load("resources/sprite_images/miner16x16.png")
anchor(sprite_miner16)

sprite_bomb16 = pyglet.image.load("resources/sprite_images/bomb16x16.png")
anchor(sprite_bomb16)

sprite_explosion32 = pyglet.image.load("resources/sprite_images/explosion32x32.png")
anchor(sprite_explosion32)

sprite_grass_top16 = pyglet.image.load("resources/sprite_images/grass_top16x16.png")
sprite_grass_under16 = pyglet.image.load("resources/sprite_images/grass_under16x16.png")
sprite_dirt16 = pyglet.image.load("resources/sprite_images/dirt16x16.png")
sprite_wood16 = pyglet.image.load("resources/sprite_images/wood16x16.png")
