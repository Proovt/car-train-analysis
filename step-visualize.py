import numpy as np

from printmaze import print_maze

for i in range(13):
    maze = np.genfromtxt("maze/maze-steps/maze1-" + str(i) + ".csv", delimiter=",", dtype="int16")
    print_maze(maze)