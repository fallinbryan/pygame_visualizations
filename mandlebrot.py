import pygame as pg
import sys
import ctypes
import mandleGen
import random
import time


def pixel(surface, color, pos):
    surface.set_at(pos, color)


if 'win' in sys.platform:
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

disp_bg_color = (0, 0, 0)
disp_w = 800
disp_h = 800
pg.init()
canvas = pg.display.set_mode((disp_w, disp_h))
canvas.fill(disp_bg_color)


white = (255, 255, 255)
black = (0, 0, 0)
x_min = -2.0
x_max = 1
y_min = -1.5
y_max = 1.5
# execution loop

start = time.clock()
MAP = mandleGen.render_mandlebrot(x_min, x_max, y_min, y_max, disp_h, disp_w)
print('Time to generate set: {}'.format(time.clock() - start))

start = time.clock()
for element in MAP:
    canvas.set_at(element[0], element[1])
print('Time to draw set: {}'.format(time.clock() - start))
pg.display.flip()
scale = 1
while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit(1)
        if event.type == pg.MOUSEBUTTONDOWN:
            scale *= 0.5
            x, y = pg.mouse.get_pos()
            x_transformed = mandleGen.map(x, 0, disp_w, x_min, x_max)
            y_transformed = mandleGen.map(y, 0, disp_h, y_min, y_max)
            x_min = x_transformed - scale
            x_max = x_transformed + scale
            y_min = y_transformed - scale
            y_max = y_transformed + scale
            start = time.clock()
            MAP = mandleGen.render_mandlebrot(x_min, x_max, y_min, y_max, disp_h, disp_w)
            print('Time to generate set: {}'.format(time.clock() - start))
            start = time.clock()
            for element in MAP:
                pixel(canvas, element[1], element[0])
            print('Time to draw set: {}'.format(time.clock() - start))
            pg.display.flip()

            print('Zoom: {:0.1f}x'.format(1/scale))








