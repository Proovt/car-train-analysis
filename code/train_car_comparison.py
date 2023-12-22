import numpy as np
import astar_lib
import parameters
import maze_plot
import json
import sys

from pathlib import Path
from parameters import NodePos, params_dir

ROOT = Path(sys.path[0]).parent
output_dir = ROOT.joinpath("output-data")

# determined factor to approximate the real distance
DISTANCE_SCALE_FACTOR = 1.7241

# estimated average speed for rail and car traffic
INTERCITY_TRAIN_SPEED = 140 # km/h
REGIO_TRAIN_SPEED = 80 # km/h

# assuming cars travel all at the maximum speed
HIGHWAY_CAR_SPEED = 120 # km/h
MAIN_ROAD_CAR_SPEED = 80 # km/h

# file names of csv files containing each one solvable maze
# 0 defines obstacle
# 1 (or any other value) defines a walkable node where the algorithm can pass
# includes all intercity (and interregio) train lines, which are treated as equal
intercity_rail_network_maze_file = "intercity-interregio-network.csv"
rail_network_maze_file = "railnetwork.csv"
road_maze_file = "roadnetwork.csv"
highway_maze_file = "highway-network.csv"

# parameter file name
train_car_parameter_file = "train_car_comparison.json"

# parameter city names in train_car_comparison.json
start_city_name = "start_city"
end_city_name = "end_city"

# output data attribute names
output_distance = "distance"
output_time = "time"
output_faster_network = "time efficient"
km_unit = " km"

""" data preparation """

# load in maze from csv file
def load_maze_locations(filename: str) -> dict[str, NodePos]:
    """
    Loads maze locations from a specified JSON file. Each location is mapped to a NodePos object.

    Inputs:
        filename - The name of the file containing maze location data.

    Outputs:
        cities - A dictionary mapping city names to their NodePos objects.
    """
    with open(params_dir.joinpath(filename), 'r') as f:
        params = parameters.read_params(f)

        cities = {}

        for city_dict in params:
            # get sub dictionary with City name and Position
            # https://stackoverflow.com/questions/30362391/how-do-you-find-the-first-key-in-a-dictionary
            # shortcut to get the first object tuple of dict
            city = next(iter(city_dict.items()))
            # add it to the cities dictionary as {name : Nodepos}
            cities.update({city[0] : NodePos(*city[1].values())})
        
        return cities

def check_destination(destination_name: str, cities: dict[str, NodePos]) -> NodePos:
    """
    Checks if a specified destination exists in the given cities dictionary and returns its NodePos.

    Inputs:
        destination_name - The name of the destination to check.
        cities - A dictionary containing city names and their NodePos objects.

    Outputs:
        _ - The NodePos object of the specified destination.
    """
    try:
        return cities[destination_name]
    except:
        raise KeyError(f'The destination "{destination_name}" does not exist!')

# get start and end destinations by checking their existance
def destinations(startpoint_name: str, endpoint_name: str, cities: dict[str, NodePos]) -> tuple[NodePos, NodePos]:
    """
    Retrieves start and end NodePos objects based on their names from a dictionary of cities.

    Inputs:
        startpoint_name - The name of the starting city.
        endpoint_name - The name of the ending city.
        cities - A dictionary containing city names and their NodePos objects.

    Outputs:
        start, end - A tuple containing the start and end NodePos objects.
    """
    # possible errors handled in the main file
    start = check_destination(startpoint_name, cities)
    end = check_destination(endpoint_name, cities)

    return start, end

# loads in the departure and end city
def load_destinations(filename: str, cities: dict[str, NodePos]) -> tuple[str, str, NodePos, NodePos]:
    """
    Loads start and end city destinations from a JSON file and verifies their existence in the provided cities dictionary.

    Inputs:
        filename - The name of the file containing destination data.
        cities - A dictionary of city names and their NodePos objects.

    Outputs:
        - The names of the start and end city
        - The start and end NodePos objects for the destinations.
        - Everything together as a tuple
    """
    with open(params_dir.joinpath(filename), 'r') as f:
        params = parameters.read_params(f)

        try:
            start_city = params[start_city_name]
        except:
            raise KeyError(f"The departure city {start_city_name} does not exist!")
        
        try:
            end_city = params[end_city_name]
        except:
            raise KeyError(f"The arrival city {end_city_name} does not exist!")
        
        
        return start_city, end_city, *destinations(start_city, end_city, cities)


