import pygame as pg
import sys
import ctypes
import random
import math
import threading
from Vector import Vector2D

random.seed()


class DNA(object):
    def __init__(self, lifespan=None, genes=None):
        if not lifespan:
            self.lifespan = 400
        else:
            self.lifespan = lifespan
        if genes:
            self.genes = genes
        else:
            self.genes = []
            force = Vector2D.zero_vector()
            for _ in range(self.lifespan):

                g_force = force.random_vector()
                g_force.set_magnitude(0.1)
                self.genes.append(g_force)

    def crossover(self, partner):
        newDna = []
        pivot = random.randrange(0, len(self.genes))
        for i, gene in  enumerate(self.genes):
            if i > pivot:
                newDna.append(gene)
            else:
                newDna.append(partner.genes[i])
        return DNA(self.lifespan, newDna)

    def mutation(self):
        if random.random() > 0.75:
            for gene in self.genes:
                gene = gene.random_vector()
                gene.set_magnitude(0.1)


    def zip_crossover(self,partner):
        newDna = []
        for i,gene in enumerate(self.genes):
            if i % 2 == 0:
                newDna.append(gene)
            else:
                newDna.append(partner.genes[i])
        return DNA(self.lifespan, newDna)

class Rocket(object):
    def __init__(self, surface, target, dna=None, start=None ):
        self.surface = surface
        self.target = target
        x = surface.get_width()
        y = surface.get_height()
        if not start:
            self.start = Vector2D(x/2, y-100)
        else:
            self.start = start
        self.pos = self.start.add(Vector2D(0, -20))
        self.velocity = Vector2D.zero_vector()
        gravity = Vector2D(0, 9.807)
        zero = Vector2D.zero_vector()
        self.acceleration = zero
        if dna:
            self.dna = dna
        else:
            self.dna = DNA()
        self.done = False
        self.detonated = False
        self.crashed = False
        self.step = 0
        self.fitness = 0
        self.distances = []
        self.obstacle = pg.Rect((x*0.30, y*0.5), (600,20))

    def apply_force(self, force):

        self.acceleration = self.acceleration.add(force)

    def update(self):
        gravity = Vector2D(0, 9.807)
        zero = Vector2D.zero_vector()

        # if self.pos.x > self.surface.get_width() or self.pos.x < 0:
        #     self.crashed = True
        #
        #
        # if self.pos.y > self.surface.get_height() or self.pos.y < 0:
        #     self.crashed = True

        if self.obstacle.collidepoint(*self.pos()):
            self.crashed = True

        if self.pos.distance(self.target) < 20:
            self.done = True
            self.pos = Vector2D(*self.target())

        if not self.done:
            self.distances.append(self.pos.distance(self.target))
            self.apply_force(gravity.div(200))
            self.apply_force(self.dna.genes[self.step])
            self.velocity = self.velocity.add(self.acceleration)
            self.pos = self.pos.add(self.velocity)
            self.acceleration = zero
            self.step += 1
        else:
           pass

    def calculate_fitness(self, target):
        d = self.pos.distance(target)
        sum = 0
        for dist in self.distances:
            sum += dist
        try:
            avg = sum / len(self.distances)
        except ZeroDivisionError:
            avg = 0
        try:
            self.fitness = 1 / d
        except ZeroDivisionError:
            self.fitness = 1

        # if self.done:
        #     self.fitness += .01
        if self.crashed:
            avg = 99999999
        self.fitness *= 1/avg



    def draw(self):
        if self.done or self.crashed:
            if not self.detonated:
                self.detonated = True
                # threading.Thread(self.detonate()).start()
        else:
            head = self.pos.add(self.velocity.mul(2))
            tail = self.pos.sub(self.velocity.mul(5))

            color = (255, 255, 255, 150)

            rocket = MyRect(self.surface, self.pos, tail, color, -self.velocity.getTheta() + math.pi/2)
            rocket.draw()
            pg.draw.circle(self.surface, color, head.floor()(), 8, 0)



    def detonate(self):
        flame_radius = 1
        grn_blu = 0
        for i in range(255, 0, -5):
            red = i
            green = self._rectify_color_param(104 - grn_blu)
            blue = self._rectify_color_param(3 - grn_blu)
            grn_blu += 4
            flame_radius += 1
            pg.draw.circle(self.surface, (red, green, blue), self.pos.floor()(), flame_radius, 1)
        pg.display.flip()
        self.surface.fill((255, 255, 255))
        pg.display.flip()
        self.surface.fill((0, 0, 0))
        pg.display.flip()
    @staticmethod
    def _rectify_color_param(param):
        if param > 255:
            param = 255
        elif param < 0:
            param = 0
        return param
