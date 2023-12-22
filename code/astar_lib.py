import numpy as np
import sys
from parameters import NodePos

#https://stakahama.gitlab.io/sie-eng270/C_intro.html#org363ad48
from ctypes import c_int, c_float, Structure, CDLL, POINTER, pointer

from os.path import exists
from pathlib import Path

# constants defined for each state the algorithm can define
OBSTACLE = 0
WALKABLE = 10
BORDER = 20
VISITED = 30
SOL_PATH = 40

# directory and library names 
ROOT = Path(sys.path[0]).parent
LIB_NAME = "a-star"

code_dir = ROOT.joinpath("code")
maze_dir = ROOT.joinpath("maze")

# global variable to store the function
run_astar = None

""" define useful structs used to pass to the C program """

class Pos(Structure):
    """
    Represents a 2D position or coordinate in a grid or maze.

    Attributes:
        x (c_int): The x-coordinate in the grid.
        y (c_int): The y-coordinate in the grid.
    """
    _fields_ = [
        ('x', c_int),
        ('y', c_int)
    ]

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

class Cost(Structure):
    """
    Encapsulates the costs associated with a node in pathfinding algorithms.

    Attributes:
        G_cost (c_int): The movement cost from the start node to the current node.
        H_cost (c_int): The estimated movement cost from the current node to the end node (heuristic).
        F_cost (c_int): The total cost (F = G + H).
    """
    _fields_ = [
        ('G_cost', c_int),
        ('H_cost', c_int),
        ('F_cost', c_int)
    ]

class Node(Structure):
    """
    Represents a node in a pathfinding graph.

    Attributes:
        parent (Node): A pointer to the parent node in the path.
        pos (Pos): The position of the node in the graph.
        cost (Cost): The costs associated with the node.
        walkState (c_int): The current state of the node (e.g., UNREACHABLE, WALKABLE).
    """
    def __init__(self, x: int, y: int, walkState: int) -> None:
        """
        Initializes a new Node instance.

        Inputs:
            x: The x-coordinate of the node.
            y: The y-coordinate of the node.
            walkState: The walkability state of the node.
        """
        self.pos = Pos(x, y)
        self.walkState = walkState

# creates the associated fields for the Node class
Node._fields_ = [
        ('parent', POINTER(Node)),
        ('pos', Pos),
        ('cost', Cost),
        ('walkState', c_int)
    ]

def load_maze(filename: str) -> np.ndarray:
    """
    Loads a maze from a CSV file, which is a file containing 0's and 1's.
    Converts obstacles to 0 and walkable paths to WALKABLE constant.

    Inputs:
        filename: str - The name of the CSV file to load the maze from.
    
    Outputs:
        _: A numpy array representing the maze, with obstacles as 0 and walkable paths as WALKABLE.
    """
    maze = np.genfromtxt(maze_dir.joinpath(filename), delimiter=",", dtype="uint0")
    return (maze != OBSTACLE) * WALKABLE

def is_in_bounds(pos: NodePos, maze: np.ndarray) -> bool:
    """
    Checks if the given position is within the bounds of the maze.

    Inputs:
        pos: NodePos - The position to check.
        maze: np.ndarray - The maze array to check against.

    Outputs:
        _: True if the position is within the maze bounds, False otherwise.
    """
    return 0 <= pos.y < maze.shape[0] and 0 <= pos.x < maze.shape[1]

def is_walkable(pos: NodePos, maze: np.ndarray) -> bool:
    return maze[pos.y, pos.x] != 0

def check_node(pos: NodePos, pos_name: str, maze: np.ndarray) -> bool:
    """
    Checks if the given position in the maze is walkable (not an obstacle).

    Inputs:
        pos: NodePos - The position to check.
        maze: np.ndarray - The maze array to check against.

    Outputs:
        _: True if the position is walkable, False otherwise.
    """
    if not is_in_bounds(pos, maze):
        # valid positions are between 0 and the size of the dimension - 1 because of 0 index
        raise IndexError(f"The {pos_name} node at x={pos.x}, y={pos.y} has to be inside of x=[0,{maze.shape[1] - 1}] y=[0,{maze.shape[0] - 1}]!")

    if not is_walkable(pos, maze):
        # The algorithm skips all nodes that are obstacles
        raise Exception(f"The {pos_name} node at x={pos.x}, y={pos.y} cannot be an obstacle!")
    return True

