import pygame as pg
import sys
import ctypes
import math
import random
import time


MIN_DIST = 15
MAX_DIST = 150


def vect_add(a, b):
    if len(a) != len(b):
        raise ValueError('Vector A and B must have the same vector space')
    return_vect = []
    for i,v in enumerate(a):
        return_vect.append(v + b[i])

    return return_vect


def vect_sub(a, b):
    if len(a) != len(b):
        raise ValueError('Vector A and B must have the same vector space')
    return [v - b[i] for i, v in enumerate(a)]


def vect_div(vect, scalar):
    return [(i / scalar) for i in vect]

def vect_mul(vect, scalar):
    return [(i * scalar) for i in vect]

def vect_norm(x):
    mag = math.sqrt(x[0]**2 + x[1]**2)
    return [i/mag for i in x]


def nearest_branch(branches, leaf):
    return_seed = branches[0]
    init_dist = dist(leaf.end, [branches[0].x, branches[0].y])
    for seed in branches:
        next_dist = dist(leaf.end, [seed.x, seed.y])
        if  next_dist < init_dist:
            return_seed = seed
            init_dist = next_dist
    return return_seed


def dist(a, b):
    x = a[0] - b[0]
    y = a[1] - b[1]
    return math.sqrt(x**2 + y**2)

class Tree:
    def __init__(self, surface, number_of_leaves, branch_len):
        self.isDoneGrowing = False
        self.animation_complete = False
        self.surface = surface
        w = surface.get_width()
        h = surface.get_height()
        circle_center = [int(w/2), int(h/3)]
        cirle_radius = 400
        self.leaves = [Leaf(surface,
                            [random.randrange(circle_center[0] - cirle_radius,
                                              circle_center[0] + cirle_radius),
                            random.randrange(circle_center[1]-cirle_radius,
                                             circle_center[1]+cirle_radius)]) for _ in range(number_of_leaves)]

        new_leaves = []
        for leaf in self.leaves:
            if dist(circle_center, leaf.pos) <= cirle_radius:
                new_leaves.append(leaf)
        self.leaves = new_leaves


        self.branch_len = branch_len
        self.root = Branch(surface, None,
                           [int(self.surface.get_width()/2), int(self.surface.get_height())],
                           vect_mul([0, -1], self.branch_len), branch_len)
        self.branches = [self.root]
        self.buds = []
        self.init_grow()

    def draw(self):
        # [leaf.draw() for leaf in self.leaves]
        [bud.draw() for bud in self.buds]
        [branch.draw() for branch in self.branches]



    def init_grow(self):
        current = self.root
        found = False
        while not found:
            for leaf in self.leaves:
                d = dist(current.pos, leaf.pos)
                if d < MAX_DIST:
                    found = True
            if not found:
                branch = current.next()
                current = branch
                self.branches.append(branch)

    def set_nearest_branches(self):
        for leaf in self.leaves:
            nearestBranch = None
            record_distance = 99999
            for branch in self.branches:
                current_dist = dist(leaf.pos, branch.pos)
                if current_dist < MIN_DIST:
                    leaf.reached = True
                    bud = Leaf(self.surface, [int(branch.pos[0]), int(branch.pos[1])])
                    bud.set_color = bud.color['green']
                    bud.growing = True
                    bud.r = 5
                    bud.green = 255
                    self.buds.append(bud)
                    break
                elif current_dist > MAX_DIST:
                    pass
                elif nearestBranch is None or current_dist < record_distance:
                    leaf.influencing = True
                    nearestBranch = branch
                    record_distance = current_dist

            if nearestBranch is not None:
                pos = nearestBranch.pos[:]
                pos = [-pos[0], -pos[1]]
                newDir = vect_add(leaf.pos, pos)
                newDir = vect_norm(newDir)
                # newDir = vect_sub(newDir, [self.branch_len, self.branch_len])
                nearestBranch.direction = vect_add(newDir, nearestBranch.direction)
                nearestBranch.count += 1

    def remove_leaves(self):
        new_leaf_list = []
        for leaf in self.leaves:
            if not leaf.reached:
                new_leaf_list.append(leaf)
        self.leaves = new_leaf_list

    def add_new_branches(self):
        branches_growing = 0
        for branch in reversed(self.branches):
            if branch.count > 0:
                branches_growing += 1
                branch.direction = vect_div(branch.direction, branch.count)
                newBranch = branch.next()
                # newBranch.pos = vect_add(newBranch.pos, [self.branch_len, self.branch_len])
                self.branches.append(newBranch)
            branch.reset()
        if branches_growing < 1:
            self.isDoneGrowing = True

    def grow(self):
        if len(self.leaves) < 50:
            self.isDoneGrowing = True
        if not self.isDoneGrowing:
            for branch in self.branches:
                if branch.width < 50:
                    branch.width += 0.1
            for bud in self.buds:
                if bud.r < 20:
                    bud.r += 0.05
            self.set_nearest_branches()
            self.remove_leaves()
            self.add_new_branches()
        else:
            if not self.grow_buds():
                if not self.color_change_buds():
                    if not self.drop_buds():
                        self.animation_complete = True

    def color_change_buds(self):
        changeing_colors = False
        for bud in self.buds:
            if bud.red < 186:
                changeing_colors = True
                bud.red += 0.1
                if bud.green < 59:
                    bud.green += 0.1
                if bud.blue < 27:
                    bud.blue += 0.1
        return changeing_colors
    def grow_buds(self):
        growing = False
        for bud in self.buds:
            if bud.r < 20:
                bud.r += 0.01
                # bud.red += 0.1
                # bud.blue += 0.1
                if bud.green > 111:
                    bud.red = 8
                    bud.blue = 4
                    bud.green -= 0.25
                growing = True
        return growing

    def drop_buds(self):
        buds_dropping = False
        for bud in self.buds:
            if bud.pos[1] < self.surface.get_height():
                buds_dropping = True
                bud.pos[1] += random.randrange(0, 5)
                bud.pos[0] -= random.randrange(0, 5)
        return buds_dropping

