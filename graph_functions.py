import pygame as pg
import sys
import ctypes
from math import *
import random
import time


MIN_DIST = 15
MAX_DIST = 150





disp_bg_color = (0, 0, 0)
disp_w = 800
disp_h = 800
x_offset = int(disp_w/2)
y_offset = int(disp_h/2)
scale = 25
resolution = 0.25
draw_axis = True
delta = 1e-15

pg.init()
canvas = pg.display.set_mode((disp_w, disp_h))
canvas.fill(disp_bg_color)



while True:
    canvas.fill(disp_bg_color)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit(1)
        if event.type == pg.MOUSEBUTTONDOWN:
            print(points[0:10])
        if event.type == pg.KEYDOWN:
            if pg.key.get_pressed()[pg.K_EQUALS]:
                scale += scale * 0.5
                resolution *= 0.9
            elif pg.key.get_pressed()[pg.K_MINUS]:
                scale -= scale *0.5
                resolution /= 0.9
            elif pg.key.get_pressed()[pg.K_UP]:
                y_offset -= 10
            elif pg.key.get_pressed()[pg.K_DOWN]:
                y_offset += 10
            elif pg.key.get_pressed()[pg.K_RIGHT]:
                x_offset += 10
            elif pg.key.get_pressed()[pg.K_LEFT]:
                x_offset -= 10
            elif pg.key.get_pressed()[pg.K_g]:
                draw_axis = draw_axis ^ True
            elif pg.key.get_pressed()[pg.K_r]:
                x_offset = int(disp_w / 2)
                y_offset = int(disp_h / 2)
                scale = 25
                resolution = 0.25
                draw_axis = True


    if draw_axis:
        pg.draw.line(canvas, (255, 255, 255), (0, y_offset), (disp_w, y_offset), 1)
        pg.draw.line(canvas, (255, 255, 255), (x_offset, 0), (x_offset, disp_h), 1)
    points = []
    x = -(disp_w/2)
    while x < disp_w:
        try:
            y = sin(x**2)
            points.append((int(x * scale) + x_offset, int(y * -scale) + y_offset))
        except:
            pass

        x += resolution


    prev = points[0]
    for point in points[1:]:
        pg.draw.line(canvas, (255, 255, 255), point, prev, 1)
        prev = point
    pg.display.flip()
