import pygame as pg
import sys
import ctypes
import math
import random
import time

class Branch:
    def __init__(self, surf, start, length, width):
        self.parent = None
        self.angle = -math.pi / 2
        self.surface = surf
        self.start = [int(start[0]), int(start[1])]
        self.length = length
        self.calc_end(length)
        self.width = width
        self.color = (255, 255, 255)
        self.has_grown = False

    def calc_end(self, length):
        x = self.start[0]
        y = self.start[1]
        x += int(length * math.cos(self.angle))
        y += int(length * math.sin(self.angle))
        self.end = [x, y]

    def re_init_begin(self):
        if self.parent:
            self.start = self.parent.end

    def grow(self, angle):
        self.has_grown = True
        w = self.width
        if w > 1:
            w -= 1

        left_branch = Branch(self.surface, self.end, self.length*0.75, w)
        right_branch = Branch(self.surface, self.end, self.length * 0.75, w)

        left_branch.parent = self
        left_branch.angle = self.angle - angle
        right_branch.angle = self.angle + angle

        right_branch.parent = self
        left_branch.calc_end(left_branch.length)
        right_branch.calc_end(right_branch.length)

        return left_branch, right_branch

    def draw(self):
        if self.length > 20:
            pg.draw.line(self.surface, self.color, self.start, self.end, self.width)
        else:
            pg.draw.line(self.surface, (0, 255, 0), self.start, self.end, self.width)
            pg.draw.circle(self.surface, (0, 255, 0), self.start, 5, 0)
            pg.draw.circle(self.surface, (0, 255, 0), self.end, 2, 0)


    def __str__(self):
        return 'start:{} end:{} angle:{}'.format(self.start, self.end, self.angle)

    def jiggle(self, variance):
        random.seed(time.clock())
        self.end = [int(self.end[0] + random.randrange(-variance, variance+1)),
                    int(self.end[1] + random.randrange(-variance, variance+1))]


if 'win' in sys.platform:
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

disp_bg_color = (0, 0, 0)
disp_w = 800
disp_h = 600

canvas = pg.display.set_mode((disp_w, disp_h))
canvas.fill(disp_bg_color)


root = Branch(canvas, [disp_w/2, disp_h], int(disp_h*0.25), 10)
branches = [root]
# execution loop
while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit(1)
        if event.type == pg.MOUSEBUTTONDOWN:
            new_branches = []
            # for i, branch in enumerate(branches):
            #     print('Branch[{}]: {}'.format(i,branch))
            for branch in branches:
                if not branch.has_grown:
                    new_branches += list(branch.grow(math.pi / 5))
            branches += new_branches
    canvas.fill(disp_bg_color)
    for branch in branches:
        # branch.jiggle(1)
        # branch.re_init_begin()
        branch.draw()
    pg.display.update()
