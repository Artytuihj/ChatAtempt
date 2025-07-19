import requests
import socket
import json
import random
import string
import threading

VERSION = "0.0.0"
SERVER = ""
hosting = False
hostname = ""
s = None
code = ""
clients = {}

def generate_scramble(length=5):
    scramble = ''.join(random.choice(string.ascii_uppercase) for _ in range(length))
    print(f"[generate_scramble] Generated room code: {scramble}")
    return scramble

def register(port, url, room_code):
    data_to_send = {
        "room_code": room_code,
        "port": port
    }

    print(f"[register] Sending registration to {url}/reg with: {data_to_send}")
    try:
        response = requests.post(f"{url}/reg", json=data_to_send)
        print(f"[register] POST {url}/reg → Status: {response.status_code}")

        if response.ok:
            try:
                print(f"[register] JSON Response: {response.json()}")
            except requests.exceptions.JSONDecodeError:
                print("[register] Server responded but did not return JSON.")
                print("Raw response:", response.text)
        else:
            print(f"[register] Server returned error status {response.status_code}.")
            print("Error content:", response.text)

    except requests.exceptions.RequestException as e:
        print(f"[register] Request failed: {e}")

def handle_clients():
    print("[handle_clients] Hosting loop started.")
    global hosting, s, clients
    while hosting:
        try:
            print("[handle_clients] Waiting for connection...")
            client_socket, client_address = s.accept()
            print(f"[handle_clients] Connection from {client_address}")

            client_socket.settimeout(5)
            try:
                print("[handle_clients] Awaiting data from client...")
                data = client_socket.recv(1024).decode()
                print(f"[handle_clients] Received raw data: {data}")
            except socket.timeout:
                print("[handle_clients] ERROR: Client connected but sent nothing within 5 seconds.")
                client_socket.close()
                continue

            try:
                msg = json.loads(data)
                print(f"[handle_clients] Parsed JSON: {msg}")
            except json.JSONDecodeError:
                print("[handle_clients] ERROR: Failed to decode handshake JSON, closing connection.")
                client_socket.close()
                continue

            if client_address in clients:
                print(f"[handle_clients] Existing client {client_address} says: {msg}")
            elif msg.get("type") == "handshake":
                if "name" in msg and "version" in msg:
                    print(f"[handle_clients] Handshake from {msg['name']} version {msg['version']}")
                    if msg.get("version") == VERSION:
                        clients[client_address] = msg['name']
                        client_socket.send("Handshake accepted".encode())
                        print(f"[handle_clients] Handshake accepted for {msg['name']}")
                    else:
                        print("[handle_clients] ERROR: Invalid version.")
                        client_socket.send("Invalid Version".encode())
                        client_socket.close()
                else:
                    print("[handle_clients] ERROR: Invalid handshake structure.")
                    client_socket.send("Invalid handshake".encode())
                    client_socket.close()
            else:
                print("[handle_clients] ERROR: Unknown message type.")
                client_socket.send("Unknown request".encode())
                client_socket.close()

        except OSError:
            print("[handle_clients] Socket closed, exiting loop.")
            break

def start_hosting_thread():
    print("[start_hosting_thread] Starting thread...")
    thread = threading.Thread(target=handle_clients, daemon=True)
    thread.start()
    print("[start_hosting_thread] Thread started.")

def setup_host(server_url, servername, version):
    global hosting, SERVER, s, code, hostname, VERSION
    print("[setup_host] Starting setup...")
    VERSION = version
    SERVER = server_url
    hostname = servername

    print("[setup_host] Creating socket...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', 0))
    ip, port = s.getsockname()
    print(f"[setup_host] Socket bound to 0.0.0.0:{port}")
    s.listen(2)
    print("[setup_host] Socket now listening...")

    code = generate_scramble()
    register(port, SERVER, code)

    hosting = True
    start_hosting_thread()

    print(f"[setup_host] Hosting ready. IP: {ip}, Port: {port}, Code: {code}")
    return ip, port, code

def close_host():
    global hosting, s
    print("[close_host] Closing host...")
    hosting = False
    if s:
        s.close()
        print("[close_host] Socket closed.")