""" output data analysis """

# function to calculate approximatively the real distance 
def real_rounded_distance_and_time(maze_distance: float, speed: float) -> tuple[int, int]:
    """
    Calculates the real rounded distance and time based on the maze distance and a given speed.

    Inputs:
        maze_distance - The distance derived from the maze.
        speed - The speed of the vehicle in km/h.

    Outputs:
        real_distance_rounded, rounded_time_mins - The real rounded distance in kilometers and time in minutes.
    """
    real_distance = maze_distance * DISTANCE_SCALE_FACTOR
    # rounded to 1 km precision
    real_distance_rounded = round(real_distance)
    
    time_in_hours = real_distance / speed
    # rounded to 1 min precision
    rounded_time_mins = round(time_in_hours * 60)

    return real_distance_rounded, rounded_time_mins

def minutes_to_hours_and_minutes(minutes: int) -> tuple[int, int]:
    """
    Converts a total number of minutes into hours and minutes.

    Inputs:
        minutes - Total number of minutes.

    Outputs:
        hours, remaining_minutes - The number of hours and remaining minutes.
    """
    hours, remaining_minutes = divmod(minutes, 60)
    return hours, remaining_minutes


def calculate_fast_route_proportion(slow_solved_maze: np.ndarray, fast_unsolved_maze: np.ndarray) -> tuple[int, int]:
    """
    Calculates the proportion of the fast route within the slow route's solution path.

    Inputs:
        slow_solved_maze - The maze with the solution path for the slower route.
        fast_unsolved_maze - The maze representing the faster route.

    Outputs:
        total_sol_nodes, fast_sol_nodes - The total number of solution nodes and the number of those nodes that are also part of the fast route.
    """
    fast_unsolved_truth_maze = fast_unsolved_maze.astype(bool)

    solution_maze = slow_solved_maze == astar_lib.SOL_PATH
    
    fast_and_solution = solution_maze & fast_unsolved_truth_maze
    
    total_sol_nodes = np.sum(solution_maze)
    fast_sol_nodes = np.sum(fast_and_solution)

    return total_sol_nodes, fast_sol_nodes


"""" simulation"""

