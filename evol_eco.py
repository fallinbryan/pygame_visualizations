import pygame as pg
import sys
import ctypes
import random
import math
import threading
from Vector import Vector2D
from Physics import Physics

random.seed()


class Target:
    def __init__(self):
        self.position = Vector2D(0, 0)

    def move(self, arg):
        self.position = Vector2D(arg[0], arg[1])

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
            self.genes = {}
            self.genes['max_size'] = random.randrange(5, 30)
            self.genes['growth_rate'] = random.uniform(0.001, 0.9)
            self.genes['max_speed'] = random.randrange(5, 100)
            self.genes['lifespan'] = random.randrange(100, 1000)
            self.genes['breeding_age'] = random.randrange(50, self.genes['lifespan'])
            self.genes['breeding_cost'] = random.randrange(100, 500)
            self.genes['feeding_behaviour'] = random.choice(['near','far'])

    def crossover(self, partner):
        new_genes = {}
        for name in self.genes:
            new_genes[name] = random.choice([self.genes[name], partner.genes[name]])

        return DNA(genes=new_genes)

    def mutation(self):
        for name in self.genes:
            if name != 'feeding_behaviour':
                if random.random() > .99:
                    self.genes[name] += random.uniform(-0.01, 0.01)
        if random.random() > .9999:
            self.genes['feeding_behaviour'] = random.choice(['near', 'far'])


class Creature(Physics):
    color_map = {'wandering': [242, 145, 200],
                 'seeking food': [91, 200, 67],
                 'seeking mate': [255, 178, 178]}
    def __init__(self, surface, pos, dna):
        super().__init__()
        self.surface = surface
        self.position = pos
        self.dna = dna
        self.energy = 500.0
        self.age = 1.0
        self.alive = True
        self.sex = random.choice([True, False])
        self.max_size = dna.genes['max_size']
        self.growth_rate = dna.genes['growth_rate']
        self.max_speed = dna.genes['max_speed']
        self.prev_acc = Vector2D(0, 0)
        self.state = "wandering"
        self.target = None
        self.targetReached = True
        self.lifespan = dna.genes['lifespan']
        self.breeding_age = dna.genes['breeding_age']
        self.breeding_cost = dna.genes['breeding_cost']
        self.feeding_behaviour = dna.genes['feeding_behaviour']

    def apply_force(self, force):
        super().apply_force(force)
        self.prev_acc = force

    def seek(self):
        target = self.target
        desired = target.position.sub(self.position)
        desired = desired.normalize()
        desired = desired.mul(self.position.distance(target.position))
        force = desired.sub(self.velocity)
        force = force.mul(0.5)
        self.apply_force(force)
        mag = self.position.distance(target.position)
        if mag < 10:
            self.targetReached = True
            mag = 0
        self.velocity.set_magnitude(mag * 0.5)
        if self.velocity.magnitude() > self.max_speed:
            self.velocity.set_magnitude(self.max_speed)

        super().update()


    def test_seek(self, target):
        self.target = target
        self.seek()


    def seek_furthest(self, targets):
        x_max = self.surface.get_width()
        y_max = self.surface.get_height()
        max_dist = 0
        target = targets[0]
        for _target in targets:
            if self.position.distance(_target.position) > max_dist:
                if _target is not self:
                    try:
                        if _target.sex == self.sex ^ True and _target.state == "seeking mate":
                            max_dist = self.position.distance(_target.position)
                            target = _target

                    except:
                        max_dist = self.position.distance(_target.position)
                        target = _target
        self.target = target
        self.seek()
        found = None

        if self.position.distance(self.target.position) < 20 and target is not self:
            found = target

        return found
    def seek_nearest(self, targets):
        x_max = self.surface.get_width()
        y_max = self.surface.get_height()
        min_dist = 9999999
        target = targets[0]
        for _target in targets:
            if self.position.distance(_target.position) < min_dist:
                if _target is not self:
                    try:
                        if _target.sex == self.sex ^ True and _target.state == "seeking mate":
                            min_dist = self.position.distance(_target.position)
                            target = _target

                    except:
                        min_dist = self.position.distance(_target.position)
                        target = _target
        self.target = target
        self.seek()
        found = None

        if self.position.distance(self.target.position) < 20 and target is not self:
            found = target

        return found

    def eat_food(self, food):
        self.energy += food.energy
        food.eaten = True

    def breed(self, mate):
        new_dna = self.dna.crossover(mate)
        return Creature(self.surface, self.position, new_dna)

    def wander(self):

        x_max = self.surface.get_width()
        y_max = self.surface.get_height()
        target = Target()
        target.move((random.randrange(0, x_max), random.randrange(0, y_max)))
        if self.targetReached:
            self.target = target
            self.targetReached = False
        self.seek()

    def C_update(self, environment):
        return_objects = []
        if self.energy == 0:
            self.alive = False
        if self.age > self.lifespan:
            self.alive = False

        if self.alive:
            self.energy -= math.exp(self.growth_rate) / (math.exp(self.growth_rate) + 1) * 2.5
            self.age += 1

            if self.energy < 400 and len(environment['food']) > 0:
                self.state = "seeking food"
                if self.feeding_behaviour == 'near':
                    found = self.seek_nearest(environment['food'])
                elif self.feeding_behaviour == 'far':
                    found = self.seek_furthest(environment['food'])
                if found:
                    self.eat_food(found)

            elif self.age > self.breeding_age and self.energy > self.breeding_cost:
                self.state = "seeking mate"
                found = self.seek_nearest(environment['creatures'])
                if found:
                    if found.state == "seeking mate":
                        return_objects.append(self.breed(found.dna))
                        return_objects.append(self.breed(found.dna))

                        self.energy -= self.breeding_cost
                else:
                    pass

            else:
                self.state = 'wandering'
                self.wander()


        return return_objects

    def draw(self):
        color = self.color_map[self.state]
        if self.sex:
            color[2] = 200
        else:
            color[2] = 50
        try:
            size = self.max_size * (math.exp(self.age*self.growth_rate) / (math.exp(self.age*self.growth_rate) + 1))
        except OverflowError:
            size = self.max_size * (math.exp(700) / (math.exp(700) + 1))
        pointlist = []
        pointlist.append((int(self.position.x + size*math.cos(self.velocity.getTheta())), int(self.position.y + size*math.sin(self.velocity.getTheta()))))
        pointlist.append((int(self.position.x - (size-5)*math.cos(self.velocity.getTheta())), int(self.position.y - (size-5)*math.sin(self.velocity.getTheta()))))
        pointlist.append((int(self.position.x - (size-5)*math.cos(self.velocity.getTheta())), int(self.position.y + (size-5)*math.sin(self.velocity.getTheta()))))
        pg.draw.polygon(self.surface, color, pointlist, 1)


