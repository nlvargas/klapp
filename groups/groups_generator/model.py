from groups.groups_generator.params import *
from collections import defaultdict
from openpyxl import *
from gurobipy import *


#  Podrian no haber preferencias (caso de Desafios de la Ingenieria)
#  Los clusters siempre pueden trabajarse como un atributo mas (?)
#  Si algun input no esta en las opciones del principio se registra como nulo

def assign(params):
    print("Soy el asignador bacan")
    print(params)

    m = Model()

    #  Params
    attributes = params["attributes"]
    preferences = [p for p in params["preferences"]]
    disponibilities = []
    groups_number = params["groups_number"]
    lower_number = params["lower_number"]
    upper_number = params["upper_number"]
    attr_bounds = get_attributes_bounds(upper_number)
    attr = student_attributes(attributes)  # 1 si alumno i tiene el atributo r
    #print(attr)
    preferences_bounds = params["preferences"]
    students_preferences_number = params["students_preferences_number"]
    students = create_students(attributes, disponibilities, students_preferences_number,
                               excel_to_dict(params))
    A = count_attributes(students)
    #  Sets
    G = ["Grupo {} - (N{})".format(p, n) for p in preferences for n in range(1, groups_number + 1)]
    R = [a for a in attr_bounds]  # atributos
    I = [students[student].id for student in students]  # alumnos
    answered = [students[student].id for student in filter(lambda i: students[i].answered, students)]
    not_answered = [students[student].id for student in filter(lambda i: not students[i].answered, students)]
    G_t = defaultdict(list)  # grupos asociados al tema t
    for g in G:
        for p in preferences:
            if "Grupo {} - ".format(p) in g:
                G_t[p].append(g)

    get_students_priorities(students, G)

    #  Vars
    # variable que valga 1 si el alumno i con el alumno j tienen el mismo atributo r en el grupo g

    y = m.addVars(I, G, vtype=GRB.BINARY, name="y")  # 1 si alumno i es asignado a grupo g
    w = m.addVars(G, lb=0, ub=1, vtype=GRB.CONTINUOUS, name="w")  # =! 0 si el grupo esta activo
    z = m.addVars(I, lb=0, vtype=GRB.CONTINUOUS, name="z")  # Prioridad del alumno i
    z_max = m.addVar(vtype=GRB.CONTINUOUS, name="z_max")  # Prioridad del alumno con peor prioridad
    f = m.addVars(I, vtype=GRB.BINARY, name="f")  # 1 si el alumno i no queda en su preferencia
    Q = m.addVars(G, R, vtype=GRB.CONTINUOUS)  # N de alumnos con la caracteristica r en el grupo g
    P = m.addVars(G, R, vtype=GRB.BINARY)  # 1 si no hay alumnos con la caracteristica r en el grupo g
    F = m.addVars(G, R, vtype=GRB.CONTINUOUS)
    O = m.addVars(I, I, A, G, vtype=GRB.BINARY)  # 1 si i y j son asignados a g y tienen el mismo atributo r

    m.setObjective(quicksum(students[i].flexibility * z[i] for i in I) +  # Flexibilidad
                       10000 * z_max +  # Peor preferencia
                       10000 * quicksum(f[i] for i in I) + # Alguna preferencia
                       100 * quicksum(O[i, j, r, g] for i in I for j in I for r in A for g in G),  # Diversidad
                   GRB.MINIMIZE)

    # Constrains
    m.addConstrs((z[i] == quicksum(y[i, g] * students[i].priority[g] for g in G) for i in I),
                 name="Prioridad obtenida por el alumno")

    m.addConstrs((z_max >= z[i] for i in I),
                 name="Definicion z_max")

    m.addConstrs((quicksum(y[i, g] for g in G) == 1 for i in I),
                 name="Todos los alumnos deben ser asignados a un grupo")

    m.addConstrs((w[g] >= y[i, g] for i in I for g in G),
                 name="Un grupo esta activo si hay al menos un alumno asignado a ese grupo")

    m.addConstr((quicksum(w[g] for g in G) == groups_number),
                name="Numero total de grupos")

    m.addConstrs((lower_number * w[g] <= quicksum(y[(i, g)] for i in I) for g in G),
                 name="Numero minimo de alumnos por grupo")

    m.addConstrs((quicksum(y[i, g] for i in I) <= upper_number * w[g] for g in G),
                 name="Numero maximo de alumnos por grupo")

    # f[i] vale 1 si el alumno i no queda en ninguna preferencia
    m.addConstrs((1 - quicksum(y[i, g] for g in groups_prefered(students[i], G)
                               if len(students[i].preferences) > 0) <= f[i] for i in answered),
                 name="f vale 1 si el alumno no queda en ninguna preferencia")
    # m.addConstrs(quicksum(y[i, g] for g in groups_prefered(students[i], G)) == 1 for i in I)


    m.addConstrs((quicksum(y[i, g] for i in not_answered) <= 1 for g in G),
                 name="No puede haber mas de uno que no contesta por grupo")
    for r in A:
        if r not in attr_bounds:
            for i in I:
                for j in I:
                    if i != j:
                        m.addConstrs((attr[i][r] * y[i, g] + attr[j][r] <= O[i, j, r, g] + 1 for g in G),
                                     name="Activar variable de diversidad")

    for r in R:
        if not attr_bounds[r]["solo"]:
            m.addConstrs(
                (attr_bounds[r]["min"] * w[g] <= quicksum(y[i, g] * attr[i][r] for i in I) for g in G),
                name="Numero minimo de alumnos con atributo r por grupo")

            m.addConstrs(
                (attr_bounds[r]["max"] * w[g] >= quicksum(y[i, g] * attr[i][r] for i in I) for g in G),
                name="Numero maximo de alumnos con atributo r por grupo")
        else:
            # Numero minimo y maximo de alumnos con atributo r por grupo (disyuntivo)
            m.addConstrs(attr_bounds[r]["min"] * (w[g] - P[g, r]) <= Q[g, r] for g in G)
            m.addConstrs(attr_bounds[r]["max"] * (1 - P[g, r]) >= Q[g, r] for g in G)
            m.addConstrs(Q[g, r] == quicksum(y[i, g] * attr[i][r] for i in I) for g in G)
            m.addConstrs(F[g, r] >= Q[g, r] - attr_bounds[r]["min"] for g in G)



    for preference in preferences_bounds:
        pref_groups = filter(lambda g: "Grupo {} - ".format(preference) in g, G)
        m.addConstr(quicksum(w[g] for g in pref_groups) >= preferences_bounds[preference]["min"],
                    name="Numero minimo de grupos armados con cierta preferencia")
        m.addConstr(quicksum(w[g] for g in pref_groups) <= preferences_bounds[preference]["max"],
                    name="Numero maximo de grupos armados con cierta preferencia")

    m.setParam('TimeLimit', 3 * 60)
    m.optimize()
    print(m.status)
    if m.status == 2:  # optimal
        save_results(I, G, y, students)
    if m.status == 3:  # infactible
        m.computeIIS()
        m.write("model.ilp")

    # alumnos_sin_preferencia = [i for i in I if f[i].X > 0]
    return m.status



