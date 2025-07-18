import requests
import socket

SERVER = ""

def setup_host(server_url,hostname):
    SERVER = server_url
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', 0))
    ip,port = s.getsockname()

    s.listen(2)


    return ip,port

def register():
    url = f"https://ippointer.onrender.com/reg"
    data = {
        "room_code": "ABCD1234",
        "port": 5555
    }
    response = requests.post(url, json=data)
    print("Status Code:", response.status_code)
    print("Response:", response.json())

register()