def vehicle_analysis(start: NodePos, end: NodePos, slow_maze: np.ndarray, fast_maze: np.ndarray, slow_title: str, fast_title: str, slow_speed: float, fast_speed: float) -> tuple[str, np.ndarray, int, int, int, dict]:
    """
    Analyzes and compares two transportation networks (e.g., rail vs. car) to determine the most efficient route in terms of time. The function performs the following steps:
    1. Run the A* algorithm on both the 'slow' and 'fast' mazes, representing two different transportation networks. The 'slow' network could be, for instance, regional train lines, while the 'fast' network could represent intercity train lines or highways.
    2. Calculate the real-world distance and travel time for each network based on the distances returned by the A* algorithm and the average speed for each network.
    3. Compare the total travel time for each network and determine which one offers the shortest travel time.
    4. Print and plot the results, showing a comparison between the two networks in terms of travel time, distance, and the route taken.

    Inputs:
        start - The starting position in the maze, represented as a NodePos object.
        end - The ending position in the maze, also represented as a NodePos object.
        slow_maze - The maze representing the slower network.
        fast_maze - The maze representing the faster network.
        slow_title - The title for the slower network.
        fast_title - The title for the faster network.
        slow_speed - The average speed on the slower network.
        fast_speed - The average speed on the faster network.

    Outputs:
        faster_maze_title: str - The title of the chosen network based on time efficiency.
        solved_rail_maze: np.ndarray - The solved maze of the chosen network.
        real_distance: int - The real-world distance of the chosen path.
        hours: int - The total hours for the journey.
        minutes: int - The remaining minutes for the journey.
        data: dict - Dictionary containing information on the length and time of the chosen paths.
    """
    fast_distance, solved_fast_maze = astar_lib.py_run_astar(start, end, fast_maze)
    slow_distance, solved_slow_maze = astar_lib.py_run_astar(start, end, slow_maze)
    
    # slow maze includes fast maze
    # if no valid path found some cities were improperly configured
    if slow_distance == -1:
        raise Exception("Could not find any valid route! Please check that all cities are properly configured.")
    
    total_nodes, fast_nodes = calculate_fast_route_proportion(solved_slow_maze, fast_maze)

    distances = np.array([fast_nodes, total_nodes - fast_nodes]) / total_nodes * slow_distance

    real_slow_slow_distance, slow_time_slow_minutes = real_rounded_distance_and_time(distances[0], slow_speed)
    real_slow_fast_distance, slow_time_fast_minutes = real_rounded_distance_and_time(distances[1], fast_speed)

    real_slow_distance = real_slow_slow_distance + real_slow_fast_distance
    slow_time_minutes = slow_time_slow_minutes + slow_time_fast_minutes

    slow_hours, slow_minutes = minutes_to_hours_and_minutes(slow_time_minutes)


    # prepare output data
    data = {slow_title: {output_distance: f"{real_slow_distance}{km_unit}", output_time: f"{slow_hours}h {slow_minutes}min"}}

    # check if fast network did not find any path
    if fast_distance == -1:
        # add 1 to always make fast time bigger to force slow time to be returned
        fast_time_minutes = slow_distance + 1
        data.update({fast_title: "No valid path found"})
    else:
        # everything went smoothly, continue calculating
        real_fast_distance, fast_time_minutes = real_rounded_distance_and_time(fast_distance, fast_speed)
        fast_hours, fast_minutes = minutes_to_hours_and_minutes(fast_time_minutes)
        data.update({fast_title: {output_distance: f"{real_fast_distance}{km_unit}", output_time: f"{fast_hours}h {fast_minutes}min"}})

    # return less time consuming path
    if fast_time_minutes <= slow_time_minutes:
        real_distance = real_fast_distance
        solved_rail_maze = solved_fast_maze
        hours, minutes = fast_hours, fast_minutes
        faster_maze_title = fast_title

        maze_plot.show_maze_comparison(solved_fast_maze, solved_slow_maze, fast_title, slow_title, DISTANCE_SCALE_FACTOR)

    else:
        real_distance = real_slow_distance
        solved_rail_maze = solved_slow_maze
        hours, minutes = slow_hours, slow_minutes
        faster_maze_title = slow_title
        
    data.update({output_faster_network: [faster_maze_title]})

    return faster_maze_title, solved_rail_maze, real_distance, hours, minutes, data

def rail_analysis(start: NodePos, end: NodePos) -> tuple[str, np.ndarray, int, int, int, dict]:
    """
    Conducts an analysis of the rail network by comparing intercity and regional train lines to find the optimal route.

    Inputs:
        start - The starting position for the analysis, represented as a NodePos object.
        end - The ending position for the analysis, also represented as a NodePos object.

    Outputs:
        A tuple containing the results of the rail analysis, including the chosen network, the solved maze, the real-world distance, the time for the journey in hours and minutes, and a data dict where these values are stored.
    """
    ic_maze = astar_lib.load_maze(intercity_rail_network_maze_file)
    regio_maze = astar_lib.load_maze(rail_network_maze_file)

    return vehicle_analysis(start, end, regio_maze, ic_maze, "Regional Train Lines", "Intercity Train Lines", REGIO_TRAIN_SPEED, INTERCITY_TRAIN_SPEED)

def car_analysis(start: NodePos, end: NodePos) -> tuple[str, np.ndarray, int, int, int, dict]:
    """
    Conducts an analysis of the car network by comparing highways and main roads to find the optimal route.

    Inputs:
        start - The starting position for the analysis, represented as a NodePos object.
        end - The ending position for the analysis, also represented as a NodePos object.

    Outputs:
        A tuple containing the results of the car analysis, including the chosen network, the solved maze, the real-world distance, the time for the journey in hours and minutes, and a data dict where these values are stored.
    """
    highway_maze = astar_lib.load_maze(highway_maze_file)
    road_maze = astar_lib.load_maze(road_maze_file)

    return vehicle_analysis(start, end, road_maze, highway_maze, "Main Roads", "Highways", MAIN_ROAD_CAR_SPEED, HIGHWAY_CAR_SPEED)

"""" outputs """

def save_outputs(filename: str, data: dict) -> None:
    """
    Saves the given data as a JSON string in a file.

    Inputs:
        filename - The name of the file to save the data to.
        data - The data to be saved, provided as a dictionary.
    """
    json_string = json.dumps(data)

    with open(output_dir.joinpath(filename), 'w') as f:
        f.write(json_string)