# Physics object
from Vector import Vector2D as Vector

class Physics(object):
    def __init__(self):
        self.position = Vector(0, 0)
        self.velocity = Vector(0, 0)
        self.acceleration = Vector(0, 0)
        self.mass = 0.0

    def update(self):
        self.position = self.position.add(self.velocity)
        self.velocity = self.velocity.add(self.acceleration)
        self.acceleration.mul(0)

    def apply_force(self, force):
        self.acceleration = self.acceleration.add(force)