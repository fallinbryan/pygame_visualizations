import pygame as pg
import sys
import ctypes
import random
import math
import threading
from Vector import Vector2D
from Physics import Physics

random.seed()

class Compass(object):
    def __init__(self, surface, pos, title=None):
        self.surface = surface
        self.heading = 0
        self.pos = pos
        self.radius = 48
        if title:
            self.title = title
        else:
            self.title = 'Compass'
    def show(self, heading):
        font = pg.font.SysFont('Comic Sans MS', 12)
        self.heading = heading
        pg.draw.circle(self.surface, (255,255,255), self.pos.floor()(), self.radius + 5, 1)
        x = self.pos.x + self.radius * math.cos(heading)
        y = self.pos.y + self.radius * math.sin(heading)
        end = Vector2D(x, y)
        pg.draw.line(self.surface, (255, 255, 255), self.pos(), end(), 1)
        title_text = font.render(self.title, True, (255,255,255))


        self.surface.blit(title_text, (self.pos.x - self.radius, self.pos.y + self.radius + 10))



class DNA(object):
    def __init__(self, lifespan=None, genes=None):
        if genes:
            self.genes = genes
        else:
            self.genes = [8]

    def crossover(self, partner):
        newDna = []
        pivot = random.randrange(0, len(self.genes))
        for i, gene in  enumerate(self.genes):
            if i > pivot:
                newDna.append(gene)
            else:
                newDna.append(partner.genes[i])
        return DNA(genes=newDna)

    def mutation(self):
        pass


class Creature(Physics):
    color_map = {'wandering': (242, 145, 247),
                 'seeking food': (91, 242, 67),
                 'seeking mate': (255, 178, 178)}
    def __init__(self, surface, pos, dna):
        super().__init__()
        self.surface = surface
        self.position = pos
        self.dna = dna
        self.energy = 500.0
        self.age = 1.0
        self.alive = True
        self.sex = random.choice(['male', 'female'])
        self.max_speed = 20
        self.prev_acc = Vector2D(0, 0)
        self.state = "wandering"

    def apply_force(self, force):
        super().apply_force(force)
        self.prev_acc = force

    def seek(self, target):
        desired = target.position.sub(self.position)
        desired = desired.normalize()
        desired = desired.mul(self.position.distance(target.position))
        force = desired.sub(self.velocity)

        return force

    def test_seek(self, target):
        force = self.seek(target)
        # force.set_magnitude(1)
        self.apply_force(force)
        mag = self.position.distance(target.position)*0.5
        self.velocity.set_magnitude(mag)

        if self.velocity.magnitude() > self.max_speed:
            self.velocity.set_magnitude(self.max_speed)

    def seek_nearest(self, targets):
        min_dist = 9999999
        target = targets[0]
        for _target in targets:
            if self.position.distance(target.position) < min_dist:
                if _target is not self:
                    min_dist = self.position.distance(target.position)
                    target = _target
        force = self.seek(target)
        found = None
        if self.position.distance(target.position) < 50:
            found = target

        return force, found

    def eat_food(self, food):
        self.energy += food.energy
        food.eaten = True

    def breed(self, mate):
        new_dna = self.dna.crossover(mate)
        return Creature(self.surface, self.position, new_dna)

    def wander(self):

        x_max = self.surface.get_width()
        y_max = self.surface.get_height()
        class target:
            position = Vector2D(x_max/2, y_max/2)
        force = self.velocity.random_vector(math.pi)
        force.set_magnitude(0.01)
        if int(self.position.x) in range(0, 100):
            force = self.seek(target)
        elif int(self.position.x) in range (x_max - 100, x_max):
            force = self.seek(target)
        if int(self.position.y) in range(0, 500):
            force = self.seek(target)
        elif int(self.position.y) in range(y_max - 100, y_max):
            force = self.seek(target)

        return force



    def C_update(self, environment):
        if self.energy == 0:
            self.alive = False
        if self.age > 5000.0:
            self.alive = False

        if self.alive:
            self.energy -= 2
            self.age += 0.5

            if self.energy < 100:
                self.state = "seeking food"
                force, found = self.seek_nearest(environment['food'])
                if found:
                    self.eat_food(found)

            elif self.age > 500 and self.energy > 100:
                self.state = "seeking mate"
                force, found = self.seek_nearest(environment['creatures'])
                if found:
                    self.breed(found.dna)
                    self.alive = False
            else:
                self.state = 'wandering'
                force = self.wander()


            self.apply_force(force)
            super().update()
            if self.velocity.magnitude() > self.max_speed:
                self.velocity.set_magnitude(self.max_speed)

    def draw(self):
        color = self.color_map[self.state]
        # if self.sex == "male":
        #     color = (150, 150, 255)
        # else:
        #     color = (255, 150, 150)
        pointlist = []
        pointlist.append((int(self.position.x + 25*math.cos(self.velocity.getTheta())), int(self.position.y + 25*math.sin(self.velocity.getTheta()))))
        pointlist.append((int(self.position.x - 15*math.cos(self.velocity.getTheta())), int(self.position.y - 15*math.sin(self.velocity.getTheta()))))
        pointlist.append((int(self.position.x - 15*math.cos(self.velocity.getTheta())), int(self.position.y + 15*math.sin(self.velocity.getTheta()))))
        pg.draw.polygon(self.surface, color, pointlist, 1)