def assign_disponibility(params):
    print("Soy el asignador")
    print(params)

    m = Model()

    #  Params
    attributes = params["attributes"]
    preferences = [p for p in params["preferences"]]
    disponibilities = params["disponibilities"] if "disponibilities" in params else []
    groups_number = params["groups_number"]
    lower_number = params["lower_number"]
    upper_number = params["upper_number"]
    cap = params["capacity"]
    attr_bounds = get_attributes_bounds(upper_number)
    attr = student_attributes(attributes) # 1 si alumno i tiene el atributo r
    preferences_bounds = params["preferences"]
    students_preferences_number = params["students_preferences_number"]
    students = create_students(attributes, disponibilities, students_preferences_number, excel_to_dict(params))

    #  Sets
    D = [d for d in disponibilities]
    G = ["Grupo {} - {} (N{})".format(p, d, n)  # grupos posibles
             for p in preferences for d in disponibilities for n in range(1, groups_number + 1)]
    R = [a for a in attr_bounds]  # atributos
    I = [students[student].id for student in students]  # alumnos
    answered = [students[student].id for student in filter(lambda i: students[i].answered, students)]
    not_answered = [students[student].id for student in filter(lambda i: not students[i].answered, students)]
    G_t = defaultdict(list)  # grupos asociados al tema t
    G_d = defaultdict(list)  # grupos asociados al dia/seccion d
    for g in G:
        for p in preferences:
            if "Grupo {} - ".format(p) in g:
                G_t[p].append(g)

        for d in D:
            if " - {} (N".format(d) in g:
                G_d[d].append(g)

    get_students_priorities(students, G)


    #  Vars
    y = m.addVars(I, G, vtype=GRB.BINARY, name="y")  # 1 si alumno i es asignado a grupo g
    w = m.addVars(G, lb=0, ub=1, vtype=GRB.CONTINUOUS, name="w")  # =! 0 si el grupo esta activo (por que no es binaria?)
    z = m.addVars(I, lb=0, vtype=GRB.CONTINUOUS, name="z")  # Prioridad del alumno i
    z_max = m.addVar(vtype=GRB.CONTINUOUS, name="z_max")  # Prioridad del alumno con peor prioridad
    f = m.addVars(I, vtype=GRB.BINARY, name="f")  # 1 si el alumno i no queda en su preferencia
    Q = m.addVars(G, R, vtype=GRB.CONTINUOUS)  # N de alumnos con la caracteristica r en el grupo g
    P = m.addVars(G, R, vtype=GRB.BINARY)  # 1 si no hay alumnos con la caracteristica r en el grupo g
    F = m.addVars(G, R, vtype=GRB.CONTINUOUS)
    if "clusters" in params:
        v_g = m.addVars(C, G, lb=0, ub=1, vtype=GRB.CONTINUOUS, name="V_g carrera")
        m.addConstrs((lim[c]["min"] * (w[g] - v_g[c, g]) <= quicksum(y[i, g] * students[i].cluster[c] for i in I) for g in G for c in C),
        name="Minimo de alumnos de cada cluster")
        m.setObjective(quicksum(students[i].flexibility * z[i] for i in I) +  # Flexibilidad
                       100 * quicksum(v_g[c, g] for g in G for c in C) +
                       10000 * z_max +  # Peor preferencia
                       10000 * quicksum(f[i] for i in I), GRB.MINIMIZE)  # Alguna preferencia
    else:
        m.setObjective(quicksum(students[i].flexibility * z[i] for i in I) +  # Flexibilidad
                       10000 * z_max +  # Peor preferencia
                       10000 * quicksum(f[i] for i in I), GRB.MINIMIZE)  # Alguna preferencia


    #  Constrains
    m.addConstrs((z[i] == quicksum(y[i, g] * students[i].priority[g] for g in G) for i in I),
                 name="Prioridad obtenida por el alumno")

    m.addConstrs((z_max >= z[i] for i in I),
                 name="Definicion z_max")

    m.addConstrs((quicksum(y[i, g] for g in G) == 1 for i in I),
                 name="Todos los alumnos deben ser asignados a un grupo")

    m.addConstrs((w[g] >= y[i, g] for i in I for g in G),
                 name="Un grupo esta activo si hay al menos un alumno asignado a ese grupo")

    m.addConstr((quicksum(w[g] for g in G) == groups_number),
                name="Numero total de grupos")

    m.addConstrs((lower_number * w[g] <= quicksum(y[(i, g)] for i in I) for g in G),
                 name="Numero minimo de alumnos por grupo")

    m.addConstrs((quicksum(y[i, g] for i in I) <= upper_number * w[g] for g in G),
                 name="Numero maximo de alumnos por grupo")

    for r in R:
        if not attr_bounds[r]["solo"]:
            m.addConstrs(
                (attr_bounds[r]["min"] * w[g] <= quicksum(y[i, g] * attr[i][r] for i in I) for g in G),
                name="Numero minimo de alumnos con atributo r por grupo")

            m.addConstrs(
                (attr_bounds[r]["max"] * w[g] >= quicksum(y[i, g] * attr[i][r] for i in I) for g in G),
                name="Numero maximo de alumnos con atributo r por grupo")
        else:
            # Numero minimo y maximo de alumnos con atributo r por grupo (disyuntivo)
            m.addConstrs(attr_bounds[r]["min"] * (w[g] - P[g, r]) <= Q[g, r] for g in G)
            m.addConstrs(attr_bounds[r]["max"] * (1 - P[g, r]) >= Q[g, r] for g in G)
            m.addConstrs(Q[g, r] == quicksum(y[i, g] * attr[i][r] for i in I) for g in G)
            m.addConstrs(F[g, r] >= Q[g, r] - attr_bounds[r]["min"] for g in G)

    # f[i] vale 1 si el alumno i no queda en ninguna preferencia
    m.addConstrs((1 - quicksum(y[i, g] for g in groups_prefered(students[i], G)
                  if len(students[i].preferences) > 0) <= f[i] for i in answered),
                 name="f vale 1 si el alumno no queda en ninguna preferencia")
    #m.addConstrs(quicksum(y[i, g] for g in groups_prefered(students[i], G)) == 1 for i in I)


    m.addConstrs((quicksum(y[i, g] for i in I for g in G_d[d]) <= cap[d] for d in D),
                 name="Capacidad diaria")

    m.addConstrs((quicksum(y[i, g] for g in G_d[d]) <= students[i].a[d] for i in I for d in D),
                 name="Disponibilidad estudiantes")

    m.addConstrs((quicksum(y[i, g] for i in not_answered) <= 1 for g in G),
                 name="No puede haber mas de uno que no contesta por grupo")

    m.addConstrs((lim[c]["max"] * w[g] >= quicksum(y[i, g] * students[i].cluster[c] for i in I) for g in G for c in C),
                 name="Maximo de alumnos de cada cluster")

    for preference in preferences_bounds:
        pref_groups = filter(lambda g: "Grupo {} - ".format(preference) in g, G)
        m.addConstr(quicksum(w[g] for g in pref_groups) >= preferences_bounds[preference]["min"],
                    name="Numero minimo de grupos armados con cierta preferencia")
        m.addConstr(quicksum(w[g] for g in pref_groups) <= preferences_bounds[preference]["max"],
                    name="Numero maximo de grupos armados con cierta preferencia")


    #  RESTRICCIONES ESPECIALES



    m.setParam('TimeLimit', 2*60)
    m.optimize()
    print(m.status)
    if m.status == 3:  # infactible
        m.computeIIS()
        m.write("model.ilp")


    #save_results(I, G, y, students)


    #alumnos_sin_preferencia = [i for i in I if f[i].X > 0]
    return m.status

def assign_clusters(params):
    pass


params = {
    'attributes': ['Genero', 'Extrovertido/introvertido', 'Tipo colegio', 'Comuna', 'Facultad'],
    'groups_number': 20,
    'lower_number': 4,
    'upper_number': 5,
    'students_preferences_number': 4,
    'capacity': {'Martes': 75, 'Miercoles': 25},
    'preferences': {
        '1': {'min': 0, 'max': 5},
        '2': {'min': 0, 'max': 5},
        '3': {'min': 0, 'max': 5},
        '4': {'min': 0, 'max': 5},
        '5': {'min': 0, 'max': 5}}
    }

assign_disponibility(params)
