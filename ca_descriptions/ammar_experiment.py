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
from enum import Enum
# ---

# # using _SRC_4 information (Zhang et al., 2017)
# fire =
# plant =

# wind_speed =
# wind_direction =

# temperature =
# moisture =

# # model_formula ->
# #     R = R_0 * K_phi * K_theta * K_s * K_r

# # fire_spread_formula ->
# #     S^t+Deltat_i,j = S^t_i,j + (R^t_i-1,j-1 + ... + R^t_i+1,j+1) * Deltat/L

# # revised_model_formula ->
# #     R_0 = a * T + b * W + c * (100 - RH) - d

# R is the speed of spread of fire
# R_0 is the initial speed of spread of fire
# K_phi is the wind coefficient
# K_theta is the terrain factor # not used here so is set to 1
# K_s is the combistible index # ignition threshold? look at the source
# a = 0.03 # not used here so is set to None
# b = 0.05
# c = 0.01
# d = 0.3
# T is the temperature (degreeC) # not used here so is set to None

# --- GLOBAL VARIABLES AND CODE TO RUN BEFORE MAIN

GRID_SIZE = 50

# turns out the better way is just to make a class I suppose -\n/- (attempt at recreating shrug emoji)
class Cell:
    def __init__(self, desc, state, color,
                 fuel_capacity=1,
                 ignition_threshold=0):
        
        self.state = state
        self.color = color

        self.values = dict()
        self.values["desc"] = desc
        self.values["fuel_capacity"] = fuel_capacity
        self.values["ignition_threshold"] = ignition_threshold
        # self.values["burning_neighbour_duration"] = burning_neighbour_duration

    def __str__(self):
        return f"\n{desc} cell\nstate: {state}, color: {color}\nstatus: {values}"

# an idea for test automation later
# you can put all the values in a csv and have all the simulations run from cmd
# probably should record them too
burnt = Cell("burnt", 0, (0,0,0), 0, 1*4)
burning = Cell("burning", 1, (1,0,0), 192, 1*4)
chapparal = Cell("chapparal", 2, (0,1,0), 192, 0.4*4)
forest = Cell("forest", 3, (0.8,0.4,0.2), 960, 0.7*4)
canyon = Cell("canyon", 4, (0.75,0.75,0.75), 8, 0.1*4)
lake = Cell("lake", 5, (0,0,1), 1, 1*4)
town = Cell("town", 6, (1,1,1), 1, 0*4)

# the order of neighbourstates is NW, N, NE, W, E, SW, S, SE
class Direction(Enum):
    NW = 0
    N = 1
    NE = 2
    W = 3
    E = 4
    SW = 5
    S = 6
    SE = 7

def grid_mapper(fn, grid):
    def row_mapper(fn, row):
        return [fn(cell) for cell in row]
    return np.array([row_mapper(fn, row) for row in grid])

# make sure this list is in the same order as the states
# so that the switcheroo function does not break
# might be a good idea to change switcheroo back to a dict?
possible_cells = [
                 burnt,
                 burning,
                 chapparal,
                 forest,
                 canyon,
                 lake,
                 town
                 ]
def switcheroo(cell_state, value_key="desc", default=-1):
    cell_state = int(cell_state)
    if cell_state < len(possible_cells):
        return possible_cells[cell_state].values[value_key]
    else: return default

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
    config.num_generations = 432#0
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
    global fuel_grid, ignition_grid, durations_grid, wind_direction, wind_speed

    scale_random = 0.2
    scale_duration = 0.02
    scale_neighbours = 0.2
    scale_wind = 3

    # commenting out the unused lines for now
    # make sure they're ACTUALLY unused and not that you forgot them!

    # ----
    # ok so
    # do we need the number of neighbours in each cardinal direction?
    # let's make it and if it ends up unused then we will comment it out or delete it
    # it seems like for that you need to shift the entire grid
    # OR simply figure out how neighbourstates works
    # and then replace all "out of bounds" with 0 burning neighbours
    # and do we need the number of burning neighbours?
    # yes, because we need to increase the probability of a cell burning based on that
    # one more thing: consider integrating flammability and iginition threshold
    # one more thing: consider the position of the "extra forest" and the "air strike"
    # ----
 
    ignition_probabilities = np.random.rand(GRID_SIZE,GRID_SIZE) * scale_random

    # for now the random chance will account for 33.3% of ignition probability
    # i.e. random chance has a % contribution of 33.3%
    # the other 66.7% are from wind and burning neighbours
    # for now all factors are assumed equal but can be adjusted later
    # might want to make the ignition probability depend on
    # how long the neighbours have been burning

    burnt_neighbours = neighbourcounts[burnt.state]
    burning_neighbours = neighbourcounts[burning.state]
    dead_neighbours = burnt_neighbours + burning_neighbours

    ignition_probabilities += (0.125 * burning_neighbours) * scale_neighbours
    durations_grid += burning_neighbours
    ignition_probabilities += durations_grid * scale_duration

    # # this doesn't work
    # # maybe try having a wind grid that scales off of it's speed and
    # # just adds an extra probability grid?
    # if wind_direction:
    #     burning_neighbour_scalar = (neighbourstates[wind_direction] == burning.state)
    #     ignition_probabilities += (wind_speed * burning_neighbour_scalar) * scale_wind

    wind_probabilities_grid = np.random.rand(GRID_SIZE,GRID_SIZE)

    # alright how about stop and take a break now and
    # after that try revisiting the formulas with pen and paper

    burnt_cells = (grid == burnt.state)
    burning_cells = (grid == burning.state)

    chapparal_cells = (grid == chapparal.state)
    forest_cells = (grid == forest.state)
    canyon_cells = (grid == canyon.state)
    flammable_cells = chapparal_cells + forest_cells + canyon_cells

    cells_can_ignite = (ignition_probabilities > ignition_grid) & flammable_cells

    fuel_grid[burning_cells] -= 1
    cells_no_more_fuel = (fuel_grid <= 0)

    cells_to_burnt = (grid == cells_no_more_fuel)
    cells_to_burning = cells_can_ignite & (burning_neighbours > 0)

    grid[cells_to_burnt] = burnt.state
    grid[cells_to_burning] = burning.state

    return grid

def main():
    """ Main function that sets up, runs and saves CA"""
    # Get the config object from set up
    config = setup(sys.argv[1:])

    # Create grid object using parameters from config + transition function
    grid = Grid2D(config, transition_function)

    global fuel_grid, ignition_grid, durations_grid, wind_direction, wind_speed

    fn_fuel = partial(switcheroo, value_key="fuel_capacity", default=1)
    fuel_grid = grid_mapper(fn_fuel, grid.grid)

    fn_ignition = partial(switcheroo, value_key="ignition_threshold", default=0)
    ignition_grid = grid_mapper(fn_ignition, grid.grid)

    # fn_durations = partial(switcheroo, value_key="burning_neighbour_duration", default=0)
    # durations_grid = grid_mapper(fn_durations, grid.grid)

    durations_grid = np.zeros((GRID_SIZE,GRID_SIZE))

    wind_direction = Direction.NW.value
    wind_speed = 1

    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # Save updated config to file
    config.save()

    # Save timeline to file
    utils.save(timeline, config.timeline_path)

if __name__ == "__main__":
    main()
