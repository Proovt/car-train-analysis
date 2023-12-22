import subprocess

from pathlib import Path
from parameters import MazeParameter

def solved_maze_path(maze_params: MazeParameter, maze_dir: Path) -> Path: 
    return maze_dir.joinpath(maze_params.maze_name + "-solved" + maze_params.extension)

def prepare_args(c_process_name: str, maze_params: MazeParameter, solved_path: Path, maze_dim, maze) -> str:

    # https://stackoverflow.com/questions/11139330/python-join-a-list-of-integers
    # convert class NodePos to tuple of strs
    start_point = map(str, maze_params.start_point.get_pos())
    end_point = map(str, maze_params.end_point.get_pos())

    # run c file with the arguments dimension of x and every value of the maze
    return [c_process_name, solved_path, *start_point, *end_point, str(maze_dim), *maze]

def run_process(args: str) -> None:
    subprocess.run(args)