from gurobipy import *
from parameters import params, groups, prior, flex, mujer, PUC, introvertido, ventas
from custom import myopt
from openpyxl import *


m = Model("Asignacion_SUS1000")


#  Sets
R = ["GENERO", "AREA", "COMUNA", "CARRERA", "UNI", "TIPO"]
I = [p["ALUMNO"] for p in params]
G = groups

#  Params
q_min = 9
q_max = 10

# 26 mujeres
m_min = 3
m_max = 5

#13 PUCs
PUC_max = 3

#Introvertidos
intro_min = 3

P = prior
n = flex


#  Vars
y = m.addVars(I, G, vtype=GRB.BINARY, name="Y")
w = m.addVars(G, lb=0, ub=1, vtype=GRB.CONTINUOUS, name="W")
z = m.addVars(I, lb=0, vtype=GRB.CONTINUOUS, name="Z")


#  Objective
m.setObjective(quicksum(n[i] * z[i] for i in I), GRB.MINIMIZE)


#  Constrains

# for d in D:
#     for t in T:
#         for g in G_td[(t, d)]:
#             for j in G_td[(t, d)]:
#                 if g < j:
#                     m.addConstr(quicksum(y[(i, g)] for i in I) >= quicksum(y[(i, j)] for i in I))

m.addConstrs((z[i] == quicksum(y[i, g] * P[i, g] for g in G) for i in I), name="Z_i")
m.addConstrs((quicksum(y[i, g] for g in G) == 1 for i in I))
m.addConstrs((w[g] >= y[i, g] for i in I for g in G), name="Activacion W")


m.addConstrs((q_min * w[g] <= quicksum(y[(i, g)] for i in I) for g in G), name="Minimo de alumnos")
m.addConstrs((quicksum(y[i, g] for i in I) <= q_max * w[g] for g in G), name="Maximo de alumnos")


m.addConstrs((quicksum(y[i, g] * mujer[i] for i in I) >= m_min * w[g] for g in G), name="Minimo de mujeres")
m.addConstrs((quicksum(y[i, g] * mujer[i] for i in I) <= m_max * w[g] for g in G), name="Maximo de mujeres")


m.addConstrs((quicksum(y[i, g] * PUC[i] for i in I) <= PUC_max * w[g] for g in G), name="Maximo PUCS")

m.addConstrs((quicksum(y[i, g] * introvertido[i] for i in I) >= intro_min * w[g] for g in G), name="Minimo introvertidos")

m.addConstrs((quicksum(y[i, g] * ventas[i] for i in I) <= 3 * w[g] for g in G), name="Maximo de ventas")

myopt(m)

res = []
for g in G:
    gr = [g]
    for i in I:
        if y[i, g].X != 0:
            gr.append(i)
    res.append(gr)

book = Workbook()
sheet = book.active
r = ["Grupo", "Alumno 1", "Alumno 2", "Alumno 3", "Alumno 4", "Alumno 5",
     "Alumno 6", "Alumno 7", "Alumno 8", "Alumno 9", "Alumno 10"]

sheet.append(r)
for row in res:
    if len(row) >= 2:
        sheet.append(row)

book.save('results.xlsx')
