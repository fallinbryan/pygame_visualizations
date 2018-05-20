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

class PickleCell:
    def __init__(self, cell):
        self.width = cell.width
        self.row = cell.row
        self.col = cell.col
        self.walls = cell.walls
        self.visited = False

class M:
    def __init__(self, cells, h, w, cell_size):
        self.cells = cells
        self.height = h
        self.width = w
        self.cell_size = cell_size

class Cell:
    def __init__(self, surface, width, row, col):
        self.width = width
        self.surface = surface
        self.row = row
        self.col = col
        self.walls = {'top': True,
                      'right': True,
                      'bottom': True,
                      'left': True}
        self.visited = False
        self.is_highligted = False

    def draw(self):
        x = self.col * self.width
        y = self.row * self.width
        w = self.width



        if self.is_highligted and self.visited:
            rect = pg.Rect(x, y, self.width, self.width)
            pg.draw.rect(self.surface, (255, 200, 0), rect, 0)
            self.is_highligted = False
        elif self.is_highligted:
            rect = pg.Rect(x, y, self.width, self.width)
            pg.draw.rect(self.surface, (255, 200, 0), rect, 0)
            self.is_highligted = False
        elif self.visited:
            rect = pg.Rect(x, y, self.width, self.width)
            pg.draw.rect(self.surface, (0, 0, 0), rect, 0)

        color = (255, 255, 255)
        if self.walls['top']:
            pg.draw.line(self.surface, color, [x, y], [x+w, y], 1)        # top
        if self.walls['right']:
            pg.draw.line(self.surface, color, [x+w, y], [x+w, y+w], 1)    # right
        if self.walls['bottom']:
            pg.draw.line(self.surface, color, [x+w, y+w], [x, y+w], 1)    # bottom
        if self.walls['left']:
            pg.draw.line(self.surface, color, [x, y], [x, y+w], 1)        # left


    def highlight(self):
        self.is_highligted = True

    def __str__(self):
        return 'Cell(row={},column={}) walls:{}'.format(self.row, self.col, self.walls)
class Grid:
    def __init__(self, surface, rows, columns, cell_width):
        self.rows = rows
        self.columns = columns
        self.cell_width = cell_width
        grid = []
        for r in range(rows):
            for c in range(cols):
                grid.append(Cell(surface, cell_width, r, c))
        self.grid = np.array(grid)

    def check_neighbors(self, cell):
        top = right = bottom = left = None
        neighbors = []
        try:
            top = self.grid[self.index(cell.col, cell.row - 1)]
        except:
            pass
        try:
            right = self.grid[self.index(cell.col + 1, cell.row)]
        except:
            pass
        try:
            bottom = self.grid[self.index(cell.col, cell.row+1)]
        except:
            pass
        try:
            left = self.grid[self.index(cell.col - 1, cell.row)]
        except:
            pass

        if top and not top.visited:
            neighbors.append(top)
        if right and not right.visited:
            neighbors.append(right)
        if bottom and not bottom.visited:
            neighbors.append(bottom)
        if left and not left.visited:
            neighbors.append(left)

        if neighbors:
            rnd = random.randrange(0, len(neighbors))
            if neighbors[rnd].col == 9 and neighbors[rnd].row == 9:
                breakpnt = "here"
            return neighbors[rnd]
        else:
            return None

    def index(self, i, j):
        if i < 0 or j < 0 or i > self.columns-1 or j > self.rows -1:
            return 'none'

        return i + j * self.columns

    def remove_walls(self, a, b):
        x = a.col - b.col
        y = a.row - b.row

        if x == 1:
            a.walls['left'] = False
            b.walls['right'] = False
        elif x == -1:
            a.walls['right'] = False
            b.walls['left'] = False

        if y == 1:
            a.walls['top'] = False
            b.walls['bottom'] = False
        elif y == -1:
            a.walls['bottom'] = False
            b.walls['top'] = False

    def draw(self):
        for cell in self.grid:
            if cell.is_highligted or cell.visited:
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
    current_cell = grid.grid[0]
    stack = []
    # execution loop
    maze_done = False
    while not maze_done:
        # pg.time.wait(100)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit(1)
            if event.type == pg.MOUSEBUTTONDOWN:
                pass
                # current_cell.visited = True
                # print('Current {}'.format(current_cell))
                # next_cell = grid.checkNeighbors(current_cell)
                # print('Next {}'.format(next_cell))
                # if next_cell:
                #     next_cell.visited = True
                #     current_cell = next_cell

        canvas.fill(disp_bg_color)
        current_cell.visited = True
        current_cell.highlight()
        # step 1
        next_cell = grid.check_neighbors(current_cell)
        if next_cell:
            next_cell.visited = True
            grid.remove_walls(current_cell, next_cell)
            stack.append(current_cell)
            # step 4
            current_cell = next_cell
        elif stack:
            current_cell = stack.pop()

        else:
            maze_done = True
        grid.draw()


        pg.display.flip()

    for_pickle = [PickleCell(cell) for cell in grid.grid]
    maze = M(for_pickle, disp_h, disp_w, cell_width)

    with open('maze.pickle', 'wb') as pf:
        pickle.dump(maze, pf)