# checks the start and end node to be in the bounds of the maze and that they are not obstacles
def check_nodes(start: NodePos, end: NodePos, maze: np.ndarray) -> None:
    """
    Checks if the given position is within the bounds of the maze and not an obstacle.
    Does nothing when the position is valid, raises an exception otherwise.

    Inputs:
        pos: NodePos - The position to check.
        pos_name: str - The name of the position (for error messages).
        maze: np.ndarray - The maze array to check against.
    """
    check_node(start, "Start", maze)
    check_node(end, "End", maze)

def createNodes(maze: np.ndarray):
    """
    Creates a contiguous array of Node structures based on the maze array.

    Inputs:
        maze: np.ndarray - The maze array to convert into nodes.

    Outputs:
        A contiguous array of Node structures corresponding to the maze layout.
    """
    x_dim = maze.shape[1]
    y_dim = maze.shape[0]
    n = maze.size

    nodes = (Node * n)()

    for i in range(y_dim):
        for j in range(x_dim):
            nodes[i * x_dim + j] = Node(j, i, maze[i, j])

    return nodes

def mazeFromNodes(nodes, shape) -> np.ndarray:
    """
    Constructs a numpy array maze from a contiguous array of Node structures.

    Inputs:
        nodes - A contiguous array of Node structures.
        shape - The shape of the output numpy array.

    Outputs:
        np.ndarray: A numpy array representing the maze with updated node states.
    """
    maze = np.full(shape, np.nan)

    for i in range(len(nodes)):
        x = nodes[i].pos.x
        y = nodes[i].pos.y
        walkState = nodes[i].walkState
        maze[y, x] = walkState
    return maze

# function to initialize the shared library from the C code
def load_library():
    """
    Loads the A* algorithm library and sets up the 'run_astar' function pointer. The function dynamically loads the compiled C library and configures the argument and return types for the 'run_astar' function.

    Raises:
        FileNotFoundError: If the library file does not exist.
    """
    # modify global variable
    global run_astar

    # for UNIX users
    # lib_path = ROOT.joinpath(LIB_NAME + ".so")
    lib_path = code_dir.joinpath(LIB_NAME + ".dll")

    if(not exists(lib_path)):
        print(lib_path)
        raise FileNotFoundError(LIB_NAME + "-library does not exist!")

    c_lib = CDLL(str(lib_path))

    run_astar = c_lib.run_astar
    # arguments are: start position, end position, graph as array of nodes, x and y dimensions as pos struct
    run_astar.argtypes = [POINTER(Pos), POINTER(Pos), POINTER(Node), POINTER(Pos)]
    # returns distance covered
    run_astar.restype = c_float

# function to run the astar algorithm written in C
def py_run_astar(start: NodePos, end: NodePos, maze: np.ndarray) -> tuple[float, np.ndarray]:    
    """
    Executes the ``A* pathfinding algorithm`` to find the shortest path through a given maze from a start point to an end point. This function is a Python wrapper that calls the A* algorithm implemented in C. The detailed process includes:

    1. Validating the library: Ensures that the C library containing the A* algorithm is correctly loaded. If not, it raises an error.
    2. Validating nodes: Checks if the start and end points are within the bounds of the maze and are not positioned on obstacles.
    3. Preparing inputs: Converts the start and end positions to the appropriate C data types and structures required by the C implementation.
    4. Executing A* algorithm: Calls the A* algorithm function from the C library, passing the converted start and end positions, the maze, and its dimensions.
    5. Error handling: Checks for potential errors during the algorithm's execution, such as memory allocation failures or absence of a valid path.
    6. Interpreting results: Converts the output from the C function into a format usable in Python, namely the total distance of the path found and the maze array with the path marked.

    Inputs:
        start - The starting position for the A* algorithm.
        end - The ending position for the A* algorithm.
        maze - The maze array in which the algorithm will run.

    Outputs:
        A tuple containing the success distance and the maze array with updated node states.
    """
    if run_astar == None:
        raise ValueError("The library was not loaded correctly!")
    
    # check the nodes, that they are in the bounds 
    check_nodes(start, end, maze)
    
    # https://www.geeksforgeeks.org/using-pointers-in-python-using-ctypes/
    # https://docs.python.org/3/library/ctypes.html#ctypes-pointers
    startPos = pointer(Pos(*start.get_pos()))
    endPos = pointer(Pos(*end.get_pos()))
    dims = pointer(Pos(maze.shape[1], maze.shape[0]))

    nodes = createNodes(maze)
    success_distance = float(run_astar(startPos, endPos, nodes, dims))

    # check if distance is -1, which means there was a memory allocation error
    if(success_distance == -1):
        raise MemoryError("The memory for border nodes could not be allocated!")

    # check if distance is not 0
    if(not success_distance):
        raise Exception("No valid path found!")

    return success_distance, mazeFromNodes(nodes, maze.shape)