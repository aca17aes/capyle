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
import numpy.random as rnd
from collections import namedtuple
# ---

# --- GLOBAL VARIABLES AND CODE TO RUN BEFORE MAIN

GRID_SIZE = 50

Cell = namedtuple("Cell", "state color fuel_capacity ignition_threshold")

burnt = Cell(0, (0,0,0), 0, 1)
burning = Cell(1, (1,0,0), 192, 1)
chapparal = Cell(2, (0,1,0), 192, 0.6)
forest = Cell(3, (0.8,0.4,0.2), 960, 0.9)
canyon = Cell(4, (0.75,0.75,0.75), 8, 0.3)
lake = Cell(5, (0,0,1), 1, 1)
town = Cell(6, (1,1,1), 1, 0)

def grid_mapper(fn, grid):
    def row_mapper(fn, row):
        return [fn(cell) for cell in row]
    return np.array([row_mapper(fn, row) for row in grid])

def fuel_switch(cell_state):
    fuel_capacities = {
        burnt.state: burnt.fuel_capacity,
        burning.state: burning.fuel_capacity,
        chapparal.state: chapparal.fuel_capacity,
        forest.state: forest.fuel_capacity,
        canyon.state: canyon.fuel_capacity,
        lake.state: lake.fuel_capacity,
        town.state: town.fuel_capacity
    }
    return fuel_capacities.get(cell_state, 1)

def ignition_switch(cell_state):
    ignition_thresholds = {
        burnt.state: burnt.ignition_threshold,
        burning.state: burning.ignition_threshold,
        chapparal.state: chapparal.ignition_threshold,
        forest.state: forest.ignition_threshold,
        canyon.state: canyon.ignition_threshold,
        lake.state: lake.ignition_threshold,
        town.state: town.ignition_threshold
    }
    return ignition_thresholds.get(cell_state, 0)

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
    # how can I make this global and use it in the transition function?
    global fuel_grid, ignition_grid
    fuel_grid = grid_mapper(fuel_switch, grid.grid)
    # might want to change this since the ignition values are only used once
    ignition_grid = grid_mapper(ignition_switch, grid.grid)

    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # Save updated config to file
    config.save()

    # Save timeline to file
    utils.save(timeline, config.timeline_path)

if __name__ == "__main__":
    main()
