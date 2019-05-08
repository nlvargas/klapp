# traducir -> rellenar -> crear matriz -> correr modelo -> crear excel
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
import numpy as np
from gurobipy import *
from custom import *
from constants import *

#Este es el código que contiene las funciones que realizan la mayoria del trabajo

#Las funciones Adapter leen el archivo y traducen de acuerdo con los diccionarios que hayan
#Fijarse que el archivo .xlsx que se ingrese solo tenga la tabla que se desee leer, si no fallara
#Actualmente le agrega disponibilidad ficticia a los alumnos
def AdapterSUS1000(dataframe, sus_encoding):
    print("Adaptando archivo ...")
    df = dataframe.copy()
    encoding_dictionary = sus_encoding

    processed_df = df.replace("Sin info", np.nan, regex=True)

    disponibilidad = [0,1,0,1,0]
    DISPONIBILIDAD = ["LUNES","MARTES","MIERCOLES","JUEVES","VIERNES"]

    for index in range(len(DISPONIBILIDAD)):
        column = DISPONIBILIDAD[index]
        processed_df["DISPONIBILIDAD_"+column]=disponibilidad[index]
        processed_df["DISPONIBILIDAD_DIAS"]=2

    for column in encoding_dictionary:
        processed_df[column] = processed_df[column].apply(lambda row: 0 if row is np.nan else encoding_dictionary[column][row])

    columns = ['Nombre:', 'Apellido', 'Rut', 'Mail UC', 'Género',
       'Tipo de establecimiento donde cursaste enseñanza media:',
       'En qué comuna vives?', '¿A qué Facultad perteneces?', 'Cluster',
       'Primera prioridad de ODS', 'Segunda prioridad de ODS',
       'Tercera prioridad de ODS', 'Cuarta prioridad de ODS', 'quinta',
       'sexta', 'septima', 'octava', 'novena', 'decima', 'onceava', 'doceava',
       'treceava', 'catorceava', 'quinceava', 'dieciseisava',
       'DISPONIBILIDAD_LUNES', 'DISPONIBILIDAD_DIAS', 'DISPONIBILIDAD_MARTES',
       'DISPONIBILIDAD_MIERCOLES', 'DISPONIBILIDAD_JUEVES',
       'DISPONIBILIDAD_VIERNES']
    selected_df = processed_df[columns]
    selected_df.index = selected_df["Rut"]

    exp_df = selected_df.copy()

    return exp_df

def AdapterING1004(dataframe, ing_encoding):
    print("Adaptando archivo .xlsx . . .")

    df = dataframe.copy()
    encoding_dictionary = ing_encoding

    processed_df = df.replace("Sin info", np.nan, regex=True)

    print(processed_df)
    #processed_df["COLEGIO TIPO"] = processed_df["COLEGIO TIPO"].replace("PARTICULAR PAGADO","PARTICULAR")

    #processed_df["COLEGIO TIPO"] = processed_df["COLEGIO TIPO"].replace("PARTICULAR FINANCIAMIENTO COMPARTIDO","PARTICULAR")
    disponibilidad = [1,0,0,0,0]
    DISPONIBILIDAD = ["LUNES","MARTES","MIERCOLES","JUEVES","VIERNES"]

    ranking = [1, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000]
    PREFERENCIA = [i for i in range(1,11)]

    for index in range(len(DISPONIBILIDAD)):
        column = DISPONIBILIDAD[index]
        processed_df["DISPONIBILIDAD_"+column]=disponibilidad[index]
        processed_df["DISPONIBILIDAD_DIAS"] = 1

    for column in encoding_dictionary:
        processed_df[column] = processed_df[column].apply(lambda row: 0 if row is np.nan else encoding_dictionary[column][row])

    cantidad_secciones = 10

    for seccion in [i+1 for i in range(0,10)]:
        processed_df["Preferencia_seccion_"+str(seccion)] = processed_df.apply(lambda row: 0 if row["Seccion"]==seccion else 1, axis=1)

    #processed_df["cluster"] = processed_df.apply(lambda row: "ing" if row["PROGRAMA"]=="INGENIERIA" else "otro", axis=1)

    selected_df = processed_df#[["SEXO","N°ALUMNO","PROGRAMA", "COLEGIO", "COLEGIO REGIÓN", "COLEGIO TIPO", "Vía Caso"]]
    selected_df.index = selected_df["N°ALUMNO"]
    exp_df=selected_df.copy()

    print(exp_df.columns)

    return exp_df

