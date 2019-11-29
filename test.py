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

print(grid)

fuel_grid = np.array([fuel_mapper(row) for row in grid])

print(fuel_grid)
