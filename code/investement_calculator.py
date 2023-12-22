import parameters
import numpy as np
import matplotlib.pyplot as plt

from math import ceil

rates_comparison_file = "rates_per_vehicle.json"

km_suffix = " km"
rate_suffix = " per" + km_suffix
unit_suffix = " unit"

# vehicles subdict of rates
car_vehicles = "car"
train_vehicles = "train"

# distance attribute to calculated rates
distance_attribute = "distance"

# plot parameters
fig_size = (12, 6)
gap_space = .5
title_font_size = 14
subtitle_font_size = 11
text_font_size = 8
bar_width = 0.5
maximum_plots_for_1_line = 3

def load_vehicle_rates_and_units() -> tuple[dict[str, dict[str, dict[str, float]]], dict[str, str]]:
    """
    Loads vehicle rates and units from a JSON file. Rates are provided per vehicle type and category, and units are specified for each rate type.

    Outputs:
        vehicle_rates - A nested dictionary containing rates for each vehicle type and category.
        rate_units - A dictionary containing the unit for each rate type.
    """
    with open(parameters.params_dir.joinpath(rates_comparison_file), 'r') as f:
        rates_and_units = parameters.read_params(f)
        vehicle_rates = {}
        rate_units = {}
        
        for key, value in rates_and_units.items():
            if key == car_vehicles or key == train_vehicles:
                vehicle_rates.update({key: value})
            else:
                rate_units.update({key: value})
        return vehicle_rates, rate_units

def calculate_for_distance(distance: int, rates: dict[str, dict[str, dict[str, float]]], vehicle: str) -> dict[str, dict[str, float]]:
    """
    Calculates for each vehicle type with a given rate per km, a value for the ``rate * distance`` covered.
    Removes the ``per km`` suffix to indicate successful calculation.
    Data is ready to be plotted.

    Inputs:
        distance: int value of the distance covered in km
        rates: nested dict with different vehicle types and their corresponding rates per km as a float.
        First key is the vehicle type sub category: train or car. It contains another dict with specific vehicle types. For each vehicle type there is a (emissions, energy, etc.) rate as a float.
        The other first keys define the unit for rate, which should not be accessed through this function.
        Has to include the same rates for each vehicle type
        vehicle types are split into train vehicles and car vehicles
        vehicle: define if rate should be calculated for trains or different car vehicles. Either 'car' or 'train'.

    Outputs:
        calculated vehicle rates - A nested dictionary containing the calculated values for the distance * rate.
     """
    return {vehicle_type : {rate_key.replace(rate_suffix, '') : rate * distance for rate_key, rate in vehicle_rates.items()} for vehicle_type, vehicle_rates in rates[vehicle].items()}

def add_distances_to_calculated_rates(train_distance: int, car_distance: int, calculated_rates_per_vehicle: dict[str, dict[str, float]], rates_per_vehicle: dict[str, dict[str, dict[str, float]]], rates_units: dict[str, str]) -> dict[str, dict[str, str]]:
    """
    Adds distances to the calculated rates for each vehicle and converts values to strings with units.

    Inputs:
        train_distance - The distance covered by train.
        car_distance - The distance covered by car.
        calculated_rates_per_vehicle - The pre-calculated rates for each vehicle.
        rates_per_vehicle - The rates for different vehicles.
        rates_units - The units for each rate type.

    Outputs:
        output_calculated_rates - A dictionary with the calculated rates and distances, formatted as strings with units.
    """
    output_calculated_rates = calculated_rates_per_vehicle.copy()

    for vehicle_type, calculated_rates in calculated_rates_per_vehicle.items():
        # convert to str and add units
        for calculated_rate_name, calculated_rate in calculated_rates.items():
            calculated_rates[calculated_rate_name] = f"{calculated_rate:.2f} {rates_units[calculated_rate_name + unit_suffix]}"

        # add distances of trip specific to vehicle 
        if vehicle_type in rates_per_vehicle[train_vehicles].keys():
            calculated_rates.update({distance_attribute: f"{train_distance}{km_suffix}"})
        elif vehicle_type in rates_per_vehicle[car_vehicles].keys():
            calculated_rates.update({distance_attribute: f"{car_distance}{km_suffix}"})

    return output_calculated_rates

def plot_bar_char(data_dict: dict[str, dict[str, int]], rate_units: dict[str, str]):
    """
    Plots a bar chart for each rate type across different vehicle types using the provided data.

    Inputs:
        data_dict - A dictionary containing the calculated rates for each vehicle type.
        rate_units  - A dictionary containing the units for each rate type.
    """
    vehicle_types = list(data_dict.keys())
    vehicle_types_len = len(vehicle_types)
    
    first_calculated_rates = next(iter(data_dict.items()))[1]
    
    calculated_rates_names = list(first_calculated_rates.keys())
    calculated_rates_len = len(calculated_rates_names)

    calculated_rates = {name : np.zeros((vehicle_types_len,1)) for name in calculated_rates_names}

    try:
        for j in range(vehicle_types_len):
            for key, value in data_dict[vehicle_types[j]].items():
                calculated_rates[key][j] = value
    except:
        raise KeyError("Not all rates contain the same amount of values!")
    
    pos = np.arange(vehicle_types_len)

    # responsive plot sizes, creates 1 line with up to maximum_plots_for_1_line plots
    # starting from maximum_plots_for_1_line + 1 plots it creates 2 lines with the according number of plots per line
    # maximum_plots_for_1_line is set to 3
    plots_per_line = ceil(calculated_rates_len / 2) if calculated_rates_len > maximum_plots_for_1_line else calculated_rates_len
    lines = 2 if calculated_rates_len > maximum_plots_for_1_line else 1
    fig, axs = plt.subplots(lines, plots_per_line, figsize=fig_size)
    
    # https://stackoverflow.com/questions/6541123/improve-subplot-size-spacing-with-many-subplots
    fig.subplots_adjust(hspace=gap_space, wspace=gap_space)

    for i in range(calculated_rates_len):
        cur_ax = axs[i//plots_per_line, i%plots_per_line] if len(axs.shape) > 1 else axs[i]
        current_calculated_values = calculated_rates[calculated_rates_names[i]]
        
        cur_ax.set_xlabel('Vehicle Type', fontsize=subtitle_font_size)
        # y label displays units
        cur_ax.set_ylabel(rate_units[calculated_rates_names[i] + unit_suffix])
        cur_ax.set_xticks(pos, vehicle_types, fontsize=text_font_size)
        cur_ax.set_title(calculated_rates_names[i], fontsize=title_font_size)

        for j, val in enumerate(current_calculated_values):
            cur_ax.bar(pos[j], val, bar_width)
        
    plt.show()

def calculate_rates(rates_per_vehicle: dict[str, dict[str, dict[str, float]]], train_distance: int, car_distance: int) -> dict[str, dict[str, float]]:
    """
    Calculates the rates for both train and car vehicles over specified distances.

    nputs:
        vehicle_rates - Nested dictionary with rates for different vehicle types.
        train_distance - The distance covered by train in kilometers.
        car_distance - The distance covered by car in kilometers.

    Outputs:
        total_calculated_rates - A dictionary containing the calculated rates for both train and car vehicles.
    """
    # calculates first for train, then gets updated to include the calculated rates for the car vehicles
    total_calculated_rates = calculate_for_distance(train_distance, rates_per_vehicle, train_vehicles)
    car_calculated_rates = calculate_for_distance(car_distance, rates_per_vehicle, car_vehicles)

    total_calculated_rates.update(car_calculated_rates)

    return total_calculated_rates