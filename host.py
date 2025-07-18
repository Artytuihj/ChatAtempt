import requests

SERVER = ""

def init(server_url):
    SERVER = server_url


def register():
    url = f"{SERVER}/reg"
    data = {
        "room_code": "ABCD1234",
        "port": 5555
    }
    response = requests.post(url, json=data)
    print("Status Code:", response.status_code)
    print("Response:", response.json())