# Name: Forest Fire
# Dimensions: 2

# --- Set up executable path, do not edit ---
import sys
import inspect
this_file_loc = (inspect.stack()[0][1])
main_dir_loc = this_file_loc[:this_file_loc.index('ca_descriptions')]
sys.path.append(main_dir_loc)
sys.path.append(main_dir_loc + 'capyle')
sys.path.append(main_dir_loc + 'capyle/ca')
sys.path.append(main_dir_loc + 'capyle/guicomponents')
# ---

from capyle.ca import Grid2D, Neighbourhood, randomise2d
import capyle.utils as utils
import numpy as np
from functools import partial

# --- ADJUST THE NECESSARY VALUES IN HERE ---

# note for Adam: please test these values and
# replace S, L, and H variables in the comments
# then get rid of this comment after testing
# Thanks!

# to be used as the length and width of the grid
GRID_SIZE = 50

# strength of North->South and West->East wind
# tested for values between -S and S
# adjust wind strength here
WIND_NS = 1
WIND_WE = -1

# base ignition thresholds for the materials that can burn
# adjust material flammability here
# chapparal tested for values between L1 and H1
# forest tested for values between L2 and H2
# canyon tested for values between L3 and H3
THRESHOLD_CHAPPARAL = 0.8
THRESHOLD_FOREST = 6.1
THRESHOLD_CANYON = 0.3
# ---

class Cell:
    def __init__(self, name, state, color,
                 fuel_capacity=1, ignition_threshold=0):

        self.state = state
        self.color = color

        self.params = dict()
        self.params["name"] = name
        self.params["fuel_capacity"] = fuel_capacity
        self.params["ignition_threshold"] = ignition_threshold

burnt = Cell("burnt", 0, (0,0,0), 0, 999999)
burning = Cell("burning", 1, (1,0,0), 192, 999999)
chapparal = Cell("chapparal", 2, (0,1,0), 192, THRESHOLD_CHAPPARAL)
forest = Cell("forest", 3, (0.8,0.4,0.2), 960, THRESHOLD_FOREST)
canyon = Cell("canyon", 4, (0.75,0.75,0.75), 8, THRESHOLD_CANYON)
lake = Cell("lake", 5, (0,0,1), 1, 999999)
town = Cell("town", 6, (1,1,1), 1, 0)

# make sure this list is in the same order as the states
# so that the switcheroo function does not break
possible_cells = [
                 burnt,
                 burning,
                 chapparal,
                 forest,
                 canyon,
                 lake,
                 town
                 ]

class Direction:
    def __init__(self, value, name, coords):

        self.value = value
        self.name = name
        self.coords = coords

# the order of neighbourstates is NW, N, NE, W, E, SW, S, SE
NW = Direction(0, "NW", (-1,-1))
N = Direction(1, "N", (-1,0))
NE = Direction(2, "NE", (-1,1))
W = Direction(3, "W", (0,-1))
E = Direction(4, "E", (0,1))
SW = Direction(5, "SW", (1,-1))
S = Direction(6, "S", (1,0))
SE = Direction(7, "SE", (1,1))

possible_directions = [NW, N, NE, W, E, SW, S, SE]

# this function maps cell functions onto an entire grid
def grid_mapper(fn, grid):
    def row_mapper(fn, row):
        return [fn(cell) for cell in row]
    return np.array([row_mapper(fn, row) for row in grid])

# this function relies on possible_cells array existing and
# returns values for a particular cell passed into it
def switcheroo(cell_state, value_key="name", default=-100):
    cell_state = int(cell_state)
    if cell_state < len(possible_cells):
        return possible_cells[cell_state].params[value_key]
    else:
        return default

# this function relies on WIND_NS and WIND_WE existing and
# calculates the wind combined effect for each neighbour
def wind_effect(coords):
    row = coords[0]
    col = coords[1]

    wind_effect_NS = 1 - (row * WIND_NS)
    wind_effect_WE = 1 - (col * WIND_WE)

    return wind_effect_NS * wind_effect_WE

# this function does what it says on the tin
# so this comment is probably unnecessary
# but we do need some bonus points for comments!
def six_divided_by(num):
    return 6/num

