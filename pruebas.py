#aqui hacemos las pruebas con python

#este modulo nos permite hacer peticiones por el malvado internet
import requests as req
#el as req nos dice que lo importamos con el nombre req

#este modulo nos permite trabajar con el formato json
import json

"""
lo primero que vamos a hacer es leer el archivo donde tenemos guardados
los datos, que se llama apikey.json e importarlos a este script
"""

api_data_fl = "./apikey.json"
api_data = {}

print(f'[+] Leyendo los datos de nuestras sesion en la api de: {api_data_fl}')

try:
    with open(api_data_fl, "r") as f:
        api_data = json.load(f)
except Exception as e:
    print(f'[!]Error leyendo el archivo: {e}')
    exit(-1)

"""
Ahora vamos a encontrar nuestra apiKey en el archivo
"""

key_json_tag = "accessToken"

key = api_data["data"][0][key_json_tag]

print(f'[+] nuestra clave de sesion es: {key}')

"""
Ahora le vamos a preguntar al servidor de las bicis que quienes somos.
Un whoami de toda la vida
"""
#esta es la url de la api
api_url = "https://openapi.emtmadrid.es/v1/mobilitylabs/"
#este es la url para ejecturar el comando whoami
command = "user/whoami/"

"""
Para hacer la peticion simplemente mandamos la url de api + comando
pero en las cabeceras http incorporamos nuestra apikey
"""

url = api_url + command
head = {"accessToken": key}
#acordaros hemos importado requests como req, get envia peticion get
try:
    print("[+] preguntando a la api quienes somos")
    a = req.get(url, headers=head)
    data = a.json()
    print(f'[+] servidor ha respondido: {json.dumps(data,indent=4,sort_keys=True)}')
except Exception as e:
    print(f'Algo fue mal: {e}')
    exit(-1)

print("Vamos a ver cuantas bicis estan disponibles en cada estacion!")

def parseStationAndPrint(s):
    print(f'[{s["id"]}] En la estacion{s["name"]} quedan {s["dock_bikes"]} porque han cogido {s["free_bases"]}')

try:
    api_url = "https://openapi.emtmadrid.es/v1/"
    url = api_url + "transport/bicimad/stations/"
    a = req.get(url, headers = head)
    for i in a.json()["data"]:
        parseStationAndPrint(i)
except Exception as e:                                                  
    print(f'Algo fue mal: {e}')                                         
    exit(-1)   