#Las funciones CreateVariables se encargan de pasar la informacion que estaba
#traducida en el .xlsx a algo que pueda trabajarse con gurobi
#Es decir, pasa de DataFrames a Diccionarios
def CreateVariablesSUS1000(dataframe):
    print("Armando parámetros...")
    data_df = dataframe.copy()

    variables = {}
    variables["SERIES"] = {
        "numero_alumno"          : data_df["Rut"],
        "genero"                 : data_df["Género"],
        "region"                 : data_df["En qué comuna vives?"],
        "tipo_colegio"           : data_df["Tipo de establecimiento donde cursaste enseñanza media:"],
        "nombre"                 : data_df["Nombre:"],
        "apellido"               : data_df["Apellido"],
        "cluster"                : data_df["Cluster"],
        "email"                  : data_df["Mail UC"],
        "disponibilidad"         : data_df["DISPONIBILIDAD_DIAS"],
        "carrera"                : data_df["¿A qué Facultad perteneces?"],
        "disponibilidad_semanal" : data_df[
                    ["DISPONIBILIDAD_LUNES", "DISPONIBILIDAD_MARTES",
                     "DISPONIBILIDAD_MIERCOLES", "DISPONIBILIDAD_JUEVES",
                     "DISPONIBILIDAD_VIERNES"]],
        "prioridad"              : data_df[["Primera prioridad de ODS","Segunda prioridad de ODS","Tercera prioridad de ODS",\
                        "Cuarta prioridad de ODS","quinta","sexta","septima","octava",\
                        "novena","decima","onceava","doceava","treceava","catorceava",\
                        "quinceava","dieciseisava"]]
    }

    variables["LISTAS"] = {
        "numero_alumno"          : [str(element) for element in data_df["Rut"].tolist()],
        "genero"                 : data_df["Género"].tolist(),
        "region"                 : data_df["En qué comuna vives?"].tolist(),
        "tipo_colegio"           : data_df["Tipo de establecimiento donde cursaste enseñanza media:"].tolist(),
        "nombre"                 : data_df["Nombre:"].tolist(),
        "apellido"               : data_df["Apellido"].tolist(),
        "cluster"                : data_df["Cluster"].tolist(),
        "email"                  : data_df["Mail UC"].tolist(),
        "disponibilidad"         : data_df["DISPONIBILIDAD_DIAS"].tolist(),
        "carrera"                : data_df["¿A qué Facultad perteneces?"].tolist(),
        "disponibilidad_semanal" : data_df[
                    ["DISPONIBILIDAD_LUNES", "DISPONIBILIDAD_MARTES",
                     "DISPONIBILIDAD_MIERCOLES", "DISPONIBILIDAD_JUEVES",
                     "DISPONIBILIDAD_VIERNES"]].values.tolist(), #dias_disp
        "prioridad"              : data_df[["Primera prioridad de ODS","Segunda prioridad de ODS","Tercera prioridad de ODS",\
                        "Cuarta prioridad de ODS","quinta","sexta","septima","octava",\
                        "novena","decima","onceava","doceava","treceava","catorceava",\
                        "quinceava","dieciseisava"]].values.tolist()
    }

    variables["DICCIONARIOS"] = {
        "genero"                  : dict(zip([str(element) for element in data_df["Rut"].tolist()], variables["LISTAS"]["genero"])),
        "region"                  : dict(zip([str(element) for element in data_df["Rut"].tolist()], variables["LISTAS"]["region"])),
        "tipo_colegio"            : dict(zip([str(element) for element in data_df["Rut"].tolist()], variables["LISTAS"]["tipo_colegio"])),
        "nombre"                  : dict(zip([str(element) for element in data_df["Rut"].tolist()], variables["LISTAS"]["nombre"])),
        "apellido"                : dict(zip([str(element) for element in data_df["Rut"].tolist()], variables["LISTAS"]["apellido"])),
        "cluster"                 : dict(zip([str(element) for element in data_df["Rut"].tolist()], variables["LISTAS"]["cluster"])),
        "email"                   : dict(zip([str(element) for element in data_df["Rut"].tolist()], variables["LISTAS"]["email"])),
        "disponibilidad"          : dict(zip([str(element) for element in data_df["Rut"].tolist()], variables["LISTAS"]["disponibilidad"])),
        "carrera"                 : dict(zip([str(element) for element in data_df["Rut"].tolist()], variables["LISTAS"]["carrera"])),
        "disponibilidad_semanal"  : dict(zip([str(element) for element in data_df["Rut"].tolist()], variables["LISTAS"]["disponibilidad_semanal"])), # aid
        "prioridad"               : dict(zip([str(element) for element in data_df["Rut"].tolist()], variables["LISTAS"]["prioridad"])),
    }

    return variables

def CreateVariablesING1004(dataframe):
    print("Armando parámetros...")
    data_df = dataframe.copy()
    variables = {}
    variables["SERIES"] = {
        "numero_alumno"   : data_df["N°ALUMNO"], #nro_a
        "genero"          : data_df["SEXO"],#gen
        "region"          : data_df["COLEGIO REGIÓN"],#reg
        "tipo_colegio"    : data_df["COLEGIO TIPO"],#tip
        "disponibilidad"  : data_df["DISPONIBILIDAD_DIAS"],#cantidad días disponibles
        "disp_semanal"    : data_df[["DISPONIBILIDAD_LUNES", "DISPONIBILIDAD_MARTES", "DISPONIBILIDAD_MIERCOLES", "DISPONIBILIDAD_JUEVES", "DISPONIBILIDAD_VIERNES"]], #disp. diaria
        "carrera"         : data_df["PROGRAMA"],#carr
        "colegio"         : data_df["COLEGIO"],#col
        "via_caso"        : data_df["Vía Caso"], #T&I
        "seccion"         : data_df["Seccion"],
        #"cluster"         : data_df["cluster"],
        "preferencias"    : data_df[["Preferencia_seccion_1", "Preferencia_seccion_2", "Preferencia_seccion_3", "Preferencia_seccion_4", "Preferencia_seccion_5", "Preferencia_seccion_6", "Preferencia_seccion_7", "Preferencia_seccion_8", "Preferencia_seccion_9", "Preferencia_seccion_10"]]

    }

    variables["LISTAS"] = {
        "numero_alumno"   : [str(element) for element in data_df["N°ALUMNO"].tolist()], #nro_a
        "genero"          : data_df["SEXO"].tolist(),#gen
        "region"          : data_df["COLEGIO REGIÓN"].tolist(),#reg
        "tipo_colegio"    : data_df["COLEGIO TIPO"].tolist(),#tip
        "disponibilidad"  : data_df["DISPONIBILIDAD_DIAS"].tolist(),#dispon
        "disp_semanal"    : data_df[["DISPONIBILIDAD_LUNES", "DISPONIBILIDAD_MARTES", "DISPONIBILIDAD_MIERCOLES", "DISPONIBILIDAD_JUEVES", "DISPONIBILIDAD_VIERNES"]].values.tolist(),
        "carrera"         : data_df["PROGRAMA"].tolist(),#carr
        "colegio"         : data_df["COLEGIO"].tolist(),#col
        "via_caso"        : data_df["Vía Caso"].tolist(),#T&I
        "seccion"         : data_df["Seccion"].tolist(),
        #"cluster"         : data_df["cluster"].tolist(),
        "preferencias"    : data_df[["Preferencia_seccion_1", "Preferencia_seccion_2", "Preferencia_seccion_3", "Preferencia_seccion_4", "Preferencia_seccion_5", "Preferencia_seccion_6", "Preferencia_seccion_7", "Preferencia_seccion_8", "Preferencia_seccion_9", "Preferencia_seccion_10"]].values.tolist()

    }

    variables["DICCIONARIOS"] = {
        "genero"          : dict(zip([str(element) for element in data_df["N°ALUMNO"].tolist()], data_df["SEXO"].tolist() )),#gen
        "region"          : dict(zip([str(element) for element in data_df["N°ALUMNO"].tolist()], data_df["COLEGIO REGIÓN"].tolist() )),#reg
        "tipo_colegio"    : dict(zip([str(element) for element in data_df["N°ALUMNO"].tolist()], data_df["COLEGIO TIPO"].tolist() )),#tip
        "disponibilidad"  : dict(zip([str(element) for element in data_df["N°ALUMNO"].tolist()], data_df["DISPONIBILIDAD_DIAS"].tolist() )),#cant. días disponibles
        "disp_semanal"    : dict(zip([str(element) for element in data_df["N°ALUMNO"].tolist()], variables["LISTAS"]["disp_semanal"] )),
        "carrera"         : dict(zip([str(element) for element in data_df["N°ALUMNO"].tolist()], data_df["PROGRAMA"].tolist() )),#carr
        "colegio"         : dict(zip([str(element) for element in data_df["N°ALUMNO"].tolist()], data_df["COLEGIO"].tolist() )),#col
        "via_caso"        : dict(zip([str(element) for element in data_df["N°ALUMNO"].tolist()], data_df["Vía Caso"].tolist() )),#T&I
        "prioridad"       : dict(zip([str(element) for element in data_df["N°ALUMNO"].tolist()], variables["LISTAS"]["preferencias"] )),
        "seccion"         : dict(zip([str(element) for element in data_df["N°ALUMNO"].tolist()], variables["LISTAS"]["seccion"] ))
        #"cluster"         : dict(zip([str(element) for element in data_df["N°ALUMNO"].tolist()], variables["LISTAS"]["cluster"] ))
    }

    return variables

