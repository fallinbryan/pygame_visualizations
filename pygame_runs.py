import pygame as pg
import sys
import ctypes

if 'win' in sys.platform:
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

disp_bg_color = (0, 0, 0)
disp_w = 1600
disp_h = 1200

canvas = pg.display.set_mode((disp_w, disp_h))
canvas.fill(disp_bg_color)

# execution loop
while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit(1)