class Leaf:
    def __init__(self, surface, pos):
        self.surface = surface
        self.vpos = pos
        self.pos = pos
        self.r = 5
        self.reached = False
        self.influencing = False
        self.growing = False
        self.color = {'red': (255, 0, 0),
                      'green': (0, 255, 0),
                      'blue': (0, 0, 255),
                      'white': (255, 255, 255)}

        self.set_color = self.color['white']
        self.red = 0
        self.green = 0
        self.blue = 0
    def draw(self):
        if self.influencing:
            self.set_color = self.color['green']
            self.r = 5
        elif self.growing:
            self.red = self.contstrain_color_val(self.red)
            self.green = self.contstrain_color_val(self.green)
            self.blue = self.contstrain_color_val(self.blue)
            self.set_color = (int(self.red), int(self.green), int(self.blue))

        else:
            self.set_color = self.color['white']
            self.r = 1

        pg.draw.circle(self.surface, self.set_color, self.vpos, int(self.r), 0)

    @staticmethod
    def contstrain_color_val(val):
        if val < 0:
            val = 0
        elif val > 255:
            val = 255
        return val
    def __str__(self):
        return 'Node at {}'.format(self.pos)

class Branch:
    def __init__(self, surf, parent, pos, direction, mag):
        self.parent = parent
        self.surface = surf
        self.pos = pos
        self.original_direction = direction[:]
        self.direction = direction
        self.mag = mag
        self.count = 0
        self.width = 1

    def next(self):
        nextDir = vect_mul(self.direction, self.mag)
        nextPos = vect_add(self.pos, nextDir)
        nextBranch = Branch(self.surface, self, nextPos, self.direction, self.mag)
        return nextBranch

    def reset(self):
        self.direction = self.original_direction[:]
        self.count = 0

    def draw(self):
        if self.parent:
            pg.draw.line(self.surface, (114, 56, 41), self.pos, self.parent.pos, int(self.width))
        else:
            # pg.draw.circle(self.surface, (0, 82, 0), self.pos, 20, 0)
            pass

    def __str__(self):
        return 'pos:{}; direction:{}'.format(self.pos, self.direction)



if 'win' in sys.platform:
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass




# execution loop






disp_bg_color = (138, 172, 181)
disp_w = 800
disp_h = 800

pg.init()
canvas = pg.display.set_mode((disp_w, disp_h))
canvas.fill(disp_bg_color)

tree = Tree(canvas, random.randrange(100, 800), 5)


while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit(1)
        if event.type == pg.MOUSEBUTTONDOWN:
            print('Number of Branches:{}'.format(len(tree.branches)))
            print('Number of Leaves: {}'.format(len(tree.leaves)))
            print('Tree is done growing? {}'.format(tree.isDoneGrowing))

    canvas.fill(disp_bg_color)
    if tree.animation_complete:
        del tree
        tree = Tree(canvas, random.randrange(100, 800), 5)
    tree.draw()
    tree.grow()
    pg.display.flip()
