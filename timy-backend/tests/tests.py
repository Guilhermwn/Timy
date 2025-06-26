import os
import random
import requests

os.system("cls")

link = "http://127.0.0.1:8000"

def show(info: requests.Response):
    print("---------------")
    print(f"URL: {info.url}")
    print(f"Status Code: {info.status_code}")
    print(f"Resposta: {info.content}")
    print("---------------")

e1 = requests.get(link)
e2 = requests.get(f"{link}/ping")

test_json = [
    {"data":"2025-06-26", "saida_casa":"07:52:00"},
    {"data":"2025-06-26", "chegada_ufs":"11:20:00"},
    {"data":"2025-06-26", "chegada_ufs":"08:15:00"},
    {"data":"2025-06-25", "saida_DIA1":"08:15:00"},
]
e3 = requests.post(f"{link}/add", json=random.choice(test_json))
e4 = requests.get(f"{link}/list")

show(e1)
show(e2)
show(e3)
show(e4)
