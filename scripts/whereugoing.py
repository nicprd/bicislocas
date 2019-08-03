import requests as req
import json
from datetime import datetime
#para medir distancias entre coordenadas
import geopy.distance 
import platform 
import os

print("Inicializando las variables del script")

###utility for clearing the screen##
def clearscreen():
    if platform.system() == 'Windows':
        os.system("cls")
    else:
        os.system("clear")
#utility for reading the apiKEY
def get_api_key():
    with open("../apikey.json", "r") as f:
        api_data = json.load(f)
    key = api_data["data"][0]["accessToken"]
    return {"accessToken" : key}

print("Leyendo la llave de la api...", end= "")
#######GLOBAL VARIABLE##### Mas facil para todos si es asi. 
try:
    API_KEY = get_api_key()####
except Exception as e:
    print(f"[!] Error : {e}")
    exit(-1)
print("OK!")


def get_all_stations():
    api_url = "https://openapi.emtmadrid.es/v1/"
    url = api_url + "transport/bicimad/stations/"
    return req.get(url, headers = API_KEY).json()["data"]

#para ahorrar en calculos creamos esta variable global.
#################GLOBAL VARIABLE#############
print("Comprobando la conexion con biciMad... ", end="")
try:
    REFERENCE_STATIONS = get_all_stations()  ####
except Exception as e:
    print(f"Error conectando con BiciMad: {e})")
print("OK!")

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

def getPossibleTravels(sta, end):
    travels = []
    for i in sta:
        for e in end:
            if i.isMatch(e):
                travels.append(travel(i,e))
    return travels

starts = []
ends = []
travels = []

print("Vamos a buscar posibles viajes en BiciMad.")
print("Esto puede tardar unos momentos.")
print("¡Tanto como un viaje en bici!")
print("...........................Script por lordjimbo@protonmail.com ")


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
        travels = getPossibleTravels(starts,ends)
        if len(travels) > 0:
            clearscreen()   
            print("Hemos encontrado los siguientes viajes:" )
            [print(f'[{i}] {e}') for i, e in enumerate(travels)]
            
        
    
