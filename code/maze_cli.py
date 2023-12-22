import sys

from typing import Callable

class Mode():
    def __init__(self, title: str, description: str, run_function: Callable[[], None]) -> None:
        self.title = title
        self.description = description
        self.run_function = run_function

def prepare_input(exit_idx: int, inputMsg: str = "") -> int:
    try:
        inp = int(input(inputMsg))
    except:
        return prepare_input(exit_idx, f"Please enter a valid input [0, {exit_idx}]: ")
    
    if inp < 0 or inp > exit_idx:
        return prepare_input(exit_idx, f"Please enter a valid input [0, {exit_idx}]: ")

    return inp

def run(modes: list[Mode]):
    exit_idx = len(modes)

    # while True:
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
    # print()