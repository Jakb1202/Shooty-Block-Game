import pyglet

from resources import *

import time


class TimedText(pyglet.text.Label):
    def __init__(self, duration_seconds, *args, **kwargs):
        super().__init__(font_name="Retro Gaming", batch=overlay_batch, *args, **kwargs)
        self.creation_time = time.time()
        self.duration_seconds = duration_seconds

    def has_expired(self):
        if time.time() > (self.creation_time + self.duration_seconds):
            self.delete()
            return True
