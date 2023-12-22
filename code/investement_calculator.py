import parameters
import numpy as np
import matplotlib.pyplot as plt

from math import ceil

rates_comparison_file = "rates_per_vehicle.json"

rate_suffix = " per km"
unit_suffix = " unit"

# vehicles subdict of rates
car_vehicles = "car"
train_vehicles = "train"

# plot parameters
fig_size = (8, 6)
gap_space = .5
title_font_size = 14
subtitle_font_size = 11
text_font_size = 8
bar_width = 0.5

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
        vehicle_rates - A nested dictionary containing rates for each vehicle type and category.
        rate_units - A dictionary containing the unit for each rate type.
     """
    return {vehicle_type : {rate_key.replace(rate_suffix, '') : rate * distance for rate_key, rate in vehicle_rates.items()} for vehicle_type, vehicle_rates in rates[vehicle].items()}

def plot_bar_char(data_dict: dict[str, dict[str, int]], vehicle_units: dict[str, str]):
    """
    Plots a bar chart for each rate type across different vehicle types using the provided data.

    Inputs:
        data_dict - A dictionary containing the calculated rates for each vehicle type.
        vehicle_units - A dictionary containing the units for each rate type.
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

    plots_per_line = ceil(calculated_rates_len / 2)
    fig, axs = plt.subplots(2, plots_per_line, figsize=fig_size)
    
    # https://stackoverflow.com/questions/6541123/improve-subplot-size-spacing-with-many-subplots
    fig.subplots_adjust(hspace=gap_space, wspace=gap_space)

    for i in range(calculated_rates_len):
        cur_ax = axs[i//plots_per_line, i%plots_per_line] if len(axs.shape) > 1 else axs[i]
        current_calculated_values = calculated_rates[calculated_rates_names[i]]
        
        cur_ax.set_xlabel('Vehicle Type', fontsize=subtitle_font_size)
        # y label displays units
        cur_ax.set_ylabel(vehicle_units[calculated_rates_names[i] + unit_suffix])
        cur_ax.set_xticks(pos, vehicle_types, fontsize=text_font_size)
        cur_ax.set_title(calculated_rates_names[i], fontsize=title_font_size)

        for j, val in enumerate(current_calculated_values):
            cur_ax.bar(pos[j], val, bar_width)
        
    plt.show()

def calculate_rates(vehicle_rates: dict[str, dict[str, dict[str, float]]], train_distance: int, car_distance: int) -> dict[str, dict[str, float]]:
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
    total_calculated_rates = calculate_for_distance(train_distance, vehicle_rates, train_vehicles)
    car_calculated_rates = calculate_for_distance(car_distance, vehicle_rates, car_vehicles)

    total_calculated_rates.update(car_calculated_rates)

    return total_calculated_rates

# test functionality
if __name__ == '__main__':
    vehicle_rates, vehicle_units = load_vehicle_rates_and_units()
    dst = 346
    a = calculate_for_distance(dst, vehicle_rates, train_vehicles)
    b = calculate_for_distance(dst, vehicle_rates, car_vehicles)
    a.update(b)

    plot_bar_char(a, vehicle_units)