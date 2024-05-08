import gurobipy as gp
from gurobipy import *
import numpy as np
from gurobipy import GRB

#NODES
n = 10
customers = [i for i in range(n) if i != 0]
nodes = [0]+customers
arcs = [(i, j) for i in nodes for j in nodes if i != j]

#TIME WINDOWS AND SERVICE TIMES
e = {0: 0, 1: 7, 2: 10, 3: 16, 4: 10, 5: 0, 6: 5, 7: 0, 8: 5, 9: 0}
l = {0:40, 1: 12, 2: 15, 3: 18, 4: 13, 5: 5, 6: 10, 7: 4, 8: 10, 9: 3}
s = {0: 0, 1: 2, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2, 7: 2, 8: 2, 9: 2}

#VEHICLES
vehicles = [1, 2, 3]

#DURATIONS
time_matrix = [
    [0, 6, 9, 8, 7, 3, 6, 2, 3, 2],
    [6, 0, 8, 3, 2, 6, 8, 4, 8, 8],
    [9, 8, 0, 11, 10, 6, 3, 9, 5, 8],
    [8, 3, 11, 0, 1, 7, 10, 6, 10, 10],
    [7, 2, 10, 1, 0, 6, 9, 4, 8, 9],
    [3, 6, 6, 7, 6, 0, 2, 3, 2, 2],
    [6, 8, 3, 10, 9, 2, 0, 6, 2, 5],
    [2, 4, 9, 6, 4, 3, 6, 0, 4, 4],
    [3, 8, 5, 10, 8, 2, 2, 4, 0, 3],
    [2, 8, 8, 10, 9, 2, 5, 4, 3, 0]
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
model.addConstrs((1 == x[i, j, k]) >> (t[i, k]+s[i]+time[i, j] == t[j, k]) for i in customers for j in customers
                 for k in vehicles if i != j)
# model.addConstrs((1 == x[i, j, k]) >> (t[i,k]+s[i]+time[i, j]-t[j, k] <= (1-x[i, j, k])*bigM) for i in customers for j in customers
#                  for k in vehicles if i!=j)
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

