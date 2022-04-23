import time

from resources import *

class ItemShooter(Item):
    def __init__(self, shooter_type, *args, **kwargs):
        shooter_type = ShooterType[shooter_type]
        kwargs['img'] = shooter_type.value["sprite"]
        self.projectile_type = shooter_type.value["projectile"]

        self.rate = shooter_type.value["rate"]
        self.last_fired = 0
        
        super().__init__(*args, **kwargs)

        self.projectiles = []
        
    def use(self, mouse_x, mouse_y):
        if time.time() - self.last_fired < self.rate:
            return
        
        dx = mouse_x-self.player.x
        angle = math.atan2(mouse_y-self.player.y, dx)
        
        self.projectiles.append(Projectile(self.player.columns, self.projectile_type, angle, dx, self.player.entity_list, x=self.x, y=self.y, batch=item_batch))
        self.last_fired = time.time()
        
    def update(self, dt):
        super().update(dt)

        for p in self.projectiles:
            p.update(dt)

        for p in list(self.projectiles):
            if not p.visible:
                self.projectiles.remove(p)
