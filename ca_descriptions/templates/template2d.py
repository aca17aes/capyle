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

def setup(args):
    """Set up the config object used to interact with the GUI"""
    config_path = args[0]
    config = utils.load(config_path)
    # -- THE CA MUST BE RELOADED IN THE GUI IF ANY OF THE BELOW ARE CHANGED --
    config.title = "Forest Fire"
    config.dimensions = 2
    config.states = (0, 1, 2, 3, 4, 5, 6) # 0-3: unburnt chapparal/dense_forest/canyon/lake, 4: burning, 5: burnt
    
    # -------------------------------------------------------------------------

    # ---- Override the defaults below (these may be changed at anytime) ----

    YELLOW = (1,1,0)
    GREEN = (0,1,0)
    GREY = (0.5,0.5,0.5)
    BLUE = (0,0,1)
    RED = (1,0,0)
    BLACK = (0,0,0)
    WHITE = (1,1,1)

    # 0-3: unburnt chapparal/dense_forest/canyon/lake, 4: burning, 5: burnt, 6: town
    config.state_colors = [YELLOW,GREEN,GREY,BLUE,RED,BLACK, WHITE]
    config.num_generations = 50 # 4320 # 90 days - 30-minute time steps
    config.grid_dims = (50,50)
    config.wrap = False # where is the original config file with all the defaults?
    # ok so I couldn't find it BUT the original wolframs_1d has the config.wrap set up

    # ----------------------------------------------------------------------

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

    GRASS = 0
    FOREST = 1
    CANYON = 2
    LAKE = 3
    BURNING = 4
    BURNT = 5
    TOWN = 6

    TERRAIN = [
        { # 0
            "name": "grass",
            "state": 0,
            "ignition": 0.6,
            "fuel_capacity": 192,
            "colour": (0,1,0)
        },

        { # 1
            "name": "dense_forest",
            "state": 1,
            "ignition": 0.3,
            "fuel_capacity": 960,
            "colour": (0,1,0)
        },

        { # 2
            "name": "canyon",
            "state": 2,
            "ignition": 0.9,
            "fuel_capacity": 8,
            "colour": (0.5,0.5,0.5)
        },

        { # 3
            "name": "lake",
            "state": 3,
            "ignition": 0,
            "fuel_capacity": 0,
            "colour": (0,0,1)
        }
    ]

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
    # more initialization

    GRASS = 0
    FOREST = 1
    CANYON = 2
    LAKE = 3
    BURNING = 4
    BURNT = 5
    TOWN = 6

    fuel_values_grid = np.zeros(shape=(50, 50))
    for row in range(50):
        print(f"ROW IS {row}")
        for col in range(50):
            print(f"COL IS {col}")
            if grid.grid[row,col] == GRASS:
                fuel_values_grid[row,col] = 192
            elif grid.grid[row,col] == FOREST:
                fuel_values_grid[row,col] = 960
            elif grid.grid[row,col] == CANYON:
                fuel_values_grid[row,col] = 8
            elif grid.grid[row,col] == LAKE:
                fuel_values_grid[row,col] = 1
            elif grid.grid[row,col] == BURNING:
                fuel_values_grid[row,col] = 192
            elif grid.grid[row,col] == TOWN:
                fuel_values_grid[row,col] = 1

    print(f"FUEL VALUES GRID = {fuel_values_grid}")
    print(f"THE REAL GRID = {grid.grid}")
    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # Save updated config to file
    config.save()
    # Save timeline to file
    utils.save(timeline, config.timeline_path)

if __name__ == "__main__":
    main()