#Esta funcion arma conjuntos T, D, I, G y los subsets correspondientes
def CrearConjuntos(cant_gtd, variables,curso):
    print("Armando Conjuntos...")
    I = variables["LISTAS"]["numero_alumno"]
    G = []

    if curso =="SUS1000":
        D = [1, 2, 3, 4, 5]
        T = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]

    else:
        D = [1]
        T = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]



    t_g  = tupledict() #Grupo: Tema
    G_td = tupledict()
    G_t  = tupledict()
    G_d  = tupledict()
    G_aux= tupledict()

    group  = 1
    puesto = 1
    for d in D:
        for t in T:
            for q in range(0,cant_gtd):
                nro=1+(cant_gtd*len(T))*(d-1)+q+cant_gtd*(t-1)
                G.append(group)

                G_aux[(d,t,puesto)]= group #(día, tema): grupo
                G_t[(t)] = G_aux.select('*',t) #t:[grupos]
                G_d[(d)]=G_aux.select(d,'*') #d:[grupos]

                t_g[(group)] = t #grupo:tema
                G_td[(t,d)] = G_aux.select(d,t)
                puesto +=1
                group  +=1

    conjuntos = {
    "I":I,
    "D":D,
    "T":T,
    "G":G,
    "G_td":G_td,
    "G_t" :G_t,
    "G_d" :G_d,
    "t_g" :t_g
    }

    return conjuntos

def ConjuntoCarrerasAuxiliar(cluster):
    #conjuntos de carreras similares
    agregacion_carrera=[]
    contador_cluster=[]

    for key,value in cluster.items():
        if value not in agregacion_carrera:
            agregacion_carrera.append(value)
            contador_cluster.append(0)

    for key,value in cluster.items():
        for x in range(0,len(agregacion_carrera)):
            if value==agregacion_carrera[x]:
                contador_cluster[x]+=1
    return agregacion_carrera

    print(agregacion_carrera)

#Las funciones CreateParameters se encargan de armar los parametros en base a
#los diccionarios que se armaron en CreateVariables
def CreateParametersING1004(variables,conjuntos):

    parameters = {
    "genero"       : TupleDictUnConjunto(variables["DICCIONARIOS"]["genero"],        conjuntos["I"]),
    "region"       : TupleDictUnConjunto(variables["DICCIONARIOS"]["region"],        conjuntos["I"]),
    "tipo_colegio" : TupleDictUnConjunto(variables["DICCIONARIOS"]["tipo_colegio"],  conjuntos["I"]),
    "colegio"      : TupleDictUnConjunto(variables["DICCIONARIOS"]["colegio"],       conjuntos["I"]),
    "via caso_TI"  : TupleDictUnConjunto(variables["DICCIONARIOS"]["via_caso"],      conjuntos["I"]),
    "colegio"      : TupleDictUnConjunto(variables["DICCIONARIOS"]["colegio"],       conjuntos["I"]),
    "P_it"         :TupleDictDosConjuntos(variables["DICCIONARIOS"]["prioridad"],    conjuntos["I"], conjuntos["T"]),
    "a_id"         :TupleDictDosConjuntos(variables["DICCIONARIOS"]["disp_semanal"], conjuntos["I"], conjuntos["D"]),
    "n_i"          :TupleDictUnConjunto(variables["DICCIONARIOS"]["disponibilidad"], conjuntos["I"]),
    "carrera"      :TupleDictUnConjunto(variables["DICCIONARIOS"]["carrera"],        conjuntos["I"]),
    "seccion"      :TupleDictUnConjunto(variables["DICCIONARIOS"]["seccion"],      conjuntos["I"])
    }

    c_d         = tupledict()
    capacidades = [400, 400, 400, 400]
    for d in conjuntos["D"]:
        for c in capacidades:
            c_d[(d)] = c

    P_ig = tupledict()
    for i in conjuntos["I"]:
        for g in conjuntos["G"]:
            P_ig[(i,g)]=parameters["P_it"][(i,conjuntos["t_g"][g])]

    parameters["c_d"]  = c_d
    parameters["P_ig"] = P_ig

    parameters["colegio_bin"] = tupledict()
    Colegios = ConjuntoColegios(parameters)

    for i in conjuntos["I"]:
        for c in Colegios:
            if parameters["colegio"][i] == c:
                parameters["colegio_bin"][(i,c)]=1
            else:
                parameters["colegio_bin"][(i,c)]=0

    return parameters

