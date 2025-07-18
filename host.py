import requests
import socket
import json  # Needed for JSON handling
import random
import string

SERVER = ""
hosting = False
hostname = ""
s = None
code = ""
def generate_scramble(length=5):
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(length))

def register(port, url, code):
    data = {
        "room_code": code,
        "port": port
    }
    response = requests.post(url, json=data)
    print("Status Code:", response.status_code)
    print("Response:", response.json())

def setup_host(server_url, servername):
    global hosting, SERVER, s, code, hostname
    SERVER = server_url
    hostname = servername
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', 0))
    ip, port = s.getsockname()
    s.listen(2)
    code = generate_scramble
    register(port, SERVER,code)
    hosting = True
    return ip, port,code

def close_host():
    global hosting
    hosting = False

while hosting:
    client_socket, client_address = s.accept()
    print(f"Connection from {client_address}")

    try:
        data = client_socket.recv(1024).decode()
        # Try to parse handshake JSON
        handshake = json.loads(data)

        # You can check keys inside handshake to verify
        if "client_name" in handshake and "app_version" in handshake:
            print(f"Handshake received from {handshake['client_name']} version {handshake['app_version']}")
            client_socket.send("Handshake accepted".encode())
        else:
            print("Invalid handshake data, closing connection.")
            client_socket.close()
            continue

        while True:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            print(f"Received message from {handshake['client_name']}: {message}")
            client_socket.send(f"Server received: {message}".encode())

    except json.JSONDecodeError:
        print("Failed to decode handshake JSON, closing connection.")
        client_socket.close()
