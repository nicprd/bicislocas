import requests as req
import json
from datetime import datetime
#para medir distancias entre coordenadas
import geopy.distance 
import platform 
import os

"""Some utilities"""
###utility for clearing the screen##
def clearscreen():
    if platform.system() == 'Windows':
        os.system("cls")
    else:
        os.system("clear")

print("Inicializando las variables del script")

#utility for reading the apiKEY
def get_api_key(file="../apikey.json"):
    with open(file, "r") as f:
        api_data = json.load(f)
        key = api_data["data"][0]["accessToken"]
    return {"accessToken" : key}


print("Leyendo la llave de la api...")

"""GLOBAL VARIABLES"""# Mas facil para todos si es asi. 
try:
    API_KEY = get_api_key()
    print("[+] OK!")
except OSError as e:
    print(f"[!] Error : {e}")
    key = input(f"Introduce manualmente una apiKey de la EMT: ")
    API_KEY = {"accessToken" : key}


def get_all_stations():
    api_url = "https://openapi.emtmadrid.es/v1/"
    url = api_url + "transport/bicimad/stations/"
    data = req.get(url, headers = API_KEY).json()
    if data["code"] != "02":
        raise ValueError(f"El servidor de BiciMad ha respondido con error: {data['code']}.\nComprueba la apiKey")
    return data["data"]

#para ahorrar en calculos creamos esta variable global.
print("Comprobando la conexion con biciMad... ")
try:
    REFERENCE_STATIONS = get_all_stations()  ####
except ValueError as e:
    print(f"[!] Error conectando con BiciMad: {e})")
    exit(-1)
print("[+] OK!")

""""funciones que usamos para trabajar con os datos de BiciMad""""
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

def get_pos_id(sid):
    for i in REFERENCE_STATIONS: 
        if i["id"] == sid:
            return i["geometry"]["coordinates"]
    raise "El id de estacion no existe"

def get_name(sid):
    for i in REFERENCE_STATIONS: 
        if i["id"] == sid:
            return i["name"]
    raise "El id de estacion no existe"

""" Definimos las clases con las que vamos a trabajar"""
#una ubicacion y tiempo de una bici cogida o dejada.
class bikeStamp:
    def __init__(self,sid):
        self.sid = sid
        self.time = datetime.now()
        self.pos = get_pos_id(sid)

    def getRelDist(self,bikeS): #getRelativeDistance
        return geopy.distance.distance(self.pos,bikeS.pos)

    def getRelTime(self,bikeS): #getRelativeTime
        return self.time - bikeS.time

    def getRelVel(self,bikeS): #getRelativeVelocity
        dist = self.getRelDist(bikeS)
        time = self.getRelTime(bikeS).total_seconds()
        return dist*3600/time

    def isMatch(self,bikeS):
        a = self.getRelVel(bikeS) < 20
        b = self.getRelVel(bikeS) > 0
        return a & b

    def getBetterMatch(self, bikeS, bikeS2):
        dist1= self.getRelDist(bikeS) 
        dist2= self.getRelDist(bikeS2)
        vel1= self.getRelVel(bikeS) 
        vel2= self.getRelVel(bikeS2) 

        if self.isMatch(bikeS) & self.isMatch(bikeS2):
            match = bikeS if dist1 > dist2 else bikeS2
        else: 
            match = bikeS if self.isMatch(bikeS) else bikeS2
        return match

class travel:
    def __init__(self, bike1, bike2):
        self.startPos = bike1.sid
        self.endPos = bike2.sid
        self.startTime = bike1.time
        self.endTime = bike2.time
        self.time = bike1.getRelTime(bike2).total_seconds()/60
        self.dist = bike1.getRelDist(bike2)
        self.vel = bike1.getRelVel(bike2)
    def __str__(self):
        a = f"Viaje desde {get_name(self.startPos)} hacia {get_name(self.endPos)}.\n"
        b = f"Recorridos {self.dist} en {round(self.time,2)} mins. ({self.vel}/h)"
        return a + b

#side efects modify end to delete ends without starts 
def getPossibleTravels(sta, end):
    sta_cpy = sta.copy()
    end_cpy = end.copy()
    travels = []
    for i in sta:
        for e in end_cpy:
            if i.isMatch(e):
                travels.append(travel(i,e))
                end_cpy.remove(e)
    #por algun modo el codigo de abajo para todo. 
    #for i in end_cpy:
    #   end.remove(i)
    return travels

def getPossibleTravels_t(sta, end):
    end_cpy = end.copy()
    travels = []
    for i in sta:
        if len(end_cpy) < 1: return travels
        top_match = end_cpy[0] 
        for e in end_cpy:
         top_match = i.getBetterMatch(top_match, e)
        if i.isMatch(top_match): travels.append(travel(i, top_match))
        end_cpy.remove(top_match)
    end = end_cpy
    return travels
    
"""Main loop"""

print("Vamos a buscar posibles viajes en BiciMad.")
print("Esto puede tardar unos momentos.")
print("¡Tanto como un viaje en bici!")
print("...........................Script por lordjimbo@protonmail.com ")

starts = []
ends = []
travels = []
stations = get_stat_by_id()
while(True):
    a = get_all_stations()
    change = 0
    for i in a:
        s_id = i["id"]
        if stations[s_id]["dock_bikes"] == (i["dock_bikes"] -1) :
            starts.append(bikeStamp(s_id))
            change += 1
        if stations[s_id]["free_bases"] == (i["free_bases"] -1) :
            ends.append(bikeStamp(s_id))
            change += 1
    if change != 0: #Aunque esta condicion parece absurda, creedme no lo es
        stations = get_stat_by_id()
        travels = getPossibleTravels_t(starts,ends)
        if len(travels) > 0:
            clearscreen()   
            print("Estas son las mejores sugerencias de viajes (Dale tiempo para que muestre algo razonable):" )
            [print(f'[{i}] {e}') for i, e in enumerate(travels)]
            
        
    