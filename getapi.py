import requests
import json 

user = "lordjimbo@protonmail.com"
pwd = "Eliseoynicolas0"
url = "https://openapi.emtmadrid.es/v1/mobilitylabs/user/login/"

reply = requests.get(url, headers = {"email": user, "password":pwd})

content = reply.json()

with open("apikey.json", "w+") as f:
    json.dump(content, f)
