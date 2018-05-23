import pygame as pg
import sys
import ctypes
import random
import math
from Vector import Vector
from Vector import Vector2D

random.seed()


class Segment(object):
    def __init__(self, surface, **kwargs):
        try:
            self.parent = kwargs["parent"]
        except KeyError:
            self.parent = None
        self.surface = surface
        if self.parent:
            self.base = self.parent.end
        else:
            try:
                self.base = kwargs["base"]
            except KeyError:
                raise AttributeError('Segment must have either a base vector, or a parent')
        self.end = None
        try:
            self.theta = kwargs["theta"]
        except KeyError:
            raise AttributeError('Segment must have an angle, theta=angle')
        try:
            self.length = kwargs["length"]
        except KeyError:
            raise AttributeError('Segment must have a length, length=length')
        try:
            self.width = kwargs['width']
        except KeyError:
            self.width = 10

        try:
            self.color = kwargs['color']
        except KeyError:
            self.color = (255, 255, 255, 150)

        self.calculate_end(self.theta)
        self.next_segment = None

    def calculate_end(self, theta):
        dx = math.cos(theta)
        dy = math.sin(theta)
        self.end = Vector2D(self.base.x + self.length*dx, self.base.y + self.length*dy)

    def calculate_head(self, theta):
        dx = math.cos(theta)
        dy = math.sin(theta)
        self.base = Vector2D(self.end.x - self.length*dx, self.end.y - self.length*dy)

    def rotate(self, theta):
        self.theta += theta
        self.calculate_end(self.theta)
        next_seg = self.next_segment
        current = self
        while next_seg:
            next_seg.base = current.end
            next_seg.calculate_end(next_seg.theta)
            current = next_seg
            next_seg = next_seg.next_segment

    def rotate_to(self, theta):
        self.theta = theta
        self.calculate_end(self.theta)
        next_seg = self.next_segment
        current = self
        while next_seg:
            next_seg.base = current.end
            next_seg.calculate_end(next_seg.theta)
            current = next_seg
            next_seg = next_seg.next_segment

    def rotate_to_not_end(self, theta):
        self.theta = theta
        self.calculate_end(self.theta)
        next_seg = self.next_segment
        current = self
        while next_seg.next_segment:
            next_seg.base = current.end
            next_seg.calculate_end(next_seg.theta)
            current = next_seg
            next_seg = next_seg.next_segment

    def reverse_rotate(self, theta):
        flip =1
        self.theta = theta
        self.calculate_head(self.theta)
        next_seg = self.parent
        current = self
        while next_seg.parent:
            flip *= -1
            next_seg.end = current.base
            next_seg.calculate_head(next_seg.theta*flip)
            next_seg = next_seg.parent

        next_seg.rotate_to_not_end(next_seg.theta)

    def draw(self):

        if self.width < 1:
            self.width = 1
        pg.draw.line(self.surface, self.color, self.base(), self.end(), self.width)
        # pg.draw.circle(self.surface, self.color, self.base.floor()(), 10, 1)
        # pg.draw.circle(self.surface, (0, 255, 150), self.end.floor()(), 5, 0)
    def __str__(self):
        return 'seg_start: {} seg_end: {}'.format(self.base, self.end)

