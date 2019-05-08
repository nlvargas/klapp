params =  input("Ingrese archivo de parámetros .txt : ")
clust  =  input("Ingrese archivo de clusters .txt : ")

#Este código se encarga de traducir el excel que se recibe
#Contiene diccionarios para ING1004 y para SUS1000, se pueden modificar según las necesidades
#También recibe los archivos .txt de los parámetros y los clusters
#Si bien ING1004 no usa clusters, el código los preguntará de todas maneras
#basta con ingresar algún archivo .txt, el resto del código (para ING1004) no lo necesitará

#Aquí se leen los parámetros que se utilizarán después
with open(params, "r") as f:
    parametros  = {
        "q_min"      :0,
        "q_max"      :0,
        "part_min"   :0,
        "part_max"   :0,
        "publ_min"   :0,
        "publ_max"   :0,
        "m_min"      :0,
        "m_max"      :0,
        "h_min"      :0,
        "h_max"      :0,
        "region_min" :0,
        "region_max" :0,
        "TI_min"     :0,
        "TI_max"     :0,
        "cant_gtd"   :0,
        "cant_grupos":0

    }
    for linea in f:
        for parameter in parametros:
            if parameter in linea:
                #print(parameter, linea.strip().strip(parameter))
                parametros[parameter] = int(linea.replace(parameter,"").strip())

#Acá se leen los clusters de ser necesarios
with open(clust,"r") as c:
    clusters = {
        "cluster1"  :"",
        "cluster2"  :"",
        "cluster3"  :"",
        "cluster4"  :"",
        "cluster5"  :"",
        "cluster6"  :"",
        "cluster7"  :"",
        "cluster8"  :"",
        "cluster9"  :"",
        "cluster10" :"",
        "cluster11" :"",
        "cluster12" :"",
        "cluster13" :"",
        "cluster14" :"",
        "cluster15" :"",
        "cluster16" :"",
        "cluster17" :"",
        "cluster18" :"",
        "cluster19" :"",
        "cluster20" :""

    }

    for linea in c:
        for cluster in clusters:
            if cluster in linea:
                #print(cluster, linea.strip().strip(cluster))
                clusters[cluster] = linea.replace(cluster,"").strip()

#Este es el diccionario utilizado para SUS1000
sus_encoding_dictionary={
            "Género":{
                "Hombre":0,
                "Mujer":1,
                "Prefiero no decirlo":0,
                "#N/A":0},
            "En qué comuna vives?":{
                'Vivo fuera de Santiago': 1,
                'Conchali':0,
                'El Bosque':0,
                'Estación Central': 0,
                'Huechuraba': 0,
                'La Cisterna': 0,
                'La Florida': 0,
                'La Granja': 0,
                'La Reina': 0,
                'Las Condes': 0,
                'Lo Barnechea': 0,
                'Lo Prado': 0,
                'Macul': 0,
                'Maipú': 0,
                'Ñuñoa': 0,
                'Padre Hurtado': 0,
                'Peñalolen': 0,
                'Pirque': 0,
                'Prefiero no decirlo': 0,
                'Providencia': 0,
                'Pedro Aguirre Cerda':0,
                'Pudahuel': 0,
                'Puente Alto': 0,
                'Quilicura': 0,
                'Recoleta':0,
                'Renca':0,
                'San Bernardo':0,
                'San Joaquín': 0,
                'San Miguel': 0,
                'San Ramón': 0,
                'Santiago': 0,
                'Vitacura':0,
                '#N/A':0},
            "Tipo de establecimiento donde cursaste enseñanza media:":{
                'Colegio Particular': 1,
                'Colegio Municipal': 0,
                'Colegio Particular Subvencionado': 1,
                'Prefiero no decirlo':1,
                '#N/A':1},
            "Primera prioridad de ODS":{
                'Acción por el clima':1,
                'Agua limpia y saneamiento':2,
                'Ciudades y comunidades sostenibles':3,
                'Educación de calidad': 4,
                'Energía asequible y no contaminante': 5,
                'Fin de la pobreza': 6,
                'Hambre cero': 7,
                'Igualdad de genero': 8,
                'Industria, innovación e infraestructura': 9,
                'Paz, Justicia e instituciones sólidas': 10,
                'Producción y consumo responsables': 11,
                'Reducción de las desigualdades': 12,
                'Salud y Bienestar': 13,
                'Trabajo decente y crecimiento económico': 14,
                'Vida de ecosistemas terrestres': 15,
                'Vida submarina': 16},
            "Segunda prioridad de ODS":{
                'Acción por el clima':1,
                'Agua limpia y saneamiento':2,
                'Ciudades y comunidades sostenibles':3,
                'Educación de calidad': 4,
                'Energía asequible y no contaminante': 5,
                'Fin de la pobreza': 6,
                'Hambre cero': 7,
                'Igualdad de genero': 8,
                'Industria, innovación e infraestructura': 9,
                'Paz, Justicia e instituciones sólidas': 10,
                'Producción y consumo responsables': 11,
                'Reducción de las desigualdades': 12,
                'Salud y Bienestar': 13,
                'Trabajo decente y crecimiento económico': 14,
                'Vida de ecosistemas terrestres': 15,
                'Vida submarina': 16},
            "Tercera prioridad de ODS":{
                'Acción por el clima':1,
                'Agua limpia y saneamiento':2,
                'Ciudades y comunidades sostenibles':3,
                'Educación de calidad': 4,
                'Energía asequible y no contaminante': 5,
                'Fin de la pobreza': 6,
                'Hambre cero': 7,
                'Igualdad de genero': 8,
                'Industria, innovación e infraestructura': 9,
                'Paz, Justicia e instituciones sólidas': 10,
                'Producción y consumo responsables': 11,
                'Reducción de las desigualdades': 12,
                'Salud y Bienestar': 13,
                'Trabajo decente y crecimiento económico': 14,
                'Vida de ecosistemas terrestres': 15,
                'Vida submarina': 16},
            "Cuarta prioridad de ODS":{
                'Acción por el clima':1,
                'Agua limpia y saneamiento':2,
                'Ciudades y comunidades sostenibles':3,
                'Educación de calidad': 4,
                'Energía asequible y no contaminante': 5,
                'Fin de la pobreza': 6,
                'Hambre cero': 7,
                'Igualdad de genero': 8,
                'Industria, innovación e infraestructura': 9,
                'Paz, Justicia e instituciones sólidas': 10,
                'Producción y consumo responsables': 11,
                'Reducción de las desigualdades': 12,
                'Salud y Bienestar': 13,
                'Trabajo decente y crecimiento económico': 14,
                'Vida de ecosistemas terrestres': 15,
                'Vida submarina': 16},

            }

#Este es el diccionario utilizado para ING1004
ing_encoding_dictionary={
        "SEXO":{
            "M":0,
            "F":1},
        "COLEGIO REGIÓN":{
            'I': 1,
            'II': 1,
            'III': 1,
            'IV': 1,
            'IX': 1,
            'V': 1,
            'VI': 1,
            'VII': 1,
            'VIII': 1,
            'X': 1,
            'XI': 1,
            'XIII': 0,
            'XIV': 1,
            'XV': 1,
            'XVI':1,
            'XII':1,
            'NO': 0
            },
        "Vía Caso":{
            'SI':1,
            'NO':0
            },
        "COLEGIO TIPO":{
            "PARTICULAR": 0,
            "COMPARTIDO":0,
            "MUNICIPAL" :1
        }
    }
