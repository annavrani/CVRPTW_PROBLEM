"""Vehicles Routing Problem (VRP) with Time Windows."""

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import requests
import pandas as pd


# Set pandas display options to show all columns and rows without truncation
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# Your DataFrame creation code

# Define your list of locations (origins and destinations)
locations = [
    "26 Anatolikis Romilias, Thessaloniki, 54454, Greece",
    "3 Kolchidos, Kalamaria, 55131, Greece",
    "2 Markou Mpotsari, Thessaloniki, 54643, Greece",
    "10 Alonnisou, Thessaloniki, 54638, Greece",
    "7 Dimokratias, Panorama, 55236, Greece",
    "30 Andrea Papandreou, Kalamaria, 55133, Greece",
    "45 Tsimiski, Thessaloniki, 54623, Greece ",
    "3 Aggelon, Pefka, 57010, Greece",
    "46 Steliou Kazantzidi, Thermi, 57001, Greece",
    "55 Egnatia, Thessaloniki, 54631, Greece",
    "15 Nikolaou Plastira, Efkarpia, 56429, Greece ",
    "10 Kolokotroni, Evosmos, 56224, Greece "
]

# API key for Distance Matrix.AI API
API_KEY = '4gjG1bO9H3SylqgStT3icoUbOdYAFfSOi4AKXmNAakoE1LRIBor5j2M7O2mq2HG2'

# Initialize an empty DataFrame for the distance matrix
distance_matrix_df = pd.DataFrame(index=locations, columns=locations)

# Iterate through all pairs of locations
for origin in locations:
    for destination in locations:
        # Make a request to the Distance Matrix.AI API to get the duration
        url = f"https://api.distancematrix.ai/maps/api/distancematrix/json?origins={origin}&destinations={destination}&key={API_KEY}"
        response = requests.get(url)
        data = response.json()

        # Parse the response and extract the duration information
        duration = None
        if 'rows' in data and len(data['rows']) > 0:
            row = data['rows'][0]
            if 'elements' in row and len(row['elements']) > 0:
                element = row['elements'][0]
                if 'duration' in element:
                    duration = element['duration']['value'] / 60  # Convert duration from seconds to minutes

        # Populate the matrix DataFrame with the extracted durations
        distance_matrix_df.at[origin, destination] = round(duration)

# Display the distance matrix DataFrame
print("Distance Matrix DataFrame:")
print(distance_matrix_df)

distance_matrix_df.to_csv('distance_matrix.csv', index=True)

def create_data_model():
    """Stores the data for the problem."""
    data = {}
    data["time_matrix"] = distance_matrix_df.values.tolist()
    data["time_windows"] = [
        (0, 100),  # Depot
        (25, 40),  # Loc1
        (25, 55),  # Loc2
        (80, 100),  # Loc3
        (0, 20),  # Loc4
        (50, 70),  # Loc5
        (30, 100),  # Loc6
        (25, 45),  # Loc7
        (35, 70),  # Loc8
        (60, 100),  # Loc9
        (0, 35),  # Loc10
        (50, 70),  # Loc11
    ]
    data["num_vehicles"] = 2
    data["depot"] = 0
    return data


def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    print(f"Objective: {solution.ObjectiveValue()}")
    time_dimension = routing.GetDimensionOrDie("Time")
    total_time = 0
    for vehicle_id in range(data["num_vehicles"]):
        index = routing.Start(vehicle_id)
        plan_output = f"Route for vehicle {vehicle_id}:\n"
        while not routing.IsEnd(index):
            time_var = time_dimension.CumulVar(index)
            plan_output += (
                f"{manager.IndexToNode(index)}"
                f" Time({solution.Min(time_var)},{solution.Max(time_var)})"
                " -> "
            )
            index = solution.Value(routing.NextVar(index))
        time_var = time_dimension.CumulVar(index)
        plan_output += (
            f"{manager.IndexToNode(index)}"
            f" Time({solution.Min(time_var)},{solution.Max(time_var)})\n"
        )
        plan_output += f"Time of the route: {solution.Min(time_var)}min\n"
        print(plan_output)
        total_time += solution.Min(time_var)
    print(f"Total time of all routes: {total_time}min")


def main():
    """Solve the VRP with time windows."""
    # Instantiate the data problem.
    data = create_data_model()

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(
        len(data["time_matrix"]), data["num_vehicles"], data["depot"]
    )

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback.
    def time_callback(from_index, to_index):
        """Returns the travel time between the two nodes."""
        # Convert from routing variable Index to time matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data["time_matrix"][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(time_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Time Windows constraint.
    time = "Time"
    routing.AddDimension(
        transit_callback_index,
        30,  # allow waiting time
        100,  # maximum time per vehicle
        False,  # Don't force start cumul to zero.
        time,
    )
    time_dimension = routing.GetDimensionOrDie(time)
    # Add time window constraints for each location except depot.
    for location_idx, time_window in enumerate(data["time_windows"]):
        if location_idx == data["depot"]:
            continue
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])
    # Add time window constraints for each vehicle start node.
    depot_idx = data["depot"]
    for vehicle_id in range(data["num_vehicles"]):
        index = routing.Start(vehicle_id)
        time_dimension.CumulVar(index).SetRange(
            data["time_windows"][depot_idx][0], data["time_windows"][depot_idx][1]
        )

    # Instantiate route start and end times to produce feasible times.
    for i in range(data["num_vehicles"]):
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.Start(i))
        )
        routing.AddVariableMinimizedByFinalizer(time_dimension.CumulVar(routing.End(i)))

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        print_solution(data, manager, routing, solution)


if __name__ == "__main__":
    main()