class Armature(object):
    def __init__(self, surface, position, seg_count, seg_scale, base_len, theta):
        # width = seg_count*2
        self.seg_count = seg_count
        width = 1
        self.total_length = base_len
        self.base = Segment(surface, base=position, theta=theta,
                            length=base_len, width=width)
        next_seg = self.base.next_segment
        current_seg = self.base

        for _ in range(seg_count):

            length = base_len
            self.total_length += length
            width -= 10
            current_seg.next_segment = Segment(surface, parent=current_seg, theta=theta,
                               length=length, width=width)
            current_seg = current_seg.next_segment
        self.tail = current_seg
        self.relative_length = self.total_length
    def draw(self):
        self.base.draw()
        next_seg = self.base.next_segment
        while next_seg:
            next_seg.draw()
            next_seg = next_seg.next_segment

    def orbit(self, theta):
        self.base.rotate(theta)
        next_seg = self.base.next_segment
        theta_multiplier = 2
        while next_seg:
            next_seg.rotate(theta*theta_multiplier)
            next_seg = next_seg.next_segment
            theta_multiplier += 1

    def wave(self):
        next_seg = self.base.next_segment
        theta = random.uniform(-0.01,0.01)
        self.base.rotate(theta)

        while next_seg:
            next_theta = random.uniform(-0.01, 0.01)
            next_seg.rotate(next_theta)
            next_seg = next_seg.next_segment

    def reach(self, target):
        dx = target.x - self.base.base.x
        dy = target.y - self.base.base.y
        theta = math.atan2(dy, dx)
        self.base.rotate_to(theta)
        next_seg = self.base.next_segment
        while next_seg:

            next_seg.rotate_to(theta)
            next_seg = next_seg.next_segment

        d = self.base.base.distance(target)
        if d < self.total_length:
            self.grab(target)
        else:
            self.relative_length = self.total_length

    def grab(self, target):
        self.tail.end = target
        self.relative_length = self.base.base.distance(target)
        self.collapse_to(self.relative_length)
        # delta_d = self.total_length - self.base.base.distance(target)
        # dx = self.tail.length - delta_d
        # a = self.tail.parent.length + dx
        # c = self.tail.parent.length
        # b = self.tail.length
        # gamma = math.acos(-0.5*((c**2-a**2-b**2)/(2*a*b)))
        # dy = self.tail.length * math.sin(gamma)
        # dx = dx * math.cos(gamma)
        # self.tail.base = Vector2D(self.tail.base.x, self.tail.base.y + dy)
        # self.tail.parent.end = self.tail.base

    def collapse_to(self, length):
        self.tail.label = "tail"
        lenght_ratio = length / self.total_length
        if lenght_ratio < 0.5:
            debug = "here"
        current = self.tail
        debug = self.tail
        prev = self.tail.parent
        flip = -1
        while prev:
            delta_x = current.length * lenght_ratio
            a = current.length*lenght_ratio + delta_x
            b = current.length
            c = prev.length
            if a == 0:
                a = 0.000000000001

            gamma = math.acos((a**2 + b**2 - c**2) / (2 * a * b))

            # current.rotate(current.theta + gamma*flip)
            current.calculate_head(current.theta + gamma*flip)
            prev.end = current.base
            current = prev
            prev = current.parent
            flip *= -1
        current.color = (255, 255, 0)
        # current.rotate(gamma*flip)
        # current.calculate_end(current.theta + gamma)


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
        color = self.getColor()
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

        #TOP
        pg.draw.line(self.parent,color['top'],
                     [top_left_x, top_left_y],
                     [top_right_x,top_right_y], 4)
        #RIGHT
        pg.draw.line(self.parent, color['right'],
                     [top_right_x, top_right_y],
                     [bottom_right_x, bottom_right_y], 4)
        #BOTTOM
        pg.draw.line(self.parent, color['bottom'],
                     [bottom_right_x, bottom_right_y],
                     [bottom_left_x, bottom_left_y], 4)
        #LEFT
        pg.draw.line(self.parent, color['left'],
                     [bottom_left_x,bottom_left_y],
                     [top_left_x, top_left_y], 4)

    def getColor(self):
        colors = {'top':self.color,
                    'right':self.color,
                    'bottom':self.color,
                    'left':self.color}
        if self.theta >= math.pi/3 and self.theta < (2/3) * math.pi:
            colors['top'] = (255, 255, 255)
        elif self.theta >= (2/3)*math.pi and self.theta < (4/3)*math.pi:
            colors['right'] = (255,255,255)
        elif self.theta >= (4/3)*math.pi and self.theta <(5/3)*math.pi:
            colors['bottom'] = (255,255,255)
        else:
            colors['left'] = (255,255,255)

        return colors




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
    WIDTH = canvas.get_width()
    HEIGHT = canvas.get_height()

    pos = Vector2D(WIDTH/2, HEIGHT/2)
    arm = Armature(canvas, pos, 20, 0.5, 25, -math.pi/2)

    seg = Segment(canvas, base=pos, length=10, theta=math.pi/2,
                  )
    while True:
        # pg.time.wait(100)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit(1)
            if event.type == pg.MOUSEBUTTONDOWN:
                canvas.fill(disp_bg_color)
                # arm.draw()
                # arm.orbit(0.1)
                # seg.draw()
                # seg.rotate(0.1)
            if event.type == pg.MOUSEBUTTONUP:
              pass
            if event.type == pg.MOUSEMOTION:
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
        arm.draw()
        pos = Vector2D(*pg.mouse.get_pos())
        arm.reach(pos)

        # seg.draw()
        # seg.rotate(0.01)
        pg.display.flip()
        pg.time.delay(0)