#Esta funcion reune el universo de colegios
def ConjuntoColegios(parameters):
    Colegios=[]
    for key,value in parameters["colegio"].items():
        if value not in Colegios:
            Colegios.append(value)
    return Colegios

#esta funcion arma parametros que se mueven en un conjunto
def TupleDictUnConjunto(diccionario, conjunto_1):
    tp_dict=tupledict()
    for i in conjunto_1:
        tp_dict[(i)]=diccionario[i]
    return tp_dict

#esta funcion arma parametros que se mueven en dos conjuntos
def TupleDictDosConjuntos(diccionario, conjunto_1, conjunto_2):
    tp_dict=tupledict()
    for i in conjunto_1:
        for j in conjunto_2:
            tp_dict[(i,j)]=diccionario[i][j-1]
    return tp_dict

def CreateParametersSUS1000(variables, conjuntos, agregacion_carrera):
    D = [1, 2, 3, 4, 5] #Dias
    T = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]

    parameters = {
    "r_ig"      :TupleDictUnConjunto(variables["DICCIONARIOS"]["genero"]      ,variables["LISTAS"]["numero_alumno"]),
    "r_ireg"    :TupleDictUnConjunto(variables["DICCIONARIOS"]["region"]      ,variables["LISTAS"]["numero_alumno"]),
    "r_icol"    :TupleDictUnConjunto(variables["DICCIONARIOS"]["tipo_colegio"],variables["LISTAS"]["numero_alumno"]),
    "r_iname"   :TupleDictUnConjunto(variables["DICCIONARIOS"]["nombre"]      ,variables["LISTAS"]["numero_alumno"]),
    "r_iape"    :TupleDictUnConjunto(variables["DICCIONARIOS"]["apellido"]    ,variables["LISTAS"]["numero_alumno"]),
    "a_id"      :TupleDictDosConjuntos(variables["DICCIONARIOS"]["disponibilidad_semanal"], variables["LISTAS"]["numero_alumno"], D),
    "n_i"       :TupleDictUnConjunto(variables["DICCIONARIOS"]["disponibilidad"]    ,variables["LISTAS"]["numero_alumno"]),
    "r_icarr"   :TupleDictUnConjunto(variables["DICCIONARIOS"]["carrera"],variables["LISTAS"]["numero_alumno"]),
    "P_it"      :TupleDictDosConjuntos(variables["DICCIONARIOS"]["prioridad"],variables["LISTAS"]["numero_alumno"],T),
    "r_imail"   :TupleDictUnConjunto(variables["DICCIONARIOS"]["email"],variables["LISTAS"]["numero_alumno"]),
    "r_cluster" :TupleDictUnConjunto(variables["DICCIONARIOS"]["cluster"],variables["LISTAS"]["numero_alumno"])
    }
    c_d         = tupledict()
    capacidades = [400, 400, 400, 400] #Cambiarlo con el .txt si no dejar este default
    for d in D:
        for c in capacidades:
            c_d[(d)] = c

    parameters["c_d"]         = c_d
    parameters["P_ig"]        = tupledict()
    parameters["Carrera_bin"] = tupledict()
    parameters["cluster_bin"] = tupledict()
    parameters["P_it"]        = tupledict()
    G = conjuntos["G"]
    I = variables["LISTAS"]["numero_alumno"]
    for i in I:
        ranking_i = variables["DICCIONARIOS"]["prioridad"][i]
        for t in T:
            if t in ranking_i:
                parameters["P_it"][(i,t)]=ranking_i.index(t)+1
            else:
                parameters["P_it"][(i,t)]=1000
    for i in I:
        for g in G:
            #print(P_it[(i,t_g[g])])
            parameters["P_ig"][(i,g)] = parameters["P_it"][(i, conjuntos["t_g"][g])]
        #aquí se arma un tupledict binario que indica si el alumno pertenece a un cluster o no
        for c in agregacion_carrera:
            if parameters["r_cluster"][i] == c:
                parameters["cluster_bin"][(i,c)]=1
            else:
                parameters["cluster_bin"][(i,c)]=0

    return parameters

#esta funcion arma los clusters a los que pertenecen los alumnos
def ArmarClusters (clusters):
    agregacion_carrera = []
    for cluster in list( clusters.values() ):
        if cluster!="":
            agregacion_carrera.append(cluster)

    return agregacion_carrera

#esta funcion ve el radio de alumnosxcluster/totalgrupos
def get_cluster_ratios(parameters):
    ratio_dict = {}
    for item in parameters["cluster_bin"]:
        if item[1] not in ratio_dict:
            ratio_dict[item[1]] = 0
        ratio_dict[item[1]] += parameters["cluster_bin"][item]

    for cluster in ratio_dict:
        ratio_dict[cluster] = ratio_dict[cluster]/ parameters["cant_grupos"]
    return(ratio_dict)

