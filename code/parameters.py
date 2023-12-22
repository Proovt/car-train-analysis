import sys
## https://www.w3schools.com/python/python_json.asp
import json

from pathlib import Path

## https://github.com/stakahama/sie-eng270-projectexample/blob/main/code/simulategrid.py
ROOT = Path(sys.path[0]).parent
params_dir = ROOT.joinpath("parameters")

# https://stackoverflow.com/questions/10252010/serializing-class-instance-to-json
# https://stackoverflow.com/questions/5160077/encoding-nested-python-object-in-json

# serves as abstract class to be called by JsonObjectHandler
# used to easily serialize and deserialize classes to and from JSON-files
class Jasonable():
    def jsonable(self) -> dict:
        return vars(self)

class NodePos(Jasonable):
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def get_pos(self) -> tuple[float, float]:
        return self.x, self.y

class MazeParameter(Jasonable):
    def __init__(self, maze_file: str, start_point: NodePos, end_point: NodePos) -> None:
        # find last index of '.' to extract extension
        extension_idx = maze_file.rfind('.')
        
        self.maze_name = maze_file[:extension_idx]
        self.extension = maze_file[extension_idx:]
        self.start_point = start_point
        self.end_point = end_point

# Nicholas Knight, Mar 1, 2011 at 21:00
# accessed: 10.12.2023
def JsonObjectHandler(Obj) -> dict:
    """
    Serializes a class object to a dictionary if the object is JSON serializable. It checks if the object has a 'jsonable' method to determine if it can be serialized.

    Inputs:
        Obj: The object to be serialized. The object should have a 'jsonable' method that returns a dictionary of its attributes.

    Outputs:
        _: A dictionary representation of the input object if it's JSON serializable. Raises a TypeError otherwise.
    """
    if hasattr(Obj, 'jsonable'):
        return Obj.jsonable()
    else:
        raise TypeError(f'Object of type {type(Obj)} with value of {repr(Obj)} is not JSON serializable')

def read_params(file) -> dict:
    """
    Reads a JSON file and converts it into a dictionary.

    Inputs:
        file: A file object or file path representing the JSON file to be read.

    Outputs:
        _: A dictionary representation of the JSON file contents.
    """
    return json.load(file)

def save_params(filename: str, parameters: MazeParameter) -> None:
    """
    Saves MazeParameter object data to a JSON file.

    Inputs:
        filename: A string representing the name of the file where the JSON data will be saved.
        parameters: A MazeParameter object that contains the data to be saved.
    """
    with open(params_dir.joinpath(filename), 'w') as f:
        f.write(convert_params_to_json(parameters))
        
def convert_params_to_json(parameters: MazeParameter) -> str:
    """
    Converts MazeParameter object to a JSON-formatted string.

    Inputs:
        parameters: A MazeParameter object that contains the data to be converted to JSON.

    Outputs:
        _: A string representation of the MazeParameter object in JSON format.
    """
    return json.dumps(parameters, default=JsonObjectHandler)

def load_params(filename: str) -> MazeParameter:
    """
    Loads MazeParameter data from a JSON file and converts it into a MazeParameter object.

    Inputs:
        filename: A string representing the name of the file where the JSON data is stored.

    Outputs:
        _: A MazeParameter object created from the JSON file data.
    """
    with open(params_dir.joinpath(filename), 'r') as f:
        params = read_params(f)

        for key, value in params.items():
            if isinstance(value, dict):
                params[key] = NodePos(*value.values())

        return MazeParameter(*params.values())