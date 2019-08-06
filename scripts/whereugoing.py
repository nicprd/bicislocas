import requests as req
import json
from datetime import datetime, timedelta
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

print("[-] Inicializando las variables del script")
"""GLOBAL VARIABLES used by some functions. Get values ASAP"""
API_KEY = {}
REFERENCE_STATIONS = {}

def get_api_key(file="../apikey.json"):
    with open(file, "r") as f:
        api_data = json.load(f)
        key = api_data["data"][0]["accessToken"]
    return {"accessToken" : key}

print("[-] Leyendo la llave de la api...", end=" ")
try:
    API_KEY = get_api_key()
    print("[+] OK!")
except OSError as e:
    print(f"[!] Error : {e}")
    key = input(f"[-] Introduce manualmente una apiKey de la EMT: ")
    API_KEY = {"accessToken" : key}

def get_all_stations():
    api_url = "https://openapi.emtmadrid.es/v1/"
    url = api_url + "transport/bicimad/stations/"
    data = req.get(url, headers = API_KEY).json()
    if data["code"] != "0":
        raise ValueError(f"BiciMad respondio con error: {data['code']}.\nComprueba la apiKey")
    return data["data"]

print("[-] Comprobando la conexion con biciMad...", end=" ")
try:
    REFERENCE_STATIONS = get_all_stations()  ####
except ValueError as e:
    print(f"[!] Error: {e})")
    exit(-1)
print("[+] OK!")

"""funciones que usamos para trabajar con os datos de BiciMad"""
def get_stat_by_id():
    """guardamos las estaciones como un diccionario { idNumerico : {}}"""
    return {
        i["id"]:
        {
            "dock_bikes": i["dock_bikes"],
            "free_bases" : i["free_bases"]
        }
        for i in get_all_stations()
    }

def get_pos(sid):
    for i in REFERENCE_STATIONS: 
        if i["id"] == sid:
            return i["geometry"]["coordinates"]
    raise "El id de estacion no existe"

def get_name(sid):
    for i in REFERENCE_STATIONS: 
        if i["id"] == sid:
            return i["name"]
    raise "El id de estacion no existe"

def asktime(inicio, final):
    """Pregunta a biciMad el tiempo de ruta en bici entre dos coordenadas"""
    url = "https://openapi.emtmadrid.es/v1/transport/busemtmad/travelplan/"
    params = {
        "routeType":"M",
        "coordinateXFrom" :inicio[0],
        "coordinateYFrom" : inicio[1],
        "coordinateXTo" : final[0],
        "coordinateYTo" : final[1],
        "allowBike" : True,
        }
    a = req.post(url, json=params, headers = API_KEY )
    if a.json()["code"] != "00":
        raise Exception("ROUTE_NOT_FOUND")

    return a.json()["data"]["duration"]*60

class bikeStamp:
    """Una ubicacion y tiempo de bici cogida a dejada"""
    def __init__(self,sid):
        self.sid = sid
        self.time = datetime.now()
        self.pos = get_pos(sid)

    def getRelDist(self,bikeS): #getRelativeDistance
        return geopy.distance.distance(self.pos,bikeS.pos)

    def getRelTime(self,bikeS): #getRelativeTime
        return (self.time - bikeS.time).total_seconds()

    def getRelVel(self,bikeS): #getRelativeVelocity
        dist = self.getRelDist(bikeS)
        time = self.getRelTime(bikeS)
        return dist*3600/time

    def getExpectedTime(self,bikeS):
        return asktime(self.pos, bikeS.pos)

    def getProb(self, bikeS):
        expec_Time = self.getExpectedTime(bikeS)
        time = bikeS.getRelTime(self)
        return 100 - (100/(expec_Time/abs(expec_Time-time)))

    def __str__(self):
        return f"<BikeStamp {self.sid} at time {self.time}>"


class travel:
    """Un viaje posible en bici"""
    def __init__(self, bike1, bike2):
        self.bikeStart = bike1 #the only param never changes
        self.startPos = bike1.sid
        self.endPos = bike2.sid
        self.startTime = bike1.time
        self.endTime = bike2.time
        self.time = (self.endTime-self.startTime).total_seconds()
        self.dist = bike1.getRelDist(bike2)
        self.vel = bike2.getRelVel(bike1)
        self.expec_Time = bike1.getExpectedTime(bike2)

    def isMatch(self):
        """Cuando la llegada ocurre antes que el tiempo"""
        return self.time > 0 
    
    def getProb(self):
        return 100 - (100/(self.expec_Time/abs(self.expec_Time-self.time)))

    def isBetterEnd(self, bikeS2):
        return self.getProb() < self.bikeStart.getProb(bikeS2)

    def check_and_set(self,bikeS2):
        print("[DEBUG] Cheking ", self, " [Against] ", bikeS2)
        if self.isBetterEnd(bikeS2):
            print("[DEBUG] was better!")
            self.__init__(self.bikeStart, bikeS2)
            return True
        return False
        
    def __str__(self):
        a = f"Viaje desde {get_name(self.startPos)} hacia {get_name(self.endPos)}.\n"
        b = f"Recorridos {self.dist} en {round(self.time/60,2)} mins. ({self.vel}/h)\n"
        c = f"Probabilidad del trayecto de : {round(self.getProb(),2)}%"
        return a + b + c


def getPossibleTravels_t(travels, end):
    """ Busca el top match entre bikeS y una lista finales de viaje en bici"""
    """ MOdifica end"""
    #print("[DEBUG]",bikeS)
    for i in travels:
        for e in end:   
            i.check_and_set(e)
                #print("[DEBUG]",a)
    return travels

"""Main loop"""
clearscreen()
print("________________________________________________________________")
print("|                BICIMAD BLIND TRACKER                         |")
print("|       Vamos a buscar posibles viajes en BiciMad.             |")
print("|            Esto puede tardar unos momentos.                  |")
print("|             ¡Tanto como un viaje en bici!                    |")
print("|                                                              |")
print("                            Script por lordjimbo@protonmail.com ")
print(" comparamos bicis sacadas con bicis dejadas, junto con la duracion")
print(" del trayecto estimada por la API de la EMT")
print("_____________________[DEBUGING OUTPUTS]_____________________________\n")

ends = []
travels = []
stations = get_stat_by_id()
while(True):
    a = get_all_stations()
    change = 0
    for i in a:
        s_id = i["id"]
        if stations[s_id]["dock_bikes"] == (i["dock_bikes"] -1) :
            start = bikeStamp(s_id)
            sta_c = bikeStamp(s_id)
            travels.append(travel(start, sta_c))
            change += 1
        if stations[s_id]["free_bases"] == (i["free_bases"] -1) :
            ends.append(bikeStamp(s_id))
            change += 1
    if change != 0:
        stations = get_stat_by_id()
        travels = getPossibleTravels_t(travels,ends)
        ends = []
        if len(travels) > 0:
            travels = sorted(travels, key=travel.getProb, reverse=True)
            clearscreen()   
            print("Estas son las mejores sugerencias de viajes (Dale tiempo para que muestre algo razonable):" )
            [print(f'[{i}] {e}') for i, e in enumerate(travels)]
            print("_____________________[DEBUGING OUTPUTS]_____________________________\n")
            