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

#para ahorrar en calculos creamos esta variable global.
#la inicializamos al definir get_all_stations aqui abajo, con su valor
REFERENCE_STATIONS = {}

def get_api_key():
    with open("../apikey.json", "r") as f:
        api_data = json.load(f)
    key = api_data["data"][0]["accessToken"]
    return {"accessToken" : key}

def get_all_stations():
    api_url = "https://openapi.emtmadrid.es/v1/"
    url = api_url + "transport/bicimad/stations/"
    return req.get(url, headers = get_api_key()).json()["data"]

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

def find_new_travel():
    stations = get_stat_by_id()
    while(True):
        a = get_all_stations()
        for i in a:
            s_id = i["id"]
            if stations[s_id]["dock_bikes"] == (i["dock_bikes"] -1) :
                print(f'[+] una bici se cogio en la estacion {i["name"]}')
                return s_id


def find_end_travel():
    stations = get_stat_by_id()
    while(True):
        a = get_all_stations()
        for i in a:
            s_id = i["id"]
            if stations[s_id]["free_bases"] == (i["free_bases"] -1) :
                print(f'[!] una bici se dejo en la estacion {i["name"]}')
                return s_id


def get_location_id(sid):
    #variable global que contiene una muestra de todas las estaciones
    for i in REFERENCE_STATIONS: 
        if i["id"] == sid:
            return i["geometry"]["coordinates"]
    raise "El id de estacion no existe"

print("Encontrado un nuevo viaje: ")
inicio = find_new_travel()
ini_date = datetime.now()
print(f'[ ] la fecha de inicio del viaje es {ini_date}')
ini_loc = get_location_id(inicio)
print(f'[ ] las coordenadas de inicio del viaje son {ini_loc}')
while(True):
    fin = find_end_travel()
    end_date = datetime.now()
    end_loc = get_location_id(fin)
    dist = geopy.distance.distance(ini_loc, end_loc)
    time = end_date - ini_date
    print(f'[ ] posible fin de trayecto:')
    print(f'[ ] recorridos {dist} minimo en {time} horas.')

