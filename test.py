import numpy as np

grid = np.zeros((7,7))
fuel_grid = np.zeros((7,7))

def fuel_mapper(grid_row):
    def init_fuel(state):
        switch = {
            0: 192,
            1: 200,
            2: 483
        }
        return switch.get(state, 0)
    return [init_fuel(cell) for cell in grid_row]

grid[0][2] = 2
grid[1][4] = 1
grid[3][1] = 2
grid[1][0] = 1
grid[4][1] = 2
grid[1][3] = 1
grid[2][1] = 2

#print(grid)

#fuel_grid = np.array([fuel_mapper(row) for row in grid])

#print(fuel_grid)

from functools import partial
def fun4(x, y=2, z=5):
    return x + y + z

def row_mapper(fn, row):
    return [fn(cell) for cell in row]

import numpy as np

kappa = np.random.rand(5)

p1 = partial(fun4, y=6, z=9)

answer = row_mapper(p1, kappa)
print(answer)