#Modelo
def CrearModeloSUS1000(variables, conjuntos, parameters, agregacion_carrera):
    print("Creando Modelo...")
    I = variables["LISTAS"]["numero_alumno"]
    D = conjuntos["D"]
    T = conjuntos["T"]
    G = conjuntos["G"]

    t_g  = conjuntos["t_g"]
    G_td = conjuntos["G_td"]
    G_t  = conjuntos["G_t"]
    G_d  = conjuntos["G_d"]

    r_ig      = parameters["r_ig"]
    r_ireg    = parameters["r_ireg"]
    r_icol    = parameters["r_icol"]
    r_icarr   = parameters["r_icarr"]
    r_cluster = parameters["r_cluster"]

    a_id = parameters["a_id"]
    n_i  = parameters["n_i"]
    c_d  = parameters["c_d"]
    P_ig = parameters["P_ig"]
    P_it = parameters["P_it"]

    cluster_bin = parameters["cluster_bin"]

    cant_grupos = parameters["cant_grupos"]

    q_min     = parameters["q_min"]
    q_max     = parameters["q_max"]

    part_min  = parameters["part_min"]
    part_max  = parameters["part_max"]
    publ_min  = parameters["publ_min"]
    publ_max  = parameters["publ_max"]

    m_min     = parameters["m_min"]
    m_max     = parameters["m_max"]
    h_min     = parameters["h_min"]
    h_max     = parameters["h_max"]

    region_min=  parameters["region_min"]

    m = Model("asignación_SUS1000")
    print("Variables...")
    x      = m.addVars(I, D, vtype=GRB.BINARY, name="X")
    y      = m.addVars(I, G, vtype=GRB.BINARY, name="Y") ###G_i
    w      = m.addVars(G, lb=0, ub=1, vtype=GRB.CONTINUOUS, name="W")
    z      = m.addVars(I, lb=0, vtype=GRB.CONTINUOUS, name="Z")
    z_max  = m.addVar( vtype=GRB.CONTINUOUS, name="Z_max")

    v_gc   = m.addVars(G, lb=0, ub=1, vtype=GRB.CONTINUOUS, name="V_g carrera")

    m.update()
    print("F.O ...")
    N = len(I)
    m.setObjective(quicksum(n_i[(i)]*z[(i)] for i in I)\
                       +100*quicksum(v_gc[(g)] for g in G for c in agregacion_carrera )\
                       +10000*z_max, GRB.MINIMIZE)

    #Restricciones
    print("Restricciones...")
    m.addConstr(quicksum(w[(g)] for g in G), GRB.LESS_EQUAL, cant_grupos)
    m.addConstrs((quicksum(y[(i,g)] for i in I for g in G_d[(d)])<=c_d[(d)] for d in D), name="Capacidad taller día d")

    for d in D:
        for t in T:
            for g in G_td[(t,d)]:
                for j in G_td[(t,d)]:
                    if g<j:
                        m.addConstr(quicksum(y[(i,g)] for i in I), GRB.GREATER_EQUAL,\
                                    quicksum(y[(i,j)] for i in I), name="Antisimetría")

    m.addConstrs((quicksum(y[(i,g)]*P_ig[(i,g)] for g in G)==z[(i)] for i in I), name="Z_i")
    m.addConstrs((quicksum(x[(i,d)] for d in D) == 1 for i in I), name="Asignación 1")
    m.addConstrs((quicksum(y[(i,g)] for g in G) == 1 for i in I), name="Asignación 2")
    m.addConstrs((z_max >= z[(i)] for i in I), name="Z_max")
    m.addConstrs((w[(g)]>=y[(i,g)] for i in I for g in G), name="Activación W")

    m.addConstrs((quicksum(y[(i,g)] for g in G_d[(d)])+x[(i,d)]<=a_id[(i,d)] for i in I for d in D), name="Asignación cátedra y taller")

    m.addConstrs((q_min*w[(g)]<=quicksum(y[(i,g)] for i in I)for g in G),name="Mínimo de alumnos")
    m.addConstrs((quicksum(y[(i,g)] for i in I)<=q_max*w[(g)] for g in G), name="Máximo de alumnos")

    m.addConstrs((quicksum(y[(i,g)]*r_ig[(i)] for i in I)>=m_min*w[(g)]for g in G), name="Mínimo de mujeres")
    m.addConstrs((quicksum(y[(i,g)]*r_ig[(i)] for i in I)<=m_max*w[(g)]for g in G), name="Máximo de mujeres")
    m.addConstrs((quicksum(y[(i,g)]*(1-r_ig[(i)]) for i in I)>= h_min*w[(g)] for g in G), name="Mínimo de hombres")
    m.addConstrs((quicksum(y[(i,g)]*(1-r_ig[(i)]) for i in I)<= h_max*w[(g)] for g in G), name="Maximo de hombres")

    m.addConstrs((quicksum(y[(i,g)]*r_icol[(i)] for i in I)>= part_min*w[(g)] for g in G), name=" Mínimo de Particulares")
    m.addConstrs((quicksum(y[(i,g)]*r_icol[(i)] for i in I)<= part_max*w[(g)] for g in G), name=" Máximo de Particulares")
    m.addConstrs((quicksum(y[(i,g)]*(1-r_icol[(i)]) for i in I)>= publ_min*w[(g)] for g in G), name=" Mínimo de Públicos")
    m.addConstrs((quicksum(y[(i,g)]*(1-r_icol[(i)]) for i in I)<= publ_max*w[(g)] for g in G), name=" Mínimo de Públicos")
    
    m.addConstrs((quicksum(y[(i,g)]*r_ireg[(i)] for i in I)<= region_min*w[(g)] for g in G), name="Mínimo Regiones")
    
    ratio_dict = get_cluster_ratios(parameters)

    for key in ratio_dict:
        if  ratio_dict[key]==int(ratio_dict[key]): #entero
            m.addConstr(
            quicksum(y[(i,g)]*parameters["cluster_bin"][(i,key)] for i in I),
            GRB.EQUAL,ratio_dict[key]*w[(g)],name = "1 por carrera_enteros")

        elif 1 < ratio_dict[key] < 1.1:
            m.addConstr(quicksum(y[(i,g)]*parameters["cluster_bin"][(i,key)] for i in I),
            GRB.LESS_EQUAL,w[(g)]+v_gc[(g)], name="1 por carrera_cercano a 1")

        elif ratio_dict[key]>1.1: # float
            lim_inf = int( ratio_dict[key] )
            lim_sup = lim_inf + 1

            m.addConstr(quicksum(y[(i,g)]*parameters["cluster_bin"][(i,key)] for i in I),GRB.LESS_EQUAL,lim_sup*w[(g)], name="1 por carrera_float mayor a 1.1")
            m.addConstr(quicksum(y[(i,g)]*parameters["cluster_bin"][(i,key)] for i in I),GRB.GREATER_EQUAL,lim_inf*w[(g)], name="1 por carrera_float mayor a 1.1")

        elif ratio_dict[key]<1:
            m.addConstr(quicksum(y[(i,g)]*parameters["cluster_bin"][(i,key)] for i in I),GRB.LESS_EQUAL,w[(g)], name="1 por carrera_menor a 1")


    myopt(m)

    return m

