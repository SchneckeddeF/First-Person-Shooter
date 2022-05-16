import ursina
from ursina import *
from ursina import curve


app = Ursina()
gun = Entity(model='cube', parent=camera, position=(.5, -.25, .25), scale=(.3, .2, 1), origin_z=-.5, color=color.red,
             on_cooldown=False)

gun.muzzle_flash = Entity(parent=gun, z=1, world_scale=.5, model='quad', color=color.yellow, enabled=False)
EnemyGun = Entity(model='cube', parent=camera, position=(.5, -.25, .25), scale=(.3, .2, 1), origin_z=-.5,
                  color=color.red,
                  on_cooldown=False)
EnemyGun.muzzle_flash = Entity(parent=gun, z=1, world_scale=.5, model='quad', color=color.yellow, enabled=False)

shootables_parent = Entity()
mouse.traverse_target = shootables_parent


def shootEnemy():
	if not EnemyGun.on_cooldown:
		print('shoot')
		EnemyGun.on_cooldown = True
		EnemyGun.muzzle_flash.enabled = True
		invoke(EnemyGun.muzzle_flash.disable, delay=.05)
		invoke(setattr, EnemyGun, 'on_cooldown', False, delay=.15)
		from ursina.prefabs.ursfx import ursfx
		ursfx([(0.0, 0.0), (0.1, 0.9), (0.15, 0.75), (0.3, 0.14), (0.6, 0.0)], volume=0.5, wave='noise',
		      pitch=random.uniform(-13, -12), pitch_change=-12, speed=3.0)
		# if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
		# 	mouse.hovered_entity.hp -= 10
		# 	mouse.hovered_entity.blink(color.red)


def shoot():
	if not gun.on_cooldown:
		print('shoot')
		gun.on_cooldown = True
		gun.muzzle_flash.enabled = True
		invoke(gun.muzzle_flash.disable, delay=.05)
		invoke(setattr, gun, 'on_cooldown', False, delay=.15)
		from ursina.prefabs.ursfx import ursfx
		ursfx([(0.0, 0.0), (0.1, 0.9), (0.15, 0.75), (0.3, 0.14), (0.6, 0.0)], volume=0.5, wave='noise',
		      pitch=random.uniform(-13, -12), pitch_change=-12, speed=3.0)
		if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
			mouse.hovered_entity.hp -= 10
			mouse.hovered_entity.blink(color.red)


class Player(Entity):
	def __init__(self, **kwargs):
		self.cursor = Entity(parent=camera.ui, model='quad', color=color.pink, scale=.008, rotation_z=45)
		super().__init__()
		self.speed = 5
		self.height = 2
		self.camera_pivot = Entity(parent=self, y=self.height)

		camera.parent = self.camera_pivot
		camera.position = (0, 0, 0)
		camera.rotation = (0, 0, 0)
		camera.fov = 90
		mouse.locked = True
		self.mouse_sensitivity = Vec2(40, 40)

		self.gravity = 1
		self.grounded = False
		self.jump_height = 2
		self.jump_up_duration = .5
		self.fall_after = .35  # will interrupt jump up
		self.jumping = False
		self.air_time = 0

		for key, value in kwargs.items():
			setattr(self, key, value)

		# make sure we don't fall through the ground if we start inside it
		if self.gravity:
			ray = ursina.raycast(self.world_position + (0, self.height, 0), self.down, ignore=(self,))
			if ray.hit:
				self.y = ray.world_point.y

	def update(self):

		self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity[1]

		self.camera_pivot.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity[0]
		self.camera_pivot.rotation_x = clamp(self.camera_pivot.rotation_x, -90, 90)

		self.direction = Vec3(
			self.forward * (held_keys['w'] - held_keys['s'])
			+ self.right * (held_keys['d'] - held_keys['a'])
		).normalized()

		feet_ray = ursina.raycast(self.position + Vec3(0, 0.5, 0), self.direction, ignore=(self,), distance=.5,
		                          debug=False)
		head_ray = ursina.raycast(self.position + Vec3(0, self.height - .1, 0), self.direction, ignore=(self,),
		                          distance=.5, debug=False)
		if not feet_ray.hit and not head_ray.hit:
			self.position += self.direction * self.speed * time.dt

		if self.gravity:
			# gravity
			ray = ursina.raycast(self.world_position + (0, self.height, 0), self.down, ignore=(self,))
			# ray = boxcast(self.world_position+(0,2,0), self.down, ignore=(self,))

			if ray.distance <= self.height + .1:
				if not self.grounded:
					self.land()
				self.grounded = True
				# make sure it's not a wall and that the point is not too far up
				if ray.world_normal.y > .7 and ray.world_point.y - self.world_y < .5:  # walk up slope
					self.y = ray.world_point[1]
				return
			else:
				self.grounded = False

			# if not on ground and not on way up in jump, fall
			self.y -= min(self.air_time, ray.distance - .05) * time.dt * 100
			self.air_time += time.dt * .25 * self.gravity

	def input(self, key):
		if key == 'space':
			self.jump()
		if key == 'left mouse down':
			print("prepare")
			shoot()
		if key == 'escape':
			mouse.locked = False
			self.cursor.enabled = False

	def start_fall(self):
		self.y_animator.pause()
		self.jumping = False

	def jump(self):
		if not self.grounded:
			return

		self.grounded = False
		self.animate_y(self.y + self.jump_height, self.jump_up_duration, resolution=int(1 // time.dt),
		               curve=curve.out_expo)
		invoke(self.start_fall, delay=self.fall_after)

	def land(self):
		# print('land')
		self.air_time = 0
		self.grounded = True

	def on_enable(self):
		mouse.locked = True
		self.cursor.enabled = True

	def on_disable(self):
		mouse.locked = False
		self.cursor.enabled = False

class Enemy(Entity):
	def __init__(self, **kwargs):
		super().__init__(parent=shootables_parent, model='cube', texture='zombie', scale=2.5, origin_y=-.5,
		                 collider='box', **kwargs)
		self.health_bar = Entity(parent=self, y=1.2, model='cube', color=color.red, world_scale=(1.5, .1, .1))
		self.max_hp = 100
		self.hp = self.max_hp

	def update(self):
		dist = distance_xz(player.position, self.position)
		if dist > 40:
			return

		self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)

		self.look_at_2d(player.position, 'y')
		hit_info = ursina.raycast(self.world_position + Vec3(0, 1, 0), self.forward, 30, ignore=(self,))
		if hit_info.entity == player:
			if dist > 2:
				shootEnemy()
				self.position += self.forward * time.dt * 5

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


# Enemy()
enemy1 = Enemy()

EnemyGun.parent = enemy1
if __name__ == '__main__':
	# window.vsync = False
	# Sky(color=color.gray)
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
	# hill = Entity(model='sphere', position=(20,-10,10), scale=(25,25,25), collider='sphere', color=color.green)
	# hill = Entity(model='sphere', position=(20,-0,10), scale=(25,25,25), collider='mesh', color=color.green)
	# from ursina.shaders import basic_lighting_shader
	# for e in scene.entities:
	#     e.shader = basic_lighting_shader

	# player.add_script(NoclipMode())
	app.run()