class MyRect(object):
    def __init__(self, parent, top, bottom, color, angle):
        self.top = top
        self.bottom = bottom
        self.color = color
        self.theta = angle
        self.parent = parent
    def draw(self):
        l = 30
        w = 2
        hyp = math.sqrt(w**2 + l**2)
        beta = math.acos(w / hyp) - self.theta
        top_left_x = self.top.x - hyp * math.cos(beta)
        top_left_y = self.top.y - hyp * math.sin(beta)
        bottom_left_x = top_left_x + math.sin(self.theta)*l*2
        bottom_left_y = top_left_y + math.cos(self.theta)*l*2
        top_right_x = top_left_x + math.cos(self.theta)*w*2
        top_right_y = top_left_y - math.sin(self.theta)*w*2
        bottom_right_x = top_right_x + math.sin(self.theta)*l*2
        bottom_right_y = top_right_y + math.cos(self.theta)*l*2
        pg.draw.line(self.parent,self.color,
                     [top_left_x, top_left_y],
                     [top_right_x,top_right_y], 3)
        pg.draw.line(self.parent, self.color,
                     [top_right_x, top_right_y],
                     [bottom_right_x, bottom_right_y], 3)
        pg.draw.line(self.parent, self.color,
                     [bottom_right_x, bottom_right_y],
                     [bottom_left_x, bottom_left_y], 3)
        pg.draw.line(self.parent, self.color,
                     [bottom_left_x,bottom_left_y],
                     [top_left_x, top_left_y], 3)


class Population(object):
    def __init__(self, surface, size, target):
        self.surface = surface
        self.rockets = []
        self.size = size
        self.target = target
        for _ in range(self.size):
            self.rockets.append(Rocket(self.surface, target))
        self.mating_pool = []

    def run(self):
        # print(self.rockets[0].step)
        for rocket in self.rockets:
            rocket.update()
            rocket.draw()

    def evaluate(self):
        maxfit = 0
        self.mating_pool.clear()
        for rocket in self.rockets:
            rocket.calculate_fitness(target)
            if rocket.fitness > maxfit:
                maxfit = rocket.fitness
        for rocket in self.rockets:
            rocket.fitness /= maxfit  # normalize fitness
        for rocket in self.rockets:
            n = rocket.fitness * 100
            for i in range(int(n)):
                self.mating_pool.append(rocket)

    def selection(self):
        newRockets = []
        for rocket in self.rockets:
            parentA = random.choice(self.mating_pool).dna
            parentB = random.choice(self.mating_pool).dna
            child = parentA.crossover(parentB)
            child.mutation()
            if random.random() > 0.99:
                child = DNA()
            newRockets.append(Rocket(self.surface, target, child))
        self.rockets = newRockets



if __name__ == '__main__':


    if 'win' in sys.platform:
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass

    disp_bg_color = (0, 0, 0)
    disp_w = 1500
    disp_h = 800

    canvas = pg.display.set_mode((disp_w, disp_h))
    canvas.fill(disp_bg_color)
    target = Vector2D(disp_w * 0.5, disp_h * 0.25)
    population = Population(canvas, 500, target)


    while  True:
        # pg.time.wait(100)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit(1)
            if event.type == pg.MOUSEBUTTONDOWN:
                pass
                # canvas.fill(disp_bg_color)
                #
                # population.run()
                # pg.draw.circle(canvas, (255, 255, 255), target.floor()(), 20, 0)
                # # pg.draw.line(canvas, (0, 0, 200, 100), target(), pos(), 1)
                # each_done = [rocket.step == rocket.dna.lifespan or rocket.done for rocket in population.rockets]
                # if all(each_done):
                #     population.evaluate()
                #     population.selection()
            if event.type == pg.MOUSEMOTION:
                # pos = pg.mouse.get_pos()
                # pos = Vector2D(*pos)
                # print('({},{}) , distance to target: {}'.format(*pos(), pos.distance(target)))
                pass
            if event.type == pg.KEYDOWN:
                if pg.key.get_pressed()[pg.K_RETURN]:
                    pass
                elif pg.key.get_pressed()[pg.K_SPACE]:
                    pass
                elif pg.key.get_pressed()[pg.K_ESCAPE]:
                    pass

        canvas.fill(disp_bg_color)

        population.run()
        pg.draw.circle(canvas,(255,255,255), target.floor()(), 20, 0)
        pg.draw.rect(canvas, (255,255,255), population.rockets[0].obstacle, 0)
        # pg.draw.line(canvas, (0, 0, 200, 100), target(), pos(), 1)
        each_done = [rocket.step == rocket.dna.lifespan or rocket.done for rocket in population.rockets]
        if all(each_done):
            population.evaluate()
            population.selection()



        pg.display.flip()
        pg.time.delay(0)

