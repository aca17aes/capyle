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
# ---

# --- GLOBAL VARIABLES AND CODE TO RUN BEFORE MAIN

GRID_SIZE = 50

# turns out the better way is just to make a class I suppose -\n/- (attempt at recreating shrug emoji)
class Cell:
    def __init__(self, desc, state, color, fuel_capacity=1, ignition_threshold=0):
        self.state = state
        self.color = color

        self.values = dict()
        self.values["desc"] = desc
        self.values["fuel_capacity"] = fuel_capacity
        self.values["ignition_threshold"] = ignition_threshold

    def __str__(self):
        return f"\n{desc} cell\nstate: {state}, color: {color}\nstatus: {values}"

burnt = Cell("burnt", 0, (0,0,0), 0, 1)
burning = Cell("burning", 1, (1,0,0), 192, 1)
chapparal = Cell("chapparal", 2, (0,1,0), 192, 0.6)
forest = Cell("forest", 3, (0.8,0.4,0.2), 960, 0.9)
canyon = Cell("canyon", 4, (0.75,0.75,0.75), 8, 0.3)
lake = Cell("lake", 5, (0,0,1), 1, 1)
town = Cell("town", 6, (1,1,1), 1, 0)

def grid_mapper(fn, grid):
    def row_mapper(fn, row):
        return [fn(cell) for cell in row]
    return np.array([row_mapper(fn, row) for row in grid])

def switcheroo(cell_state, value_key="desc", default=-1):
    values = {
        burnt.state: burnt.values[value_key],
        burning.state: burning.values[value_key],
        chapparal.state: chapparal.values[value_key],
        forest.state: forest.values[value_key],
        canyon.state: canyon.values[value_key],
        lake.state: lake.values[value_key],
        town.state: town.values[value_key]
    }
    return values.get(cell_state, default)

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
    global fuel_grid, ignition_grid
 
    random_ignition_grid = np.random.rand(GRID_SIZE,GRID_SIZE)

    burnt_neighbours = neighbourcounts[burnt.state]
    burning_neighbours = neighbourcounts[burning.state]
    dead_neighbours = burnt_neighbours + burning_neighbours

    burnt_cells = (grid == burnt.state)
    burning_cells = (grid == burning.state)

    chapparal_cells = (grid == chapparal.state)
    forest_cells = (grid == forest.state)
    canyon_cells = (grid == canyon.state)
    cells = chapparal_cells + forest_cells + canyon_cells

    cells_can_ignite = (random_ignition_grid > ignition_grid)

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

    global fuel_grid, ignition_grid

    fn_fuel = partial(switcheroo, value_key="fuel_capacity", default=1)
    fuel_grid = grid_mapper(fn_fuel, grid.grid)
    # might want to change this since the ignition values are only used once
    fn_ignition = partial(switcheroo, value_key="ignition_threshold", default=0)
    ignition_grid = grid_mapper(fn_ignition, grid.grid)

    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # Save updated config to file
    config.save()

    # Save timeline to file
    utils.save(timeline, config.timeline_path)

if __name__ == "__main__":
    main()
