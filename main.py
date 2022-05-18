import ursina
from ursina import *
from ursina import curve
from Player import Player, shootables_parent
app = Ursina()
window.title = 'My Game'  # The window title
window.borderless = False  # Show a border
window.fullscreen = True
window.exit_button.visible = False  # Do not show the in-game red X that loses the window
window.fps_counter.enabled = True
window.fps_counter.scale_x = 4
window.fps_counter.scale_y = 4
window.fps_counter.x = 0.9
window.fps_counter.color = color.red



class Enemy(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=shootables_parent, model='cube', scale=2.5, origin_y=-.5,
                         collider='box', **kwargs)
        self.health_bar = Entity(parent=self, y=1.2, model='cube', color=color.red, world_scale=(1.5, .1, .1))
        self.max_hp = 50
        self.hp = self.max_hp

    def update(self):
        dist = distance_xz(player.position, self.position)
        if dist > 40:
            return

        self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)

        self.look_at_2d(player.position, 'y')
        hit_info = ursina.raycast(self.world_position + Vec3(0, 1, 0), self.forward, 30, ignore=(self,))
        if hit_info.entity == player:
            if dist > 4:
                self.position += self.forward * time.dt * 5
                shootEnemy()

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        self._hp = value
        if value <= 0:
            destroy(self)
            return

        self.health_bar.world_scale_x = self.hp / self.max_hp * 1.5
        self.health_bar.alpha = 1
enemy1 = Enemy(x=50, z=50)
EnemyGun = Entity(model='cube', parent=enemy1, position=(.5, .5, .25), scale=(.3, .2, 1), origin_z=-.5,
                  color=color.blue,
                  on_cooldown=False)
EnemyGun.muzzle_flash = Entity(parent=EnemyGun, z=1, world_scale=.5, model='quad', color=color.yellow, enabled=False)




def shootEnemy():
    if not EnemyGun.on_cooldown:
        EnemyGun.on_cooldown = True
        EnemyGun.muzzle_flash.enabled = True
        invoke(EnemyGun.muzzle_flash.disable, delay=.05)
        invoke(setattr, EnemyGun, 'on_cooldown', False, delay=.15)
        from ursina.prefabs.ursfx import ursfx
        ursfx([(0.0, 0.0), (0.1, 0.9), (0.15, 0.75), (0.3, 0.14), (0.6, 0.0)], volume=0.5, wave='noise',
              pitch=random.uniform(-13, -12), pitch_change=-12, speed=3.0)
        player.hp -= 10


EnemyGun.parent = enemy1
if __name__ == '__main__':
    ground = Entity(model='plane', scale=(100, 1, 100), color=color.yellow.tint(-.2), texture='white_cube',
                    texture_scale=(100, 100), collider='box')
    e = Entity(model='cube', scale=(1, 5, 10), x=2, y=.01, rotation_y=45, collider='box', texture='white_cube')
    e.texture_scale = (e.scale_z, e.scale_y)
    e = Entity(model='cube', scale=(1, 5, 10), x=-2, y=.01, collider='box', texture='white_cube')
    e.texture_scale = (e.scale_z, e.scale_y)

    player = Player(y=2, origin_y=-.5)
    player.collider = BoxCollider(player, Vec3(0, 1, 0), Vec3(1, 2, 1))

    slope = Entity(model='cube', collider='box', position=(0, 0, 8), scale=6, rotation=(45, 0, 0), texture='brick',
                   texture_scale=(8, 8))
    slope = Entity(model='cube', collider='box', position=(5, 0, 10), scale=6, rotation=(80, 0, 0), texture='brick',
                   texture_scale=(8, 8))
    hp = player.hp
    hp2 = "HP: {}".format(hp)
    health = Text(text=hp2)
    health.x = -0.85
    health.y = 0.465
    info = Text(text="Controls:\n"
                     "Move forward: W\n"
                     "Move backwards: A\n"
                     "Move left: A\n"
                     "Move right: D\n"
                     "Jump: space\n"
                     "Fire: right mouse")
    info.x = -0.85
    info.y = 0.465
    info.background = True
    info.visible = False

    app.run()
