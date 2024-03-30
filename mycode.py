"""Vehicles Routing Problem (VRP) with Time Windows."""

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import requests
import pandas as pd
import xlsxwriter

# Set pandas display options to show all columns and rows without truncation
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)


# Read the Excel file into a pandas DataFrame
df = pd.read_excel("C:/Users/annav/OneDrive/Υπολογιστής/DATA XRONOI/data_xronoi_best_guess_ABCD.xlsx", index_col=0)
df2 = pd.read_excel("C:/Users/annav/PycharmProjects/CVRPTW_PROBLEM/timewindows.xlsx")

def create_data_model():
    """Stores the data for the problem."""
    data = {}
    data["locations"] = 79
    data["time_matrix"] = df.values.tolist()
    data["unload_times"] = df2["Unload Times"][0:data["locations"]].astype(int).tolist()
    data["earliest_arrival_time"] = df2["EAT"][0:data["locations"]].astype(int).tolist()
    data["latest_arrival_time"] = df2["LAT"][0:data["locations"]].astype(int).tolist()
    data["time_windows"] = list(zip(data["earliest_arrival_time"], data["latest_arrival_time"]))
    data["num_vehicles"] = 4
    data["depot"] = 0
    return data

# Call create_data_model function and print the result
print(create_data_model())

def print_solution(data, manager, routing, solution):

    solutionDF = pd.DataFrame(columns=['Route', 'Time', 'Google Maps Link'])
    """Prints solution on console."""
    print(f"Objective: {solution.ObjectiveValue()}")
    time_dimension = routing.GetDimensionOrDie("Time")
    total_time = 0
    dictObj = {}

    for vehicle_id in range(data["num_vehicles"]):
        dictObj = {}
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
        routeInfo = plan_output
        timeInfo = solution.Min(time_var)
        plan_output += f"Time of the route: {timeInfo}min\n"
        dictObj['Time'] = timeInfo
        dictObj['Route'] = routeInfo
        solutionDF.loc[len(solutionDF)] = dictObj
        print(plan_output)
        total_time += solution.Min(time_var)
    print(f"Total time of all routes: {total_time}min")
    writer = pd.ExcelWriter('output.xlsx', engine='xlsxwriter')

    # Get the xlsxwriter workbook and worksheet objects.
    workbook = writer.book
    firstSheetName = 'RoutingOptimization'
    solutionDF.to_excel(writer, sheet_name=firstSheetName, index=False)

    worksheet = writer.sheets[firstSheetName]

    writer.close()

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
        return data["time_matrix"][from_node][to_node] + data["unload_times"][from_node]


    transit_callback_index = routing.RegisterTransitCallback(time_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)


    # Add Time Windows constraint.
    time = "Time"
    routing.AddDimension(
        transit_callback_index,
        15,  # allow waiting time
        420,  # maximum time per vehicle
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
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.TABU_SEARCH
        )
        search_parameters.time_limit.seconds = 20

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        print_solution(data, manager, routing, solution)


if __name__ == "__main__":
    main()