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
from collections import namedtuple
# ---

# --- GLOBAL VARIABLES

GRID_SIZE = (7,7)

State = namedtuple("State", "id color")

burnt = State(0, (0,0,0))
burning = State(1, (1,0,0))
unburnt = State(2, (0,1,0))
kappa_state = State(3, (1,1,1))

Material = namedtuple("Material", "id color ")

#

fuel_grid = np.zeros(GRID_SIZE)
def fuel_mapper(grid_row):
    def fuel_switch(material):
        capacities = {
            0: 192,
            1: 200,
            2: 483,
            3: 4
        }
        return capacities.get(material, 1)
    return [fuel_switch(cell) for cell in grid_row]

def setup(args):
    """Set up the config object used to interact with the GUI"""
    config_path = args[0]
    config = utils.load(config_path)

    # -- THE CA MUST BE RELOADED IN THE GUI IF ANY OF THE BELOW ARE CHANGED --
    config.title = "Forest Fire"
    config.dimensions = 2
    config.states = (burnt.id, burning.id, unburnt.id, kappa_state.id)

    # ---- Override the defaults below (these may be changed at anytime) -----

    config.state_colors = [burnt.color, burning.color, unburnt.color, kappa_state.color]
    config.num_generations = 21
    config.grid_dims = GRID_SIZE
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

    burnt_neighbours = neighbourcounts[burnt.id]
    burning_neighbours = neighbourcounts[burning.id]

    burnt_cells = (grid == burnt.id)
    burning_cells = (grid == burning.id)
    unburnt_cells = (grid == unburnt.id)
    kappa_state_cells = (grid == kappa_state.id)

    global fuel_grid
    fuel_grid[burning_cells] -= 99
    print(fuel_grid)

    no_more_fuel = (fuel_grid <= 0)

    cells_to_burnt = (grid == no_more_fuel)
    cells_to_burning = (unburnt_cells | kappa_state_cells) & (burning_neighbours > 0)

    grid[cells_to_burnt] = burnt.id
    grid[cells_to_burning] = burning.id

    # seems that the initial fuel grid is functioning as it should
    # HOWEVER the fire isn't spreading yet so they will all burn out at the same time

    # # 2d arrays representing the grid
    # burning_neighbours = neighbourcounts[BURNING]

    # unburnt_grass = grid == grass["state"]
    # burning_cells = grid == BURNING

    # # burn if burning neighbour(s) and if chapparal
    # cells_to_burn = (burning_neighbours > 0) & (grid == grass["state"])

    # grass_fuel_values_lt0 = grid == (grass["fuel_capacity"] <= 0)
    # too_burnt_grass = (grid == BURNING) & (grid == grass["state"]) & grass_fuel_values_lt0

    # # if grass is burning and fuel > 0:
    #     # fuel--

    # grid[cells_to_burn] = BURNING

    return grid

def main():
    """ Main function that sets up, runs and saves CA"""
    # Get the config object from set up
    config = setup(sys.argv[1:])

    # Create grid object using parameters from config + transition function
    grid = Grid2D(config, transition_function)
    # how can I make this global and use it in the transition function?
    global fuel_grid
    fuel_grid = np.array([fuel_mapper(row) for row in grid.grid])

    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # Save updated config to file
    config.save()

    # Save timeline to file
    utils.save(timeline, config.timeline_path)

if __name__ == "__main__":
    main()
