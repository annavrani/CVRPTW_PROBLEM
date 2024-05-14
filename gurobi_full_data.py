import gurobipy as gp
from gurobipy import *
import numpy as np
from gurobipy import GRB
import pandas as pd

df = pd.read_excel("C:/Users/annav/OneDrive/Υπολογιστής/DATA XRONOI/data_xronoi_best_guess.xlsx", index_col=0)

#NODES
n = 79
customers = [i for i in range(n) if i != 0]
nodes = [0]+customers
arcs = [(i, j) for i in nodes for j in nodes if i != j]

#TIME WINDOWS AND SERVICE TIMES
e = e = {i: 0 for i in range(n)}
values_late = [420, 300, 180, 300, 300, 300, 360, 180, 300, 300, 300, 300, 300, 300, 300, 300, 180, 300, 180, 300, 180, 300, 300, 300, 360, 300, 180, 360, 180, 300, 360, 180, 300, 300, 300, 300, 300, 300, 300, 300, 300, 360, 360, 360, 300, 300, 300, 300, 300, 300, 300, 180, 180, 180, 300, 180, 300, 300, 180, 300, 300, 360, 360, 300, 300, 300, 300, 300, 300, 180, 360, 360, 180, 360, 360, 360, 360, 360, 300]
l = {i: value_late for i, value_late in enumerate(values_late)}
values_service = [0, 4, 12, 4, 4, 4, 8, 12, 4, 4, 4, 4, 4, 4, 4, 4, 12, 4, 12, 4, 12, 4, 4, 4, 8, 4, 12, 8, 12, 4, 8, 12, 4, 4, 4, 4, 4, 4, 4, 4, 4, 8, 8, 8, 4, 4, 4, 4, 4, 4, 4, 12, 12, 12, 4, 12, 4, 4, 12, 4, 4, 8, 8, 4, 4, 4, 4, 4, 4, 12, 8, 8, 12, 8, 8, 8, 8, 8, 4]
s = {i: value_service for i, value_service in enumerate(values_service)}
#VEHICLES
vehicles = [1, 2, 3]

#DURATIONS
time_matrix = df.values.tolist()

bigM = max(s)+max(l)-max(e)
time = {(i,j): time_matrix[i][j] for i in nodes for j in nodes}

#ARCS FOR THE MODEL
arcs_var = [(i, j, k) for i in nodes for j in nodes for k in vehicles if i != j]
arcs_time = [(i, k) for i in nodes for k in vehicles]

#MODEL
model = Model('VRPTW')

#DECISION VARIABLES
x = model.addVars(arcs_var, vtype=GRB.BINARY, name='x')
t = model.addVars(arcs_time, vtype=GRB.CONTINUOUS, name='t')
#OBJECTIVE FUNCTION
model.setObjective(gp.quicksum((time[i,j]+s[i])*x[i, j, k] for i, j, k in arcs_var), GRB.MINIMIZE)

#CONSTRAINTS
#Each vehicle leaves depot 0 and arrives at the depot 0
model.addConstrs(1 == quicksum(x[0, j, k] for j in customers) for k in vehicles)
model.addConstrs(1 == quicksum(x[i, 0, k] for i in customers) for k in vehicles)

#Each customer is visited exactly ones by one vehicle
model.addConstrs(1 == quicksum(x[i, j, k] for j in nodes for k in vehicles if i != j) for i in customers)

#After arriving at a customer the vehicle leaves again
model.addConstrs(0 == quicksum(x[i, j, k] for i in nodes if i != j)-quicksum(x[j,i,k] for i in nodes if i != j)
                 for j in customers for k in vehicles)

#Time Windows
# model.addConstrs((1 == x[i, j, k]) >> (t[i, k]+s[i]+time[i, j] == t[j, k]) for i in nodes for j in customers
#                  for k in vehicles if i != j)
model.addConstrs((1 == x[i, j, k]) >> (t[i,k]+s[i]+time[i, j]-t[j, k] <= (1-x[i, j, k])*bigM) for i in nodes for j in customers
                 for k in vehicles if i!=j)
# for i,k in arcs_time:
#     t[i,k].LB = e[i]
#     t[i,k].UB = l[i]
model.addConstrs(t[i, k] >= e[i] for i, k in arcs_time)
model.addConstrs(t[i, k] <= l[i] for i, k in arcs_time)

model.Params.Threads = 4
# model.Params.TimeLimit = 60
model.Params.MIPFocus = 3
#model.Params.MIPGap = 0.1

model.optimize()

#print solution
print("Objective value: ", str((model.ObjVal)))
for v in model.getVars():
    if hasattr(v, 'X') and v.X > 0.9:
        print(str(v.VarName) + "=" + str(v.Xn))

routes = []
truck = []

K = vehicles
N = nodes

for k in vehicles:
    for i in nodes:
        if i != 0 and x[0, i, k].X > 0.9:
            aux = [0, i]
            while i != 0:
                j = i
                for h in nodes:
                    if j != h and x[j, h, k].X > 0.9:
                        aux.append(h)
                        i = h
            routes.append(aux)
            truck.append(k)
print(routes)
print(truck)

# #calculate times
time_acum = list()
for n in range(len(routes)):
    for k in range(len(routes[n])):
        if k == 0:
            aux = [0]
        else:
            i = routes[n][k-1]
            j = routes[n][k]
            travel_time = time[i,j]
            arrival_time = aux[-1] + travel_time + s[i]
            if arrival_time < e[j]:
                arrival_time = e[j]
            aux.append(arrival_time)
    time_acum.append(aux)
print(time_acum)

