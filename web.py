from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import pandas as pd
import time
import tkinter as tk


class IORedirector(object):
    def __init__(self, text_area):
        self.text_area = text_area

class StdoutRedirector(IORedirector):
    def write(self, str):
        self.text_area.insert(tk.END, str)
        self.text_area.see(tk.END)

def create_data_model():
    df = pd.read_excel(r'C:\Users\adria\Desktop\skuska\matica_PO.xlsx')
    df_demand = pd.read_excel(r'C:\Users\adria\Desktop\skuska\matica_PO.xlsx', sheet_name='order')
    df_cap = pd.read_excel(r'C:\Users\adria\Desktop\skuska\matica_PO.xlsx', sheet_name='capacities')
    #df_veh = pd.read_excel(r'C:\Users\adria\Desktop\skuska\matica_PO.xlsx', sheet_name='veh')
# Drop the first column
    df = df.drop(df.columns[0], axis=1)
    df_demand = df_demand.drop(df_demand.columns[0], axis=1)
    df_cap = df_cap.drop(df_cap.columns[0], axis=1)
    """Stores the data for the problem."""
    data = {}
    data['distance_matrix'] = df.astype(int).values.tolist()
    data['demands'] = df_demand.iloc[:, 0].tolist()
    data['vehicle_capacities'] = df_cap.iloc[:, 0].tolist()
    data['num_vehicles'] = 2
    data['depot'] = 0
    return data

def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    max_route_distance = 0
    total_distance=0
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_distance = 0
        while not routing.IsEnd(index):
            plan_output += '{}->'.format(manager.IndexToNode(index))
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
        plan_output += '{}\n'.format(manager.IndexToNode(index))
        plan_output += 'Distance of the route: {}\n'.format(route_distance)
        print(plan_output)
        max_route_distance = max(route_distance, max_route_distance)
        total_distance +=(route_distance)
    print('Maximum of the route distances: {}'.format(max_route_distance))
    print('Distance of all roads: {}'.format(total_distance))
    print("Time taken: ", time.time() - start_time, "seconds")
    

def main():
    """Solve the CVRP problem."""
    # Instantiate the data problem.
    data = create_data_model()

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback.
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        return data['distance_matrix'][manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Capacity constraint.
    def demand_callback(from_index):
        """Returns the demand of the node."""
        return data['demands'][manager.IndexToNode(from_index)]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data['vehicle_capacities'],  # vehicle maximum capacities
        True,  # start cumul to zero
        'Capacity')

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
#    search_parameters.first_solution_strategy = (
#        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.SAVINGS)

#    search_parameters.local_search_metaheuristic = (
#       routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.FromSeconds(1)
    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        print_solution(data, manager, routing, solution)

if __name__ == '__main__':
    start_time = time.time()
    main()