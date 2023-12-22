# https://stackoverflow.com/questions/15908371/matplotlib-colorbars-and-its-text-labels
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import matplotlib.colors as mcolors
import numpy as np

from astar_lib import OBSTACLE, WALKABLE, BORDER, VISITED, SOL_PATH

# plot parameters
fig_size = (12, 5)

# calculate the values at which each color should appear
# the last entry is used to complete the range of values each color represents, because one more is needed to display all colors
# - WALKABLE / 2 is used for the centering of the color labes inside of the colorbar
colorbar_vals = np.array([OBSTACLE, WALKABLE, BORDER, VISITED, SOL_PATH, SOL_PATH + WALKABLE]) - WALKABLE / 2
color_labels = ['obstacle','walkable','border','visited', "solution"]

#discrete color scheme
colors = ['white', 'limegreen', 'skyblue', 'dodgerblue', 'red']
train_car_colors = ['white', 'limegreen', 'mediumpurple', 'dodgerblue', 'red']
cMap = ListedColormap(colors)
norm = mcolors.BoundaryNorm(colorbar_vals, cMap.N)

tick_count = 4

def calculate_swiss_map_ticks(maze_shape: tuple[int, int], resize_factor: int) -> tuple[np.ndarray, np.ndarray]:
    """
    Calculates the tick marks for the Swiss road and train maps based on the maze shape and a resize factor.

    Inputs:
        maze_shape: The shape of the maze (height, width).
        resize_factor: The factor by which the maze dimensions are scaled.

    Outputs:
        x_ticks, y_ticks: Two numpy arrays representing the x and y tick marks.
    """
    x_ticks = np.arange(0, maze_shape[1] + 1) * resize_factor
    y_ticks = np.arange(0, maze_shape[0] + 1) * resize_factor
    return x_ticks, y_ticks

def show_maze_comparison(maze1: np.ndarray, maze2: np.ndarray, maze1_title: str, maze2_title: str, resize_factor: int) -> None:
    """
    Displays a side-by-side comparison of two mazes with titles and customized tick marks.

    Inputs:
        maze1: The first maze array to display.
        maze2: The second maze array to display.
        maze1_title: The title for the first maze.
        maze2_title: The title for the second maze.
        resize_factor: The factor by which the maze dimensions are scaled.
    """
    fig, axs = plt.subplots(1, 2, figsize=fig_size)

    axs[0].set_title(maze1_title)
    axs[1].set_title(maze2_title)

    # it does not matter which shape is passed to the function, since both shapes are equal
    x_ticks, y_ticks = calculate_swiss_map_ticks(maze1.shape, resize_factor) 

    mesh1 = axs[0].pcolormesh(x_ticks, y_ticks, maze1, cmap=cMap, norm=norm)
    axs[1].pcolormesh(x_ticks, y_ticks, maze2, cmap=cMap, norm=norm)

    # Layout adjustment for colorbar
    plt.subplots_adjust(bottom=0.08)
    
    # Get the position of the entire grid of subplots
    pos1 = axs[0].get_position()
    pos2 = axs[1].get_position()
    cbar_pos = [pos1.x0, 0.05, pos2.x1 - pos1.x0, 0.03]
    cbar_ax = fig.add_axes(cbar_pos)
    colorbar = fig.colorbar(mesh1, cax=cbar_ax, orientation='horizontal', ticks=[])

    for j, lab in enumerate(color_labels):
        colorbar.ax.text(j * 10, .5, lab, ha='center', va='center')
        
    # print(x_ticks, y_ticks)
    
    # invert y axis to show plot in the same way it is stored in the csv file
    for ax in axs.flat:
        ax.set_xlabel('x coordinate [km]')
        ax.set_ylabel('y coordinate [km]')
        ax.invert_yaxis()
        ax.set_aspect('equal')

    plt.show()

def show_maze(maze: np.ndarray) -> None:
    """
    Displays a single maze with a colorbar indicating different states.

    Inputs:
        maze: The maze array to display.
    """
    fig, ax = plt.subplots(1)
    mesh = ax.pcolormesh(maze, cmap=cMap, norm=norm)

    colorbar = fig.colorbar(mesh, ticks=[], orientation="horizontal")

    for j, lab in enumerate(color_labels):
        colorbar.ax.text(j * 10, .5, lab, ha='center', va='center')
    
    # invert y axis to show plot in the same way it is stored in the csv file
    fig.gca().invert_yaxis()
    fig.gca().set_aspect('equal')
    plt.show()