class Food(object):
    def __init__(self, x, y, energy=None):
        self.position = Vector2D(x, y)
        if energy:
            self.energy = energy
        else:
            self.energy = 100
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

    environment = {"food": [],
                   "creatures": [Creature(canvas, Vector2D(random.randrange(0, WIDTH), random.randrange(0, HEIGHT)), DNA()) for _ in range(50)]}

    theta = 0
    food_field_radius = 400
    for _ in range(100):
        environment['food'].append(Food(disp_w/2 + food_field_radius * math.cos(theta), disp_h/2 + food_field_radius * math.sin(theta)))
        theta += .13


    class Target:
        def __init__(self):
            self.position = Vector2D(0,0)
        def move(self, arg):
            self.position = Vector2D(arg[0], arg[1])
    target = Target()
    creature = Creature(canvas, Vector2D(WIDTH/2, HEIGHT/2), DNA())
    compass = Compass(canvas, Vector2D(WIDTH*0.1, HEIGHT*0.1), 'Creature Heading')
    isGrabbed = False
    frame_rate = 100
    chase_mouse = False
    while True:
        food_field_radius = random.choice([50,100,150,200,225,250,300])
        # if food_field_radius < 1:
        #     food_field_radius = 400
        # theta += .13
        # if theta > 500:
        #     theta = 0
        theta = random.uniform(0, 2*math.pi)
        # pg.time.wait(100)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit(1)
            if event.type == pg.MOUSEBUTTONDOWN:
                chase_mouse = True

            if event.type == pg.MOUSEBUTTONUP:
                chase_mouse = False

            if event.type == pg.MOUSEMOTION:
                if isGrabbed:
                   pass

            if event.type == pg.KEYDOWN:
                if pg.key.get_pressed()[pg.K_RETURN]:
                    pass
                elif pg.key.get_pressed()[pg.K_SPACE]:
                    pass
                elif pg.key.get_pressed()[pg.K_UP]:
                    frame_rate -= 10
                elif pg.key.get_pressed()[pg.K_DOWN]:
                    frame_rate += 10
                elif pg.key.get_pressed()[pg.K_ESCAPE]:
                    pg.quit()
                    sys.exit(1)

        canvas.fill(disp_bg_color)
        if environment["food"]:
            for count, food in enumerate(environment["food"]):
                if count > 50:
                    food.eaten = True
                if food.eaten:
                    environment["food"].pop(environment["food"].index(food))
                if not food.eaten:
                    pg.draw.circle(canvas, (50, 255, 50), food.position.floor()(), 2, 0)

        if not chase_mouse:
            if len(environment['creatures']) == 0:
                environment['creatures'] += [Creature(canvas, Vector2D(random.randrange(0, WIDTH), random.randrange(0, HEIGHT)), DNA()) for _ in
                 range(10)]
            for count, creature in enumerate(environment["creatures"]):
                if count > 50:
                    creature.alive = False
                if creature.alive:
                    new_creatures = creature.C_update(environment)
                    creature.draw()
                    if new_creatures:
                            environment["creatures"] += new_creatures

                else:
                    # environment['food'].append(Food(creature.position.x, creature.position.y, 500))
                    environment['food'].append(Food(disp_w/2 + food_field_radius * math.cos(theta), disp_h/2 + food_field_radius * math.sin(theta)))
                    environment['creatures'].pop(environment['creatures'].index(creature))
        else:
            target.move(pg.mouse.get_pos())
            pg.draw.circle(canvas, (255, 80, 80), (target.position.x, target.position.y), 10, 0)
            for creature in environment['creatures']:
                creature.test_seek(target)
                creature.update()
                creature.draw()
        # compass.show(creature.velocity.getTheta())
        # heading_text = font.render('Heading: {:.02f}  Velocity: {:.02f}'.format(creature.velocity.getTheta() * 180 / math.pi,
        #                                                       creature.velocity.magnitude()), False, (255, 255, 255))
        # distance_text = font.render('Distance to target {:.02f}'.format(creature.position.distance(target.position)), False, (255, 255, 255))
        # accell_text = font.render('Applied acceleration: ({:.02f},{:.02f})'.format(creature.prev_acc.x, creature.prev_acc.y), False, (255, 255, 255))
        #
        # canvas.blit(heading_text, (WIDTH - 500, HEIGHT - 200))
        # canvas.blit(distance_text, (WIDTH - 500, HEIGHT - 150))
        # canvas.blit(accell_text, (WIDTH - 500, HEIGHT - 100))
        pg.display.flip()

        pg.time.delay(frame_rate)

