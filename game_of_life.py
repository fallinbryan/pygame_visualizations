import pygame as pg
import sys
import ctypes
import random
import numpy as np
import pickle
random.seed()

disp_bg_color = (255, 255, 255)
disp_w = 800
disp_h = 800
cell_width = 10
rows = int(disp_w / cell_width)
cols = int(disp_h / cell_width)


class Cell:
    def __init__(self, surface, width, row, col):
        self.width = width
        self.surface = surface
        self.row = row
        self.col = col

        self.alive = False

    def draw(self):
        x = self.col * self.width
        y = self.row * self.width
        w = self.width
        black = (0, 0, 0)
        white = (255, 255, 255)

        if self.alive:
            color = black
        else:
            color = white

        rect = pg.Rect(x, y, self.width, self.width)
        pg.draw.rect(self.surface, color, rect, 0)
        pg.draw.line(self.surface, black, [x, y], [x+w, y], 1)        # top
        pg.draw.line(self.surface, black, [x+w, y], [x+w, y+w], 1)    # right
        pg.draw.line(self.surface, black, [x+w, y+w], [x, y+w], 1)    # bottom
        pg.draw.line(self.surface, black, [x, y], [x, y+w], 1)        # left

    def __str__(self):
        return 'Cell(row={},column={}) walls:{}'.format(self.row, self.col, self.walls)
class Grid:
    def __init__(self, surface, rows, columns, cell_width):
        self.rows = rows
        self.columns = columns
        self.cell_width = cell_width
        self.is_simulation_running = False
        grid = []
        for r in range(rows):
            for c in range(cols):
                grid.append(Cell(surface, cell_width, r, c))
        self.grid = grid

    def check_neighbors(self, cell):
        living_neighbors = 0
        neumann_neighbors = {'top': (cell.col + 0, cell.row - 1),
                             'right': (cell.col + 1, cell.row + 0),
                             'bottom': (cell.col + 0, cell.row + 1),
                             'left': (cell.col - 1, cell.row + 0)}

        moore_neighbors = {'top': (cell.col + 0, cell.row - 1),
                           'top_right': (cell.col + 1, cell.row - 1),
                           'right': (cell.col + 1, cell.row + 0),
                           'bottom_right': (cell.col + 1, cell.row + 1),
                           'bottom': (cell.col + 0, cell.row + 1),
                           'bottom_left': (cell.col - 1, cell.row + 1),
                           'left': (cell.col - 1, cell.row + 0),
                           'top_left': (cell.col - 1, cell.row - 1)}

        for neighbor in moore_neighbors:
            try:
                next = self.grid[self.index(*moore_neighbors[neighbor])]
                if next.alive:
                    living_neighbors += 1
            except:
                pass

        return living_neighbors

    def index(self, i, j):
        if i < 0 or j < 0 or i > self.columns-1 or j > self.rows -1:
            return 'none'

        return i + j * self.columns

    def apply_rules(self):
        map_the_living = {0: False, 1: False, 2: True, 3: True, 4: False, 5: False, 6: False, 7: False, 8: False}
        map_the_dead = {0: False, 1: False, 2: False, 3: True, 4: False, 5: False, 6: False, 7: False, 8: False}
        population_control = []
        for cell in self.grid:
            living_cells = self.check_neighbors(cell)
            if cell.alive:
                population_control.append(map_the_living[living_cells])
            else:
                population_control.append(map_the_dead[living_cells])

        for i, cell in enumerate(self.grid):
            cell.alive = population_control[i]

    def toggle_cell(self, i, j):
        state = self.grid[self.index(int(i/self.cell_width), int(j/self.cell_width))].alive
        self.grid[self.index(int(i/self.cell_width), int(j/self.cell_width))].alive = state ^ True

    def toggle_sim_state(self):
        self.is_simulation_running = self.is_simulation_running ^ True

    def reset(self):
        for cell in self.grid:
            cell.alive = False

    def draw(self):
        if self.is_simulation_running:
            self.apply_rules()
        else:
            pass
        for cell in self.grid:
            cell.draw()



if __name__ == '__main__':


    if 'win' in sys.platform:
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass



    canvas = pg.display.set_mode((disp_w, disp_h))
    canvas.fill(disp_bg_color)


    grid = Grid(canvas, rows, cols, cell_width)

    while  True:
        # pg.time.wait(100)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit(1)
            if event.type == pg.MOUSEBUTTONDOWN:
                grid.toggle_cell(*pg.mouse.get_pos())
            if event.type == pg.KEYDOWN:
                if pg.key.get_pressed()[pg.K_RETURN]:
                    grid.toggle_sim_state()
                elif pg.key.get_pressed()[pg.K_SPACE]:
                    grid.apply_rules()
                elif pg.key.get_pressed()[pg.K_ESCAPE]:
                    grid.reset()
        canvas.fill(disp_bg_color)

        grid.draw()


        pg.display.flip()


