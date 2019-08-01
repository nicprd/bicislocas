"""
Cuando una bici se pierde de algun sitio rastreamos hasta
esperar donde aparece una nueva bici.
Calculamos el tiempo que tarda hasta que aparece una nueva bici
medimos la distancia entre las dos estaciones.
Calculamos si es un tiempo razonable de destino.
Asumimos como destino o seguimos esperando un nuevo destino
"""
import requests as req
import json

def get_api_key():
    with open("../apikey.json", "r") as f:
        api_data = json.load(f)
    key = api_data["data"][0]["accessToken"]
    return {"accessToken" : key}

def get_all_stations():
    api_url = "https://openapi.emtmadrid.es/v1/"
    url = api_url + "transport/bicimad/stations/"
    return req.get(url, headers = get_api_key()).json()["data"]

stations = { i["id"]: [i["dock_bikes"], i["free_bases"]] for i in get_all_stations()}

print("[+] Resgistrando cambios en las estaciones")

while(True):
    for i in get_all_stations():
        if stations[i["id"]][0] == i["dock_bikes"] -1 :
            print(f'[+] una bici se cogio en la estacion {i["name"]}')
        if stations[i["id"]][1] == i["free_bases"] -1:
            print(f'[-] una bici se dejo en la estacion {i["name"]}')
    stations = { i["id"]: [i["dock_bikes"], i["free_bases"]] for i in get_all_stations()}

