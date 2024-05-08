import gurobipy as gp
from gurobipy import *
import numpy as np
from gurobipy import GRB

#NODES
n = 17
customers = [i for i in range(n) if i != 0]
nodes = [0]+customers
arcs = [(i, j) for i in nodes for j in nodes if i != j]

#TIME WINDOWS AND SERVICE TIMES
e = {0: 0, 1: 7, 2: 10, 3: 5, 4: 5, 5: 0, 6: 5, 7: 0, 8: 5, 9: 0, 10: 10, 11: 10, 12: 0, 13: 5, 14: 7, 15: 10, 16: 5}
l = {0:40, 1: 12, 2: 15, 3: 14, 4: 13, 5: 5, 6: 10, 7: 10, 8: 10, 9: 5, 10: 16, 11: 15, 12: 5, 13:10, 14: 12, 15: 15, 16: 15}
s = {0: 0, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1, 10: 1, 11: 1, 12: 1, 13:1, 14: 1, 15: 1, 16: 1}
#VEHICLES
vehicles = [1, 2, 3, 4]

#DURATIONS
time_matrix = [
    [0, 6, 9, 8, 7, 3, 6, 2, 3, 2, 6, 6, 4, 4, 5, 9, 7],
    [6, 0, 8, 3, 2, 6, 8, 4, 8, 8, 13, 7, 5, 8, 12, 10, 14],
    [9, 8, 0, 11, 10, 6, 3, 9, 5, 8, 4, 15, 14, 13, 9, 18, 9],
    [8, 3, 11, 0, 1, 7, 10, 6, 10, 10, 14, 6, 7, 9, 14, 6, 16],
    [7, 2, 10, 1, 0, 6, 9, 4, 8, 9, 13, 4, 6, 8, 12, 8, 14],
    [3, 6, 6, 7, 6, 0, 2, 3, 2, 2, 7, 9, 7, 7, 6, 12, 8],
    [6, 8, 3, 10, 9, 2, 0, 6, 2, 5, 4, 12, 10, 10, 6, 15, 5],
    [2, 4, 9, 6, 4, 3, 6, 0, 4, 4, 8, 5, 4, 3, 7, 8, 10],
    [3, 8, 5, 10, 8, 2, 2, 4, 0, 3, 4, 9, 8, 7, 3, 13, 6],
    [2, 8, 8, 10, 9, 2, 5, 4, 3, 0, 4, 6, 5, 4, 3, 9, 5],
    [6, 13, 4, 14, 13, 7, 4, 8, 4, 4, 0, 10, 9, 8, 4, 13, 4],
    [6, 7, 15, 6, 4, 9, 12, 5, 9, 6, 10, 0, 1, 3, 7, 3, 10],
    [4, 5, 14, 7, 6, 7, 10, 4, 8, 5, 9, 1, 0, 2, 6, 4, 8],
    [4, 8, 13, 9, 8, 7, 10, 3, 7, 4, 8, 3, 2, 0, 4, 5, 6],
    [5, 12, 9, 14, 12, 6, 6, 7, 3, 3, 4, 7, 6, 4, 0, 9, 2],
    [9, 10, 18, 6, 8, 12, 15, 8, 13, 9, 13, 3, 4, 5, 9, 0, 9],
    [7, 14, 9, 16, 14, 8, 5, 10, 6, 5, 4, 10, 8, 6, 2, 9, 0]
]

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


#model.Params.TimeLimit = 60
#model.Params.MIPGap = 0.1

model.optimize()

#print solution
print("Objective value: ", str((model.ObjVal)))
for v in model.getVars():
    if v.X >0.9:
        print(str(v.VarName)+"="+str(v.X))

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