for j in range(7(k - 1) + 1, 7(k - 1) + 7):
m.addConstrs(quicksum(delta[t] for t in range(7(k - 1) + 1, 7(k - 1) + 7 + 1)) = 1 for k in range(1, 25))
#Modelo
def CrearModeloING1004(variables, conjuntos, parameters, parametros, Colegios):
    print("Creando Modelo...")
    I = variables["LISTAS"]["numero_alumno"]

    ID = tupledict()
    contador =1
    for i in I:
        ID[(i)]=contador
        contador+=1


    t_g = conjuntos["t_g"]

    D    = conjuntos["D"]
    T    = conjuntos["T"]
    G    = conjuntos["G"]
    G_td = conjuntos["G_td"]
    G_t  = conjuntos["G_t"]
    G_d  = conjuntos["G_d"]

    c_d  = parameters["c_d"]

    r_ig    = parameters["genero"]
    r_ireg  = parameters["region"]
    r_icol  = parameters["tipo_colegio"]
    a_id    = parameters["a_id"]
    n_i     = parameters["n_i"]
    r_icarr = parameters["carrera"]
    r_iTI   = parameters["via caso_TI"]
    P_it    = parameters["P_it"]

    P_ig = parameters["P_ig"]
    P_it = parameters["P_it"]

    colegio_bin = parameters["colegio_bin"]
    Colegios    = ConjuntoColegios(parameters)

    cant_grupos = parametros["cant_grupos"]

    q_min     = parametros["q_min"]
    q_max     = parametros["q_max"]

    part_min  = parametros["part_min"]
    part_max  = parametros["part_max"]
    publ_min  = parametros["publ_min"]
    publ_max  = parametros["publ_max"]

    m_min     = parametros["m_min"]
    m_max     = parametros["m_max"]
    h_min     = parametros["h_min"]
    h_max     = parametros["h_max"]

    region_min= parametros["region_min"]
    region_max= parametros["region_max"]

    TI_min    = parametros["TI_min"]
    TI_max    = parametros["TI_max"]

    M = 1000

    m = Model("asignación_ING1004")

    print("Variables. . .")
    y      = m.addVars(I, G, vtype=GRB.BINARY, name="Y") ###G_i
    w      = m.addVars(G, vtype=GRB.BINARY, name="W")
    z      = m.addVars(I, lb=0, vtype=GRB.CONTINUOUS, name="Z")

    #F_grupo   = m.addVars(G, lb=0,vtype=GRB.CONTINUOUS)

    Q_mujeres    = m.addVars(G, vtype=GRB.CONTINUOUS, name = "nro de alumnos con una caract en grupo")
    P_mujeres    = m.addVars(G, vtype=GRB.BINARY, name="Si hay cero alumnos con la caract")
    F_mujeres   = m.addVars(G, lb=0,vtype=GRB.CONTINUOUS)

    Q_municipal    = m.addVars(G, vtype=GRB.CONTINUOUS, name = "nro de alumnos con una caract en grupo")
    P_municipal    = m.addVars(G, vtype=GRB.BINARY, name="Si hay cero alumnos con la caract")
    F_municipal   = m.addVars(G, lb=0,vtype=GRB.CONTINUOUS)

    Q_regiones    = m.addVars(G, vtype=GRB.CONTINUOUS, name = "nro de alumnos con una caract en grupo")
    P_regiones    = m.addVars(G, vtype=GRB.BINARY, name="Si hay cero alumnos con la caract")
    F_regiones   = m.addVars(G, lb=0,vtype=GRB.CONTINUOUS)

    Q_TI    = m.addVars(G, vtype=GRB.CONTINUOUS, name = "nro de alumnos con una caract en grupo")
    P_TI    = m.addVars(G, vtype=GRB.BINARY, name="Si hay cero alumnos con la caract")
    F_TI   = m.addVars(G, lb=0,vtype=GRB.CONTINUOUS)

    m.update()

    print("F.O . . . ")
    N = len(I)
    m.setObjective(100*quicksum(z[(i)] for i in I) + quicksum(F_mujeres[(g)] for g in G) + quicksum(F_municipal[(g)] for g in G) +quicksum(F_regiones[(g)] for g in G) + quicksum(F_TI[(g)] for g in G) , GRB.MINIMIZE)
    #Restricciones
    print("Restricciones . . .")

    m.addConstr(quicksum(w[(g)] for g in G), GRB.LESS_EQUAL, cant_grupos)
    m.addConstr(quicksum(w[(g)] for g in G), GRB.GREATER_EQUAL, 120)
    print("Restricción de antisimetría")
    for t in T:
        for g in G_t[(t)]:
            for g2 in G_t[(t)]:
                if g2 == g - 1 :
                    m.addConstr(y[(i,g)], GRB.LESS_EQUAL,\
                                quicksum(y[(j,g-1)] for j in I if ID[(j)] < ID[(i)]), name="Antisimetría")
                    
    print("Otras Restricciones")
    m.addConstrs((quicksum(y[(i,g)]*P_ig[(i,g)] for g in G)==z[(i)] for i in I), name="Z_i")
    m.addConstrs((w[(g)]>=y[(i,g)] for i in I for g in G), name="Activación W")

    m.addConstrs((quicksum(y[(i,g)] for g in G) == 1 for i in I), name="Asignación 2")

    print("Máx/Mín alumnos por grupo")
    m.addConstrs((q_min*w[(g)]<=quicksum(y[(i,g)] for i in I)for g in G),name="Mínimo de alumnos")
    m.addConstrs((quicksum(y[(i,g)] for i in I)<=q_max*w[(g)] for g in G), name="Máximo de alumnos")
    #m.addConstrs((quicksum(y[(i,g)] for i in I) - q_min <= F_grupo[(g)] for g in G), name="F_grupos")

    print("Características del grupo")
    m.addConstrs((quicksum(y[(i,g)]*r_ig[(i)] for i in I) == Q_mujeres[(g)] for g in G), name="variable q_g para mujeres")
    m.addConstrs((F_mujeres[(g)] >= Q_mujeres[(g)] - m_min for g in G), name="F_g mujeres")
    m.addConstrs((m_min*w[(g)] - m_min*P_mujeres[(g)] <= Q_mujeres[(g)] for g in G), name= "Cantidad de mujeres por grupo")
    m.addConstrs((Q_mujeres[(g)] <= m_max*(1-P_mujeres[(g)]) for g in G), name="Máximo de mujeres por grupo")


    m.addConstrs((quicksum(y[(i,g)]*r_icol[(i)] for i in I) == Q_municipal[(g)] for g in G), name="variable q_g para municipales")
    m.addConstrs((F_municipal[(g)] >= Q_municipal[(g)] - publ_min for g in G), name="F_g municipales")
    m.addConstrs((publ_min*w[(g)] - publ_min*P_municipal[(g)] <= Q_municipal[(g)] for g in G), name= "Cantidad de municipal por grupo")
    m.addConstrs((Q_municipal[(g)] <= publ_max*(1-P_municipal[(g)]) for g in G), name="Máximo de muncipal por grupo")


    m.addConstrs((quicksum(y[(i,g)]*r_ireg[(i)] for i in I) == Q_regiones[(g)] for g in G), name="variable q_g para regiones")
    m.addConstrs((F_regiones[(g)] >= Q_regiones[(g)] - region_min for g in G), name="F_g regiones")
    m.addConstrs((region_min*w[(g)] - region_min*P_regiones[(g)] <= Q_regiones[(g)] for g in G), name= "Cantidad de regiones por grupo")
    m.addConstrs((Q_regiones[(g)] <= region_max*(1-P_regiones[(g)]) for g in G), name="Máximo de regiones por grupo")

    m.addConstrs((quicksum(y[(i,g)]*r_iTI[(i)] for i in I) == Q_TI[(g)] for g in G), name="variable q_g para TI")
    m.addConstrs((F_TI[(g)] >= Q_TI[(g)] - TI_min for g in G), name="F_g TI")
    m.addConstrs((TI_min*w[(g)] - TI_min*P_TI[(g)] <= Q_TI[(g)] for g in G), name= "Cantidad de TI por grupo")
    m.addConstrs((Q_TI[(g)] <= TI_max*(1-P_TI[(g)]) for g in G), name="Máximo de TI por grupo")

    print("Restricción de colegios")
    m.addConstrs((quicksum(y[(i,g)]*parameters["colegio_bin"][(i,Colegios[c])] for i in I) <=1 for g in G for c in range(0, len(Colegios))) , name="1 por colegio_menor a 1")

    myopt(m)


    status=m.Status
    if status==GRB.Status.INFEASIBLE or status==GRB.Status.UNBOUNDED or status == GRB.Status.INF_OR_UNBD:
        print("MODELO INFACTIBLE")

    return m

