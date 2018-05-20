import pygame as pg
import sys
import ctypes
import random, time
import math
import pickle
from maze_generator import M, PickleCell
random.seed()


with open('maze.pickle', 'rb') as pf:
    maze = pickle.load(pf)


disp_bg_color = (0, 0, 0)
disp_w = maze.width
disp_h = maze.height
cell_width = maze.cell_size
rows = int(disp_w / cell_width)
cols = int(disp_h / cell_width)


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

        self.heuristic = None
        self.cost = None

    def draw(self):
        x = self.col * self.width
        y = self.row * self.width
        w = self.width
        rect = pg.Rect(x, y, self.width, self.width)
        if self.cost < 0:
            grey = 0
        elif self.cost > 255:
            grey = 255
        else:
            grey = self.cost

        pg.draw.rect(self.surface, (grey, grey, grey), rect, 0)


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
            pg.draw.rect(self.surface, (255, 0, 255), rect, 0)


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
    def __init__(self, surface, maze_obj):
        self.surface = surface
        self.rows = int(maze_obj.height / maze_obj.cell_size)
        self.columns = int(maze_obj.width / maze_obj.cell_size)
        self.cell_width = maze_obj.cell_size
        grid = []
        for cell in maze_obj.cells:
            newCell = Cell(self.surface, cell.width, cell.row, cell.col)
            newCell.walls = cell.walls
            grid.append(newCell)
        self.grid = grid



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

        if top and not top.visited and not top.walls['bottom']:
            neighbors.append(top)
        if right and not right.visited and not right.walls['left']:
            neighbors.append(right)
        if bottom and not bottom.visited and not bottom.walls['top']:
            neighbors.append(bottom)
        if left and not left.visited and not left.walls['right']:
            neighbors.append(left)

        if neighbors:
            return sorted(neighbors, key=lambda x: (x.heuristic + x.cost))
        else:
            return None

    def index(self, i, j):
        if i < 0 or j < 0 or i > self.columns-1 or j > self.rows -1:
            return 'none'

        return i + j * self.columns

    def apply_heuristics(self, goal_cell):
        for cell in self.grid:
            x = goal_cell.col - cell.col
            y = goal_cell.row - cell.row
            cell.heuristic = math.sqrt(x**2 + y**2)
            cell.cost = random.randrange(155, 200)

    def draw(self):
        [cell.draw() for cell in self.grid]

if 'win' in sys.platform:
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

def distance(a, b):
    x = b.col - a.col
    y = b.row = a.row
    return math.sqrt(x**2 + y**2)

canvas = pg.display.set_mode((disp_w, disp_h))
canvas.fill(disp_bg_color)


grid = Grid(canvas, maze)
current_cell = grid.grid[0]
target_cell = grid.grid[-1]
grid.apply_heuristics(target_cell)
stack = []
# execution loop
maze_done = False
path = []
start = time.clock()
while not maze_done:
    # pg.time.wait(500)
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

    if current_cell is not target_cell:
        current_cell.visited = True
        # current_cell.highlight()
        neighbors = grid.check_neighbors(current_cell)
        next_cell = None
        if neighbors:
            next_cell = neighbors[0]
        if next_cell:
            next_cell.visited = True
            stack.append(current_cell)
            current_cell = next_cell
            path.append(current_cell)
        else:
            current_cell = stack.pop()
            path.pop()
        grid.draw()
        for i, cell in enumerate(path):
            x = cell.col * cell.width + int(cell_width / 2)
            y = cell.row * cell.width + int(cell_width / 2)
            if i-1 != -1:
                prev_x = path[i-1].col * cell_width +int(cell_width / 2)
                prev_y = path[i-1].row * cell_width +int(cell_width / 2)
            else:
                prev_x = int(cell_width/2)
                prev_y = int(cell_width/2)
            pg.draw.line(canvas, (0, 0, 244), [x, y], [prev_x, prev_y], 3)
    else:
        print('Path length: {}'.format(len(path)))
        print('Time to discovery: {:.0f}s'.format( (time.clock() - start)*1000))
        for cell in path:
            cell.cost -= 10
        for cell in grid.grid:
            cell.visited = False
        path.clear()
        current_cell = grid.grid[0]
        canvas.fill(disp_bg_color)
        start = time.clock()




    pg.display.flip()



