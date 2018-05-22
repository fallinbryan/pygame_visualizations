# Vector Maths
import math
import random
import time


class Vector(object):
    def __init__(self, *args):
        self.index = 0
        self.vect = list(args)

    def add(self, b):
        if type(b) is not Vector:
            raise ValueError("Argument must be a Vector object")
        if len(self.vect) != len(b):
            raise ValueError("Argument must be in {} Vector Space".format(len(self)))
        return Vector(*[a + b[i] for i, a in enumerate(self.vect)])

    def sub(self, b):
        if type(b) is not Vector:
            raise ValueError("Argument must be a Vector object")
        if len(self.vect) != len(b):
            raise ValueError("Argument must be in {} Vector Space".format(len(self)))
        return Vector(*[a - b[i] for i, a in enumerate(self.vect)])

    def mul(self, b):
        if type(b) is Vector:
            raise ValueError("Argument must be a scalar")
        return Vector(*[a * b for a in self.vect])

    def div(self, b):
        if type(b) is Vector:
            raise ValueError("Argument must be a scalar")
        if b == 0:
            raise ZeroDivisionError
        return Vector(*[a / b for a in self.vect])

    def dot(self, b):
        if type(b) is not Vector:
            raise ValueError("Argument must be a Vector object")
        if len(self.vect) != len(b):
            raise ValueError("Argument must be in {} Vector Space".format(len(self)))
        products = []
        for i, a in enumerate(self.vect):
            products.append(a * b.vect[i])
        return self._kahun_sum(products)

    @staticmethod
    def _kahun_sum(products):
        r_sum = 0.0
        c = 0.0
        for i in products:
            y = i - c
            t = r_sum + y
            c = (t - r_sum) - y
            r_sum = t
        return r_sum

    def normalize(self):
        if self.magnitude() == 0:
            return Vector(*[0 for _ in self.vect])
        return Vector(*[a / self.magnitude() for a in self.vect])

    def magnitude(self):
        squares = [a ** 2 for a in self.vect]
        return math.sqrt(self._kahun_sum(squares))

    def is_orthogonal_to(self, vect):
        if type(vect) is not Vector:
            raise ValueError("Argument must be a Vector object")
        if len(self.vect) != len(vect):
            raise ValueError("Argument must be in {} Vector Space".format(len(self)))
        return self.dot(vect) == 0

    def get_theta_between(self, vect):
        if type(vect) is not Vector:
            raise ValueError("Argument must be a Vector object")
        if len(self.vect) != len(vect):
            raise ValueError("Argument must be in {} Vector Space".format(len(self)))
        if self.magnitude() * vect.magnitude() == 0:
            return 0
        return math.acos(self.dot(vect) / (self.magnitude() * vect.magnitude()))

    def set_magnitude(self, scalar):
        if type(scalar) is Vector:
            raise ValueError("Argument must be a scalar")
        self.vect = self.normalize()
        self.vect = self.mul(scalar)

    def project_on_to(self, vect):
        if type(vect) is not Vector:
            raise ValueError("Argument must be a Vector object")
        if len(self.vect) != len(vect):
            raise ValueError("Argument must be in {} Vector Space".format(len(self)))
        norm_vect = vect.normalize()
        scalar_a = self.dot(norm_vect)
        return norm_vect.mul(scalar_a)

    def distance(self, vect):
        if type(vect) is not Vector:
            raise ValueError("Argument must be a Vector object")
        if len(self.vect) != len(vect):
            raise ValueError("Argument must be in {} Vector Space".format(len(self)))
        squares =[]
        for i, a in enumerate(self.vect):
                squares.append((vect[i]-a)**2)
        return math.sqrt(self._kahun_sum(squares))


    def floor(self):
        return Vector(*[int(a) for a in self.vect])

    def __eq__(self, other):
        if type(other) is not Vector:
            raise ValueError("Argument must be a Vector object")
        if len(self.vect) != len(other):
            raise ValueError("Argument must be in {} Vector Space".format(len(self)))
        rv = True
        for i, a in enumerate(self.vect):
            rv = rv and a == other[i]
        return rv

    def __getitem__(self, index):
        if index >= len(self.vect):
            raise IndexError
        return self.vect[index]

    def __setitem__(self, key, value):
        self.vect[key] = value

    def __call__(self):
        return self.vect

    def __len__(self):
        return len(self.vect)

    def __str__(self):
        return '{}'.format(self.vect)

    def __repr__(self):
        return 'Vector{}'.format(self.vect)

    def __hash__(self):
        return hash(tuple(self.vect))

    def __iter__(self):
        return self

    def __next__(self):
        temp = self.index
        self.index += 1
        if temp == len(self):
            self.index = 0
            raise StopIteration

        return self.vect[temp]


class Vector2D(Vector):
    def __init__(self, *args):
        super().__init__(*args)
        if len(args) > 2:
            raise ValueError("2 Dimensional Vector takes only two arguments")

        self.x = args[0]
        self.y = args[1]
        self.random_theta = random.uniform(0, 2*math.pi)

    def add(self, b):
        b = Vector(*b())
        return Vector2D(*super().add(b))

    def sub(self, b):
        b = Vector(*b())
        return Vector2D(*super().sub(b))

    def mul(self, b):
        return Vector2D(*super().mul(b))

    def div(self, b):
        return Vector2D(*super().div(b))

    def dot(self, b):
        b = Vector(*b())
        return super().dot(b)

    def normalize(self):
        return Vector2D(*super().normalize())

    def project_on_to(self, b):
        b = Vector(*b())
        return Vector2D(*super().project_on_to(b))

    def floor(self):
        return Vector2D(*super().floor())


    def distance(self, vect):
        b = Vector(*vect())
        return super().distance(b)

    def getTheta(self):
        theta = self.get_theta_between(Vector(1, 0))
        if self.x < 0 and self.y < 0:
            theta *= -1
        elif self.x > 0 and self.y < 0:
            theta *= -1
        elif self.x > 0 and self.y > 0:
            pass
        elif self.x <0 and self.y > 0:
            pass
        return theta

    @staticmethod
    def zero_vector():
        return Vector2D(0, 0)


    def random_vector(self):
        random.seed()
        pivot = self.random_theta

        theta = random.triangular(pivot - math.pi/8, pivot + math.pi/8, pivot)

        self.random_theta = theta

        return Vector2D(math.cos(theta), math.sin(theta))



    def __repr__(self):
        return 'Vector2D({},{})'.format(self.x, self.y)
