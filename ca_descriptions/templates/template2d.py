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
    config.num_generations = 4320 # 90 days - 30-minute time steps
    config.grid_dims = (50,50)

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
    
    ch, df, ca, la, br, bu, tw = neighbourcounts
    # [X, X, X
    #  X, P, X,
    #  X, X, X]

    cell_should_burn = (grid == 4)

    if np.any(cell_should_burn):
        burn = True
    else:
        burn = False

    grid[:, :] = 0

    grid[burn] = 4

    return grid

    # # dead = state == 0, live = state == 1
    # # unpack state counts for state 0 and state 1
    # dead_neighbours, live_neighbours = neighbourcounts
    # # create boolean arrays for the birth & survival rules
    # # if 3 live neighbours and is dead -> cell born
    # birth = (live_neighbours == 3) & (grid == 0)
    # # if 2 or 3 live neighbours and is alive -> survives
    # survive = ((live_neighbours == 2) | (live_neighbours == 3)) & (grid == 1)
    # # Set all cells to 0 (dead)
    # grid[:, :] = 0
    # # Set cells to 1 where either cell is born or survives
    # grid[birth | survive] = 1
    # return grid


def main():
    """ Main function that sets up, runs and saves CA"""
    # Get the config object from set up
    config = setup(sys.argv[1:])

    # Create grid object using parameters from config + transition function
    grid = Grid2D(config, transition_function)

    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # Save updated config to file
    config.save()
    # Save timeline to file
    utils.save(timeline, config.timeline_path)

if __name__ == "__main__":
    main()
