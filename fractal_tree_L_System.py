# Lindenmayer System,  search wikipeda
# text based graphic generation
# has an alphabet, axiom, set of rules
# recursively generates sentences using string replacement

import pygame as pg
import sys
import ctypes
import math
import random
import time


class Tree:
    def __init__(self, surface, axiom, rules):
        self.surface = surface
        self.sentence = axiom
        self.rules = rules
        self.turtle = {'F': self.line,
                       '+': self.turn_r,
                       '-': self.turn_l,
                       '[': self.push,
                       ']': self.pop,
                       'B': self.bulb}

        self.pos = [int(surface.get_width()/2), int(surface.get_height())]
        self.len = 5
        self.rotation = math.pi/2
        self.stack = []

    def generate_sentence(self):
        new_sentence = ''
        for c in self.sentence:
            try:
                new_sentence += self.rules[c]
            except:
                new_sentence += c
        self.sentence = new_sentence

    def draw(self):
        for c in self.sentence:
            self.turtle[c]()

    def calculate_next_pos(self):
        x = self.pos[0] + int(self.len * math.cos(self.rotation))
        y = self.pos[1] - int(self.len * math.sin(self.rotation))
        return [x, y]

    def line(self):
        next_pos = self.calculate_next_pos()
        pg.draw.line(self.surface, (3, 121, 26), self.pos, next_pos, 2)
        pg.display.flip()
        self.pos = next_pos

    def turn_r(self):
        self.rotation += math.pi/6

    def turn_l(self):
        self.rotation -= math.pi/6
    def push(self):
        self.stack.append((self.pos, self.rotation))

    def pop(self):
        self.pos, self.rotation = self.stack.pop()

    def bulb(self):
        pg.draw.circle(self.surface, (242, 172, 232), self.pos, 4, 0)
        pg.draw.circle(self.surface, (255,248,131), self.pos, 2, 0)

    def __str__(self):
        return self.sentence


if 'win' in sys.platform:
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass


disp_bg_color = (138, 172, 181)
disp_w = 800
disp_h = 600

pg.init()
canvas = pg.display.set_mode((disp_w, disp_h))
canvas.fill(disp_bg_color)

alphabet = ['F', '+', '-', '[', ']']
axiom = 'F'
# FF+[+F-F-F]-[-F+F+F]'
rules = {'F': 'FF+[+F-F-F]-[-F+F+F]',
         }
tree = Tree(canvas, axiom, rules)

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit(1)
        if event.type == pg.MOUSEBUTTONDOWN:
            tree.generate_sentence()
            tree.push()
            tree.draw()
            tree.pop()
            print(len(tree.sentence))

    canvas.fill(disp_bg_color)
    # tree.push()
    # tree.draw()
    # tree.pop()
    # pg.display.flip()
