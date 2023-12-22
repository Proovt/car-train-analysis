import sys

from typing import Callable

class Mode():
    """
    Represents a mode of operation in a command-line interface application. Each mode encapsulates a specific functionality.
    The modes implemented at the moment are: Maze Solver, Car Train Comparison and Image to Maze Conversion.

    Attributes:
        title (str): The title of the mode.
        description (str): A brief description of the mode's functionality.
        run_function (Callable[[], None]): A callable function associated with this mode, executed when the mode is selected.

    Methods:
        __init__: Initializes a new instance of Mode.
    """
    def __init__(self, title: str, description: str, run_function: Callable[[], None]) -> None:
        """
        Initializes a new Mode instance.

        Inputs:
            title: The title of the mode.
            description: A brief description of what the mode does.
            run_function: A callable function to execute when this mode is selected.
        """
        self.title = title
        self.description = description
        self.run_function = run_function

def prepare_input(exit_idx: int, inputMsg: str = "") -> int:
    """
    Prompts the user for input and ensures it is a valid integer within a specified range.

    Inputs:
        exit_idx - The upper bound of the valid input range (inclusive).
        inputMsg - An optional message to display when prompting for input.

    Outputs:
        The user's input as an integer if it is within the range [0, exit_idx]; otherwise, prompts again.
    """
    try:
        inp = int(input(inputMsg))
    except:
        return prepare_input(exit_idx, f"Please enter a valid input [0, {exit_idx}]: ")
    
    if inp < 0 or inp > exit_idx:
        return prepare_input(exit_idx, f"Please enter a valid input [0, {exit_idx}]: ")

    return inp

def run(modes: list[Mode]):
    """
    Runs a CLI (Command Line Interface) that allows users to choose from different modes. Each mode is associated with a specific function.

    Inputs:
        modes - A list of Mode instances, each representing a different functionality the user can select.

    Notes:
        - The function prints all mode options and prompts the user to select one.
        - Selecting 'Exit Program' will terminate the application.
        - Upon selecting a mode, the associated function is executed.
    """
    exit_idx = len(modes)

    print(" === Please choose among the following modes ===")
    for i, mode in enumerate(modes):
        print(f" - {i}: {mode.title}")
        print(mode.description)
        print()
    print(f" - {exit_idx}: Exit Program")

    print()
    selcted_mode = prepare_input(exit_idx, "Please enter the index of one of the modes: ")
    print()

    if selcted_mode == exit_idx:
        sys.exit()
    
    modes[selcted_mode].run_function()