def setup(args):
    """Set up the config object used to interact with the GUI"""
    config_path = args[0]
    config = utils.load(config_path)

    # -- THE CA MUST BE RELOADED IN THE GUI IF ANY OF THE BELOW ARE CHANGED --
    config.title = "Forest Fire"
    config.dimensions = 2
    config.states = (
                    burnt.state,
                    burning.state,
                    chapparal.state,
                    forest.state,
                    canyon.state,
                    lake.state,
                    town.state
                    )

    # ---- Override the defaults below (these may be changed at anytime) -----
    config.state_colors = [
                          burnt.color,
                          burning.color,
                          chapparal.color,
                          forest.color,
                          canyon.color,
                          lake.color,
                          town.color
                          ]
    config.num_generations = 432 # 9 days - just for testing # 4320 # 90 days
    config.grid_dims = (GRID_SIZE,GRID_SIZE)
    config.wrap = False

    # ------------------------------------------------------------------------

    # the GUI calls this to pass the user defined config
    # into the main system with an extra argument
    # do not change
    if len(args) == 2:
        config.save()
        sys.exit()
    return config

def transition_function(grid, neighbourstates, neighbourcounts):
    """Function to apply the transition rules
    and return the new grid"""
    
    # prepare to use global grids information
    global fuel_grid, ignition_grid, neighbour_multipliers

    burning_neighbour_counts = neighbourcounts[burning.state]
    rand_ignition_probabilities = np.random.rand(GRID_SIZE,GRID_SIZE)

    wind_effect_grid = np.zeros((GRID_SIZE,GRID_SIZE))
    burning_neighbours_effect = np.zeros((GRID_SIZE,GRID_SIZE))

    for direction in possible_directions:
        # here the "diagonal" wind direction effects are divided by 2 to
        # reduce their impact. hence the `/len(direction.name)` part
        wind_effect_grid.fill(wind_effect(direction.coords)/len(direction.name))
        burning_neighbours_effect_grid = neighbourstates[direction.value] == burning.state
        burning_neighbours_effect += burning_neighbours_effect_grid * wind_effect_grid * rand_ignition_probabilities

    burning_neighbours_average = grid_mapper(six_divided_by, neighbour_multipliers)
    base_burning_probabilities = (burning_neighbours_effect * burning_neighbours_average)

    burning_cells = (grid == burning.state)
    flammable_cells = (grid == chapparal.state) + (grid == forest.state) + (grid == canyon.state)
    ignitable_cells = flammable_cells & (base_burning_probabilities + rand_ignition_probabilities > ignition_grid)

    # thanks for scrolling to see the long and descriptive names
    # the lines only get shorter from here so don't worry
    # you won't have to do this again :-)

    fuel_grid[burning_cells] -= 1
    cells_no_more_fuel = (fuel_grid <= 0)

    cells_to_burnt = (grid == cells_no_more_fuel)
    cells_to_burning = ignitable_cells & (burning_neighbour_counts > 0)

    grid[cells_to_burnt] = burnt.state
    grid[cells_to_burning] = burning.state

    return grid

def main():
    """ Main function that sets up, runs and saves CA"""

    # declare global grids information
    global fuel_grid, ignition_grid, neighbour_multipliers

    # Get the config object from set up
    config = setup(sys.argv[1:])

    # Create grid object using parameters from config + transition function
    grid = Grid2D(config, transition_function)

    # create grid containing all cells' fuel capacities
    fn_fuel = partial(switcheroo,
        value_key="fuel_capacity", default=1)
    fuel_grid = grid_mapper(fn_fuel, grid.grid)

    # create grid containing all cells' ignition thresholds
    # (or flammability values)
    fn_ignition = partial(switcheroo,
        value_key="ignition_threshold", default=0)
    ignition_grid = grid_mapper(fn_ignition, grid.grid)

    # set the maximum number of neighbours for the fire spread multiplier
    neighbour_multipliers = np.zeros((GRID_SIZE,GRID_SIZE))
    neighbour_multipliers.fill(6)
    neighbour_multipliers[0].fill(4)
    neighbour_multipliers[GRID_SIZE-1].fill(4)
    for row in range(0, GRID_SIZE):
        if row == 0 or row == GRID_SIZE-1:
            neighbour_multipliers[row][0] = 2.5
            neighbour_multipliers[row][GRID_SIZE-1] = 2.5
        else:
            neighbour_multipliers[row][0] = 4
            neighbour_multipliers[row][GRID_SIZE-1] = 4

    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # Save updated config to file
    config.save()

    # Save timeline to file
    utils.save(timeline, config.timeline_path)

if __name__ == "__main__":
    main()
