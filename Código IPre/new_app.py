print("Cargando Librerías ...")
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
from gurobipy import *
from custom import *
from constants import *
from main import *

#Este codigo se encarga de unificar los codigos anteriores
curso   = input("Ingrese curso (ING1004 ó SUS1000): ")
archivo = input("Ingrese archivo .xlsx : " )
hoja    = input("Ingrese hoja en que se encuentran los datos: ")

#Esta linea lee el archivo donde se encuenta la informacion de los alumnos
#Notar que los lee desde una carpeta "Muestras"
raw_df  = pd.read_excel("../../Muestras/"+archivo,sheet_name=hoja)

if curso=="ING1004":
    cant_gtd = parametros["cant_gtd"]

    df        =  AdapterING1004(raw_df, ing_encoding_dictionary)
    variables = CreateVariablesING1004(df)

    conjuntos = CrearConjuntos(cant_gtd, variables, curso)

    parameters = CreateParametersING1004(variables, conjuntos)
    c_d        = parameters["c_d"]

    Colegios = ConjuntoColegios(parameters)

    for key in parametros:
        parameters[key]   = parametros[key]

    modelo = CrearModeloING1004(variables, conjuntos, parameters, parametros,Colegios)

    status=modelo.Status
    if status==GRB.Status.INFEASIBLE or status==GRB.Status.UNBOUNDED or status == GRB.Status.INF_OR_UNBD:
        print("MODELO INFACTIBLE")
    else:

        CrearExcelING1004(modelo, variables, parameters, conjuntos)

elif curso=="SUS1000":

    cant_gtd = parametros["cant_gtd"]

    df        =  AdapterSUS1000(raw_df, sus_encoding_dictionary)
    variables = CreateVariablesSUS1000(df)

    conjuntos = CrearConjuntos(cant_gtd, variables,curso)

    agregacion_carrera = ConjuntoCarrerasAuxiliar(variables["DICCIONARIOS"]["cluster"])
    agregacion_carrera = ArmarClusters(clusters)

    parameters = CreateParametersSUS1000(variables, conjuntos, agregacion_carrera)

    for key in parametros:
        parameters[key]   = parametros[key]

    modelo = CrearModeloSUS1000(
        variables, conjuntos, parameters, agregacion_carrera
        )
    status=modelo.Status
    if status==GRB.Status.INFEASIBLE or status==GRB.Status.UNBOUNDED or status == GRB.Status.INF_OR_UNBD:
        print("MODELO INFACTIBLE")
    else:
        CrearExcelSUS1000(modelo, variables, parameters, conjuntos)
