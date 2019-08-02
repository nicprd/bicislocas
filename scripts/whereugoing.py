"""
Cuando una bici se pierde de algun sitio rastreamos hasta
esperar donde aparece una nueva bici.
Calculamos el tiempo que tarda hasta que aparece una nueva bici
medimos la distancia entre las dos estaciones.
Calculamos si es un tiempo razonable de destino.
Asumimos como destino o seguimos esperando un nuevo destino
"""

"""
TODO: LA ruta sensata la mediremos en km/h 
      Crearemos un conjunto de rutas sensatas para cada nueva ruta que se abre
"""

import requests as req
import json
from datetime import datetime
#para medir distancias entre coordenadas
import geopy.distance 

def get_api_key():
    with open("../apikey.json", "r") as f:
        api_data = json.load(f)
    key = api_data["data"][0]["accessToken"]
    return {"accessToken" : key}

#######GLOBAL VARIABLE#####
API_KEY = get_api_key()####
###########################

def get_all_stations():
    api_url = "https://openapi.emtmadrid.es/v1/"
    url = api_url + "transport/bicimad/stations/"
    return req.get(url, headers = API_KEY).json()["data"]

#para ahorrar en calculos creamos esta variable global.
#################GLOBAL VARIABLE#############
REFERENCE_STATIONS = get_all_stations()  ####
#############################################

def get_stat_by_id():
    #guardamos las estaciones como un diccionario { idNumerico : {}}
    #asi se vuelve mas facil acceder a la estacion sin iterar toda la lista
    return {
        i["id"]:
        {
            "dock_bikes": i["dock_bikes"],
            "free_bases" : i["free_bases"]
        }
        for i in get_all_stations()
    }

def get_location_id(sid):
    for i in REFERENCE_STATIONS: 
        if i["id"] == sid:
            return i["geometry"]["coordinates"]
    raise "El id de estacion no existe"

def get_name_id(sid):
    for i in REFERENCE_STATIONS: 
        if i["id"] == sid:
            return i["name"]
    raise "El id de estacion no existe"



#VAMOS AL MEOLLO
"""

Lo importante aqui es la forma en la que guardamos los datos
de los posibles destinos. 
Tenemos un Array, que guarda Arrays que guardan conjuntos de viajes posibles.

tra_sta = [C1, C2, ...]

Un conjunto de viajes posibles C1, tiene esta estructura:

C1 = [Inicio, [F1, F2, ...]] Donde F1 es un final posible 

Inicio = [id, time] id es el id de la estacion segun BICIMAD, 
                    time es el tiempo de inicio del viaje,

F1 = [id, dist, traveltime] id es el id de la estacion segun BICIMAD
                            dist es la distancia en Km entre INICIO y F1
                            traveltime es el tiempo entre inicio y F1

"""


#travels es el array de viajes posibles
def check_end_start(travels, end_id):
    loc_end = get_location_id(end_id)
    time_end = datetime.now()
    for i in travels:
        loc_st = get_location_id(i[0][0])
        time = time_end - i[0][1]
        dist = geopy.distance.distance(loc_st,loc_end)
        data = [end_id, dist, time]
        i[1].append(data)


def check_reasonable(travels):
    for i in travels:
        for e in i[1]:
            vel = e[1]/(e[2].total_seconds()/60)
            vel *= 60
            if vel > 25:
                i[1].remove(e)
                
import os
import sys

def print_travels(travels):
    os.system("clear")
    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    print("$$$             BICIMAD BLIND TRACKER            $$$$")
    print("$$$______________________________________________$$$$\n")
    print(f'\r[!] Estos son los posibles viajes que hemos encontrado:')
    sys.stdout.flush()
    for n, i in enumerate(travels):
        st_loc = get_name_id(i[0][0])
        print(f"[{n}] Viaje desde {st_loc} a las {i[0][1]}")
        for n2, e in enumerate(i[1]):
            loc = get_name_id(e[0])
            dist = e[1]
            time = e[2].total_seconds()/60
            vel = (dist/time)*60
            print(f"[ ]-[{n2}] Posible final en: {loc}, un minimo de {dist} en {round(time,2)} minutos")
            print(f'[ ]-[ ] Velocidad de: {vel}/h')
        
################################################
############## MAIN LOOP ######################
##############################################

tra_sta = []

stations = get_stat_by_id()
while(True):
    a = get_all_stations()
    change = 0
    for i in a:
        s_id = i["id"]
        if stations[s_id]["dock_bikes"] == (i["dock_bikes"] -1) :
            data = [s_id, datetime.now()]
            tra_sta.append([data,[]])
            change += 1
        if stations[s_id]["free_bases"] == (i["free_bases"] -1) :
            check_end_start(tra_sta, s_id)
            change += 1
    if change != 0: #Aunque esta condicion parece absurda, creedme no lo es
        stations = get_stat_by_id()
    check_reasonable(tra_sta)
    print_travels(tra_sta)
    
