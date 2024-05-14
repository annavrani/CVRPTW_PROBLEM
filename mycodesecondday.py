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
df = pd.read_excel("C:/Users/annav/OneDrive/Υπολογιστής/DATA XRONOI/data_xronoi_pert_2.xlsx", index_col=0)
df2 = pd.read_excel("C:/Users/annav/PycharmProjects/CVRPTW_PROBLEM/timewindows2.xlsx")
df3 = pd.read_excel("C:/Users/annav/OneDrive/Υπολογιστής/DATA XRONOI/data_distance_km_2.xlsx", index_col=0)

def create_data_model():
    """Stores the data for the problem."""
    data = {}
    data["locations"] = len(df)
    data["distance_km"] = df3.values.tolist()
    data["time_matrix"] = df.values.tolist()
    data["unload_times"] = df2["Unload Times"][0:data["locations"]].astype(int).tolist()
    data["earliest_arrival_time"] = df2["EAT"][0:data["locations"]].astype(int).tolist()
    data["latest_arrival_time"] = df2["LAT"][0:data["locations"]].astype(int).tolist()
    data["time_windows"] = list(zip(data["earliest_arrival_time"], data["latest_arrival_time"]))
    data["mass"] = [round(value, 2) for value in df2["Mass"][0:data["locations"]]]
    data["volume"] = [round(value, 2) for value in df2["Volume"][0:data["locations"]]]
    data["mass"] = df2["Mass"][0:data["locations"]].tolist()
    data["volume"] = df2["Volume"][0:data["locations"]].tolist()
    data["num_vehicles"] = 4
    data["depot"] = 0
    return data

# Call create_data_model function and print the result
print(create_data_model())

def print_solution(data, manager, routing, solution):

    solutionDF = pd.DataFrame(columns=['Route', 'Time (min)', 'Distance (km)', 'Total mass (kg)', 'Total volume (m3)'])
    """Prints solution on console."""
    print(f"Objective: {solution.ObjectiveValue()}")
    time_dimension = routing.GetDimensionOrDie("Time")
    total_time = 0

    for vehicle_id in range(data["num_vehicles"]):
        dictObj = {}
        index = routing.Start(vehicle_id)
        plan_output = f"Route for vehicle {vehicle_id+1}:\n"
        total_distance = 0.0
        total_mass = 0.0
        total_volume = 0.0
        while not routing.IsEnd(index):
            time_var = time_dimension.CumulVar(index)
            next_index = solution.Value(routing.NextVar(index))
            total_distance += data["distance_km"][manager.IndexToNode(index)][manager.IndexToNode(next_index)]
            total_mass += data["mass"][manager.IndexToNode(index)]
            total_volume += data["volume"][manager.IndexToNode(index)]
            plan_output += (
                f"{manager.IndexToNode(index)}"
                f" Time({solution.Min(time_var)},{solution.Max(time_var)})"
                " -> "
            )
            index = next_index
            total_distance_str = "{:.1f}".format(total_distance)  # Round total distance to one decimal place as a string
            total_mass_str = "{:.3f}".format(total_mass)
            total_volume_str = "{:.5f}".format(total_volume)
        time_var = time_dimension.CumulVar(index)
        plan_output += (
            f"{manager.IndexToNode(index)}"
            f" Time({solution.Min(time_var)},{solution.Max(time_var)})\n"
        )
        routeInfo = plan_output
        timeInfo = solution.Min(time_var)
        plan_output += (
            f"Time of the route: {timeInfo}min\n"
            f"Distance of the route: {total_distance_str}km\n"
            f"Total mass of load: {total_mass_str}kg\n"
            f"Total volume of load: {total_volume_str}m3\n"
        )
        dictObj['Time (min)'] = timeInfo
        dictObj['Route'] = routeInfo
        dictObj['Distance (km)'] = total_distance
        dictObj['Total mass (kg)'] = total_mass
        dictObj['Total volume (m3)'] = total_volume
        solutionDF.loc[len(solutionDF)] = dictObj
        print(plan_output)
        total_time += solution.Min(time_var)
    print(f"Total time of all routes: {total_time}min")
    writer = pd.ExcelWriter('output.xlsx', engine='xlsxwriter')
    # Print solver status regardless of whether a solution is found or not
    status = routing.status()
    status_meaning = {
        0: "ROUTING_NOT_SOLVED: Problem not solved yet.",
        1: "ROUTING_SUCCESS: Problem solved successfully.",
        2: "ROUTING_PARTIAL_SUCCESS_LOCAL_OPTIMUM_NOT_REACHED: Problem solved successfully after calling RoutingModel.Solve(), except that a local optimum has not been reached. Leaving more time would allow improving the solution.",
        3: "ROUTING_FAIL: No solution found to the problem.",
        4: "ROUTING_FAIL_TIMEOUT: Time limit reached before finding a solution.",
        5: "ROUTING_INVALID: Model, model parameters, or flags are not valid.",
        6: "ROUTING_INFEASIBLE: Problem proven to be infeasible."
    }
    print("Solver status:", status_meaning.get(status, "Unknown status"))

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
        20,  # allow waiting time
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
            routing_enums_pb2.FirstSolutionStrategy.SAVINGS
        )
        # Setting optimized solution metaheuristic.
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.TABU_SEARCH
        )
        search_parameters.time_limit.seconds = 120

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        print_solution(data, manager, routing, solution)
    else:
        print("\nNo solutions founds")


if __name__ == "__main__":
    main()
