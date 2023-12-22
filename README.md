
# Pathfinding Algorithm to Analyze And Compare Car and Rail Travel

An advanced suite of algorithms and tools for pathfinding, particularly focusing on mazes and transportation network analysis. This project implements the A* algorithm for maze solving and compares different travel methods (e.g., rail vs. car) to find the shortest routes and tries to approximate the most time-efficient routes.
This project was created for the university EPFL during the course Computational Methods and Tools.

## Requirements
### Python version and modules:
- Python: version 3.11.5
- numpy: version 1.26.2
- matplotlib: version 3.8.0
- pillow: version 10.0.1

### C
- gcc: version 13.2.0
- Target: x86_64-w64-mingw32 (64 bit version)

### Operating System:
- Windows 10 Home
- version: 22H2
- 64-bit operating system

## Features

- **A\* Pathfinding Implementation**: Efficiently solves mazes using the A* algorithm.
- **Transportation Network Analysis**: Compares travel times across different transportation networks, like rail and car.
- **Visualization Tools**: Includes utilities for visualizing paths and travel routes.
- **Customizable Parameters**: Allows user-defined settings for destination configurations, Price, Emissions and Energy Consumption per distance.
- **Image to Maze Conversion**: Converts black and white images to maze representations for solving.

## Installation, Compilation And Usage
- run ``git clone https://github.com/Proovt/car-train-analysis`` to 
- The C code was written on a Windows machine. Therefore the program is targetted to only windows machines and is only tested on windows machines.
- To use the program first compile the C library by navigating to the code folder ``cd code/``. Then compile the C code as a shared library: ``gcc -shared -o a-star.dll .\a-star.c``. Maybe the ``-m64`` flag is needed to force a 64-bit compilation.
- To run the code navigate back to the root folder ``cd ..`` and run the batch file using ``.\run.bat``

## Program Procedure
When the program gets run the user is greeted with a CLI to choose between 3 different 'modes' to run different parts of the program and one entry to exit the program.
- The first mode (enter: 0) is the Maze Solving Part, where the user can define the parameters in the file ``maze-parameters/maze.json``. The parameters include the filename of the maze in the ``maze/`` folder. Preferrably, use .csv files. Furthermore, you can enter a starting position and an end position from where to where the algorithm should try to find a path.
- The second mode (enter: 1) consists of the trip analysis. 
    - To change the outcome change the starting city and destination city in the file ``maze-parameters/train_car_comparison.json``. The selectable cities are defined in the file ``maze-parameters/cities.json``, which should not be changed. You can change the emission rate, energy consumption rate and price rate in the file ``maze-parameters/cities.json``, where you can change the rates for each vehicle or add new vehicles and rates. For each new rate a unit like the other per km e. g. ``kg CO2 / km`` must be provided in this file.
    - First the start and end positions are loaded in the main file, then the an analysis is called for the car network and train network with the corresponding function from the train_car_comparison module. For both a the astar algorithm written in C is called twice using the ``py_run_astar`` function of the astar_lib module to calculate the shortest path for a faster but longer highway/ intercity network and is compared to a slower main road/regional train network.
    - Those networks were taken from map.geo.admin.ch and then loaded change to csv with this program.
    - The distance calculated by the algorithm is not to scale. This was overcome by measuring the scale provided by the maps with the algorithm and determining a scaling factor which is ``DISTANCE_SCALE_FACTOR = 1.7241``.
    - The time for travelling this distance is calculated by dividing the distance by the corresponding speed. For the fast networks a constant speed is used, while the slower networks use a slower speeds on routes that are only present in the slow network, and the fast speed otherwise. This is calculated using the function ``calculate_fast_route_proportion`` which calculates the proportion of nodes of the path from start to end that are also present in the fast (unsolved) network. With this value the time of both paths can be calculated and compared. The analysis functions then returns the faster route of the both. But it plots the comparison between the fast and the slow network from left to right.
    - Back in the main module the distance and time is printed and the faster route of both train and car routes are plotted side by side from left to right.
    - The last part consists of calulating the Emissions, Price etc. described before, which is done by providing the distance travelled for the train and car routes to the investement_calculator module. The results are then plotted. In total 4 plots are shown, when selecting this mode.