#La funcion CrearExcel se encarga de arrojar el excel que muestra la solucion
#El nombre del archivo siempre sera "Asignaciones_SIGLA".xlsx
#si se corre muchas veces el codigo el archivo se sobreescribe
def CrearExcelSUS1000(modelo, variables, parameters, conjuntos):
    result=modelo.getVars()

    I   = variables["LISTAS"]["numero_alumno"]
    D   = conjuntos["D"]
    T   = conjuntos["T"]
    G   = conjuntos["G"]
    G_d = conjuntos["G_d"]
    t_g = conjuntos["t_g"]

    r_ig      = parameters["r_ig"]
    r_icol    = parameters["r_icol"]
    r_ireg    = parameters["r_ireg"]
    r_icarr   = parameters["r_icarr"]
    r_cluster = parameters["r_cluster"]

    c_d  = parameters["c_d"]
    a_id = parameters["a_id"]
    n_i  = parameters["n_i"]
    P_it = parameters["P_it"]
    P_ig = parameters["P_ig"]

    Carrera_bin = parameters["Carrera_bin"]
    cluster_bin = parameters["cluster_bin"]

    name      = parameters["r_iname"]
    last_name = parameters ["r_iape"]

    nozero=[]

    for i in result:
        if i.X>0.5:
            nozero.append(i)

    nozero_x=[]
    nozero_y=[]

    for i in nozero:
        if i.varname[0]=="X":
            nozero_x.append(i.varname.lstrip('X[').rstrip(']').split(',')) #["nro_alumno","cátedra"]
        elif i.varname[0]=="Y":
            nozero_y.append(i.varname.lstrip('Y[').rstrip(']').split(',')) #["nro_alumno","grupo"]

    created = False
    for i in nozero_x:
        for j in nozero_y:
            if i[0]==j[0]:
                numero_alumno = i[0]
                index      = variables["LISTAS"]["numero_alumno"].index(numero_alumno)
                grupo      = j[1]
                tema       = t_g[int(grupo)]
                genero     = r_ig[i[0]]
                region     = r_ireg[i[0]]
                tipo_col   = r_icol[i[0]]
                carrera    = r_icarr[i[0]]
                alumno_nom = variables["LISTAS"]["nombre"][index]
                alumno_ape = variables["LISTAS"]["apellido"][index]
                alumno_mail= variables["LISTAS"]["email"][index]
                rank       = variables["DICCIONARIOS"]["prioridad"][numero_alumno]
                r          = rank[:4]
                for key,value in P_it:
                    if tema in r:
                        prioridad = P_it[i[0],tema]
                    else:
                        prioridad="1000"
                for d in D:
                    if int(grupo) in G_d[(d)]:
                        row = pd.DataFrame([[i[0], str(alumno_nom), str(alumno_ape), i[1], j[1], str(tema), str(prioridad), str(r), str(d), str(genero), str(region), str(tipo_col), str(carrera)]], columns=[
                "Alumno", "Nombre", "Apellido", "Catedra", "Grupo", "Tema", "Prioridad","Ranking","Taller", "Género", "Region", "Tipo de colegio", "Carrera"])
                if not created:
                    output_df = row.copy()
                    created = True
                else:
                    output_df = output_df.append(row)

    writer = ExcelWriter('Asignaciones_SUS1000.xlsx')
    output_df.to_excel(writer,'Hoja1',index=False)
    writer.save()
    print("Archivo Asignaciones_SUS1000.xlsx creado")
    return writer

