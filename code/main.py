import maze_cli
import parameters as params
import astar_lib
import image_maze_conversion
import train_car_comparison as comparison
import maze_plot
import investement_calculator

from maze_cli import Mode

# json file with city locations of the corresponding networks
# rail_cities_file = "rail_cities.json"
# car_cities_file = "car_cities.json"
cities_file = "cities.json"

# parameters file for the maze solving algorithm
maze_parameter_file = "maze.json"

def print_results(network_name: str, distance: int, hours: int, minutes: int) -> None:
    """
    Prints the results of a network analysis, including the network name, distance covered, and time taken.

    Inputs:
        network_name - The name of the network (e.g., 'Train' or 'Car').
        distance - The distance covered in the network analysis in kilometers.
        hours - The number of hours taken to cover the distance.
        minutes - The additional minutes taken to cover the distance.
    """
    print(f"The shortest time was achieved using the {network_name}.")
    print(f"The covered distance was {distance} km.")
    print(f"It takes {hours} h {minutes} min to cover this distance.")

# function to run the maze solver
# parameters can be adjusted in the file "maze.json"
def run_maze_solver():
    """
    Executes the maze solving algorithm using parameters from a specified JSON file. The function loads the maze, runs the A* algorithm, and displays the solved maze.
    """
    maze_params = params.load_params(maze_parameter_file)
    maze = astar_lib.load_maze(maze_params.maze_name + maze_params.extension)
    distance, solved_maze = astar_lib.py_run_astar(maze_params.start_point, maze_params.end_point, maze)
    print(f"The covered distance was {distance}.")
    maze_plot.show_maze(solved_maze)

# function to run the car train comparison to find the least time consuming path
# parameters can be adjusted in the file "maze.json"
def run_rail_car_comparison():
    """
    Runs a comparison between rail and car travel to find the least time-consuming path. It loads city locations, analyzes both rail and car networks, prints the results, and plots a comparison chart.
    """
    cities = comparison.load_maze_locations(cities_file)
    start_name, end_name, start, end = comparison.load_destinations(comparison.train_car_parameter_file, cities)

    data = {"Start City": start_name, "End City": end_name}

    rail_title, solved_rail_maze, rail_real_distance, rail_hours, rail_minutes, rail_data = comparison.rail_analysis(start, end)
    car_title, solved_car_maze, car_real_distance, car_hours, car_minutes, car_data = comparison.car_analysis(start, end)
    
    # combine rail and car data
    data.update(rail_data)

    faster_car_route = car_data.pop(comparison.output_faster_network)
    data.update(car_data)

    # add the fast car route without overriding the fast train route
    data[comparison.output_faster_network] += faster_car_route

    print(" === Train ===")
    print_results(rail_title, rail_real_distance, rail_hours, rail_minutes)
    
    print()

    print(" === Car ===")
    print_results(car_title, car_real_distance, car_hours, car_minutes)
    
    maze_plot.show_maze_comparison(solved_rail_maze, solved_car_maze, rail_title, car_title, comparison.DISTANCE_SCALE_FACTOR)
    
    rates_per_vehicle, rates_units = investement_calculator.load_vehicle_rates_and_units()
    combined_calculated_rates = investement_calculator.calculate_rates(rates_per_vehicle, rail_real_distance, car_real_distance)

    investement_calculator.plot_bar_char(combined_calculated_rates, rates_units)
    # print(combined_calculated_rates, rates_per_vehicle, rates_units)
    output_data = investement_calculator.add_distances_to_calculated_rates(rail_real_distance, car_real_distance, combined_calculated_rates, rates_per_vehicle, rates_units)

    data.update(output_data)

    # save outputs to file
    output_filename = f"{start_name}-{end_name}_data.json"
    comparison.save_outputs(output_filename, data)

# function to run the conversion from image to csv file usable for the algorithm
def run_maze_converter():
    """
    Converts an image file to a CSV file usable for the maze-solving algorithm. It prompts the user for the path to the image and the shrinking factor, then performs the conversion.
    
    Raises:
        ValueError: If the input shrinking factor is invalid or not greater than zero.
    """
    path_from_root = input("Please enter the Path to the image from the root folder: ")
    shrinking_factor = input("Please enter the factor by which the image should be shrunken: ")

    try:
        shrinking_factor = int(shrinking_factor)
        if shrinking_factor <= 0:
            raise ValueError("Please enter a number >0!")
    except:
        raise ValueError("Please enter a valid integer shrinking factor!")
    image_maze_conversion.convertImageToCSV(path_from_root, shrinking_factor)

modes = [
    Mode("Maze Solver", "Find the Solution to A Maze defined in a csv file", run_maze_solver), 
    Mode("Train vs. Car Comparison", "Compare Path of Rail and Car Travel", run_rail_car_comparison), 
    Mode("Load Maze from Image", "Convert a black and white image to a csv file", run_maze_converter)
]

if __name__ == '__main__':
        astar_lib.load_library()
    # try:
        maze_cli.run(modes)
    # except Exception as e:
        # print(e)