class Food(object):
    def __init__(self, x, y):
        self.position = Vector2D(x, y)
        self.energy = 25
        self.eaten = False

if __name__ == '__main__':
    if 'win' in sys.platform:
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass

    pg.font.init()
    font = pg.font.SysFont('Comic Sans MS', 12)
    disp_bg_color = (0, 0, 0)
    disp_w = 1500
    disp_h = 800

    canvas = pg.display.set_mode((disp_w, disp_h))
    canvas.fill(disp_bg_color)
    WIDTH = canvas.get_width()
    HEIGHT = canvas.get_height()

    # environment = {"food": [Food(random.randrange(0, WIDTH), random.randrange(0, HEIGHT)) for _ in range(100)],
    #                "creatures": [Creature(canvas, Vector2D(random.randrange(0, WIDTH), random.randrange(0, HEIGHT)), DNA()) for _ in range(10)]}

    # environment = {"food": [Food(WIDTH/2, HEIGHT/2) for _ in range(1)],
    #                "creatures": [
    #                    Creature(canvas, Vector2D(random.randrange(0, WIDTH), random.randrange(0, HEIGHT)), DNA()) for _
    #                    in range(10)]}

    class Target:
        def __init__(self):
            self.position = Vector2D(0,0)
        def move(self, arg):
            self.position = Vector2D(arg[0],arg[1])
    target = Target()
    creature = Creature(canvas, Vector2D(WIDTH/2, HEIGHT/2), DNA())
    compass = Compass(canvas, Vector2D(WIDTH*0.1, HEIGHT*0.1), 'Creature Heading')
    isGrabbed = False
    while  True:
        # pg.time.wait(100)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit(1)
            if event.type == pg.MOUSEBUTTONDOWN:
                isGrabbed = True

            if event.type == pg.MOUSEBUTTONUP:
                isGrabbed = False

            if event.type == pg.MOUSEMOTION:
                if isGrabbed:
                   pass

            if event.type == pg.KEYDOWN:
                if pg.key.get_pressed()[pg.K_RETURN]:
                    pass
                elif pg.key.get_pressed()[pg.K_SPACE]:
                    pass
                elif pg.key.get_pressed()[pg.K_ESCAPE]:
                    pg.quit()
                    sys.exit(1)

        canvas.fill(disp_bg_color)
        # if environment["food"]:
        #     for food in environment["food"]:
        #         if food.eaten:
        #             environment["food"].pop(environment["food"].index(food))
        #         if not food.eaten:
        #             pg.draw.circle(canvas, (50, 255, 50), food.position.floor()(), 2, 0)
        #
        #     for creature in environment["creatures"]:
        #         if creature.alive:
        #             creature.C_update(environment)
        #             creature.draw();

        target.move(pg.mouse.get_pos())
        pg.draw.circle(canvas, (255, 255, 255), (target.position.x, target.position.y), 20, 1)
        creature.test_seek(target)
        creature.update()
        creature.draw()
        compass.show(creature.velocity.getTheta())
        heading_text = font.render('Heading: {:.02f}  Velocity: {:.02f}'.format(creature.velocity.getTheta() * 180 / math.pi,
                                                              creature.velocity.magnitude()), False, (255, 255, 255))
        distance_text = font.render('Distance to target {:.02f}'.format(creature.position.distance(target.position)), False, (255, 255, 255))
        accell_text = font.render('Applied acceleration: ({:.02f},{:.02f})'.format(creature.prev_acc.x, creature.prev_acc.y), False, (255, 255, 255))

        canvas.blit(heading_text, (WIDTH - 500, HEIGHT - 200))
        canvas.blit(distance_text, (WIDTH - 500, HEIGHT - 150))
        canvas.blit(accell_text, (WIDTH - 500, HEIGHT - 100))
        pg.display.flip()

        pg.time.delay(100)