- The third mode (enter: 2) is used to generate maze csv files from a black and white image, where a black pixel ((0, 0, 0) in RGB) is defined as an obstacle, where the algorithm must find a way around, and white (or any other color) defines walkable pixels. You are greeted to enter the exact path to the image starting from the root folder and a shrinking factor. This is used to reduce computation time, if no shrinking is wished enter 1. 

## Contributing
For this project it is currently not planned to consider contributions.

## Data
### DISTANCE_SCALE_FACTOR
- Determined factor to approximate the real distance calculated using the scale provided by map.geo.admin.ch.
- By measuring the scale using the algorithm and comparing to the actual 50 km the scale is set to be.
- This factor was calculated as 50 km / 29 km = 1.7241, where the 29 km are the distance from the bottom left to the bottom right corner of the 50 km scale measured by the algorithm

### Average Speeds
For the average speed, I assumed the cars always travel at the most common maximum speed[^10] which is:
- Highway: 120 km/h
- Main Road: 80 km/h
The trains vary significantly[^20]. While some InterCity (IC) trains travel at 100 km/h others travel at 200 km/h and the Gotthard tunnel even supports speeds up to 250 km/h. Therefore I settle for 140 km/h which is the average of the most common speeds.
Regional Trains (RE) vary even more. Very slow mountain climbing trains drive as slow as 35 km/h. On straigth lines they can also travel up to 120 km/h. I therefore assume an average value of 80 km/h.

### Emissions, Energy Consumption, Price Parameters
- CO2: The values for the train and EV were taken from this article[^30]. CO2 emissions for combustion cars were found here[^40].
- Energy Consumption: Tesla Model 3: 0.137 kWh/km [^70]. Skoda Octavia (Exact Model: Skoda Octavia 2019 2.0 TSI 4x4 AT): 0.076 L/km [^80] * 8.5 kWh/L (Liter benzene to kWh)[^90] = 0.646 kWh/km. The train uses between 9,8 kWh and 11,86 kWh / 100 km, I use the value 0.01 kWh / km [^100].
- Costs: 1.78 CHF/Liter benzene, cost for energy 0.27 CHF/kWh[^50]. The most sold vehicles were Skoda Octavia and Tesla Model 3 which are used for the energy consumption[^60]. Tesla: 0.27 CHF/kWh * 0.137 kWh/km = 0.037 CHF/km. Skoda: 1.78 CHF/L * 0.076 L/km = 0.135 CHF/km. The train costs are calculated using Bern to Lausanne as a reference. The train line is 97.2 km and cost 36 CHF, therefore 36 / 97.2 = 0.37 CHF/km.

## Code Source
Help with commenting and documenting was provided by ChatGPT[^1][^2].
Many little code snippets were found on stackoverflow. The links are always directly above the copied or modified code.

[^10]: https://www.ch.ch/en/vehicles-and-traffic/how-to-behave-in-road-traffic/traffic-regulations/driving-over-the-speed-limit
[^20]: https://www.openrailwaymap.org/
[^30]: https://news.sbb.ch/artikel/111186/e-auto-oder-zug-und-ist-das-e-velo-wirklich-so-nachhaltig
[^40]: https://www.bfs.admin.ch/bfs/de/home/statistiken/raum-umwelt/umweltindikatoren/alle-indikatoren/reaktionen-der-gesellschaft/co2-ausstoss-personenwagen.html
[^50]: https://www.tcs.ch/de/testberichte-ratgeber/tests/vergleich-benziner-elektroauto.php
[^60]: https://www.tcs.ch/de/testberichte-ratgeber/ratgeber/elektromobilitaet/alternativeantriebe-automarkt-schweiz.php
[^70]: https://ev-database.org/car/1991/Tesla-Model-3
[^80]: https://www.auto-abc.eu/info/real-fuel-consumption/Skoda-Octavia
[^90]: https://natural-resources.canada.ca/energy-efficiency/transportation-alternative-fuels/personal-vehicles/choosing-right-vehicle/buying-electric-vehicle/understanding-the-tables/21383
[^100]: https://www.energate-messenger.ch/news/223930/stromverbrauch-e-auto-mit-zwei-fahrgaesten-mit-bahn-vergleichbar
[^1]: https://chat.openai.com/share/27fb2015-4258-46c7-8521-c485b708c617
[^2]: https://chat.openai.com/share/2674b15d-0349-481f-9743-ba00a26bc618