def CrearExcelING1004(modelo, variables, parameters, conjuntos):
    result=modelo.getVars()

    I = variables["LISTAS"]["numero_alumno"]
    D = conjuntos["D"]
    T = conjuntos["T"]
    G = conjuntos["G"]

    G_d  = conjuntos["G_d"]
    t_g  = conjuntos["t_g"]

    r_ig    = parameters["genero"]
    r_ireg  = parameters["region"]
    r_icol  = parameters["tipo_colegio"]
    r_icarr = parameters["carrera"]
    r_iTI   = parameters["via caso_TI"]

    a_id = parameters["a_id"]
    n_i  = parameters["n_i"]
    P_it = parameters["P_it"]

    seccion = parameters["seccion"]
    cole    = parameters["colegio"]

    nozero=[]
    nozero_x=[]
    nozero_y=[]


    for i in result:
        if i.X>0.5:
            nozero.append(i)

    for i in nozero:
        if i.varname[0]=="Y":
            nozero_y.append(i.varname.lstrip('Y[').rstrip(']').split(',')) #["nro_alumno","grupo"]

    created = False
    for i in nozero_y:
        numero_alumno = i[0]
        index    = variables["LISTAS"]["numero_alumno"].index(str(numero_alumno))
        grupo    = i[1]
        tema     = t_g[int(grupo)]
        genero   = r_ig[str(i[0])]
        region   = r_ireg[str(i[0])]
        tipo_col = r_icol[str(i[0])]
        carrera  = r_icarr[str(i[0])]
        talento  = r_iTI[str(i[0])]
        secc     = seccion[str(i[0])]
        secc_final = t_g[int(grupo)]
        colegio    = cole[str(i[0])]

        for d in D:
            if int(grupo) in G_d[(d)]:
                row = pd.DataFrame([[i[0], i[1],  str(genero), str(region), str(talento), str(colegio), str(tipo_col), str(secc), str(secc_final),str(carrera)]], columns =
                ["Alumno",  "Grupo", "Género", "Region", "T&I","Colegio", "Tipo de colegio", "Seccion", "Secc Final", "Carrera"])
                if not created:
                    output_df = row.copy()
                    created = True
                else:
                    output_df = output_df.append(row)


    writer = ExcelWriter('Asignaciones_ING1004.xlsx')
    output_df.to_excel(writer,'Hoja1',index=False)
    writer.save()
    print("Archivo Asignaciones_ING1004.xlsx creado")
    return writer

"""
if __name__=="__main__":
    import pandas as pd
    from gurobipy import *
    from pandas import ExcelWriter
    from pandas import ExcelFile
    from constants import *
    from custom import *

    curso         = "SUS1000"
    archivo       = "ODS - cluster.xlsx"
    hoja          = "Respuestas de formulario 1"

    raw_df = pd.read_excel("../../Muestras/"+archivo,sheet_name=hoja)

    cant_gtd = parametros["cant_gtd"]
    df =  AdapterSUS1000(raw_df, sus_encoding_dictionary)
    variables = CreateVariablesSUS1000(df)
    conjuntos = CrearConjuntos(cant_gtd, variables)
    agregacion_carrera = ConjuntoCarrerasAuxiliar(variables["DICCIONARIOS"]["cluster"])
    agregacion_carrera = ArmarClusters(clusters)
    parameters = CreateParametersSUS1000(variables, conjuntos, agregacion_carrera)
    for key in parametros:
        parameters[key]   = parametros[key]

    modelo =    CrearModeloSUS1000(
        variables, conjuntos, parametros, parameters, agregacion_carrera
        )
    CrearExcelSUS1000(modelo, variables, parameters, conjuntos)
"""
