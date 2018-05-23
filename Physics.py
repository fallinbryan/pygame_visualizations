# Physics object
import Vector

class Physics(object):
    def __init__(self):
        self.position = Vector.Vector(0, 0, 0)
        self.velocity = Vector.Vector(0, 0, 0)
        self.acceleration = Vector.Vector(0, 0, 0)
        self.mass = 0.0

    def update(self):
        self.velocity.add(self.acceleration)
        self.position.add(self.velocity)

    def apply_force(self, force):
        self.acceleration.add(force)