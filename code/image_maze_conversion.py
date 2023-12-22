import sys
import numpy as np

from os.path import exists
from pathlib import Path
from PIL import Image

ROOT = Path(sys.path[0]).parent
maze_path = ROOT.joinpath('maze')

def get_csv_name(img_name: str) -> str:
    """
    Generates a CSV file name by replacing the extension of an image file name with '.csv'.

    Inputs:
        img_name - The name of the image file.

    Outputs:
        csv_name - The corresponding CSV file name.
    """
    img_name = img_name
    # find last index of '.' to extract extension
    extension_idx = img_name.rfind('.')
    csv_name = img_name[:extension_idx] + ".csv"
    return csv_name

def convertImageToCSV(path: Path | str, shrinking_factor: float) -> None:
    """
    Converts an image to a CSV format where black pixels are represented as obstacles. The image is first resized based on the shrinking factor.

    Inputs:
        path - The path to the image file.
        shrinking_factor - The factor by which the image dimensions are shrunk.

    Raises:
        FileNotFoundError: If the specified image file does not exist.
    """
    path = ROOT.joinpath(path)

    if not exists(path):
        raise FileNotFoundError(f'The file with path "{path}" does not exist!')
    
    im = Image.open(path)
    
    resized_dimensions = np.array(im.size) // shrinking_factor
    resized_dimensions[1] = max(resized_dimensions[1], 1)

    resized_image = im.resize(resized_dimensions)
    # convert to an RGB image to check for the pixels rgb value
    rgba_im = resized_image.convert('RGB')
    rgba_arr = np.array(rgba_im)

    # https://stackoverflow.com/questions/42150110/comparing-subarrays-in-numpy
    # True when pixel is black False otherwise to determine if pixel is an obstacle
    non_black_pixels_arr = np.logical_and.reduce(rgba_arr != [0, 0, 0], axis = -1)

    # store new file as csv in /maze directory
    new_path = maze_path.joinpath(get_csv_name(path.name))
    # https://stackoverflow.com/questions/6081008/dump-a-numpy-array-into-a-csv-file
    np.savetxt(new_path, non_black_pixels_arr, delimiter=",", fmt="%0d")
    # return non_black_pixels_arr[:10, :10]


def test():
    # a = np.array([[0,0,0], [0,1,0]])
    # non_0 = (a != [0,0,0])
    # print(non_0)
    a = np.array([1, 1, 1])
    b = np.array([0,0,0])
    c = np.array([[0,0,0,0]])
    
    # https://stackoverflow.com/questions/42150110/comparing-subarrays-in-numpy
    sol = np.logical_and.reduce(c[:, :3] == b, axis = -1)
    print(sol)