import requests
import socket
import json
import random
import string
import threading

class HostHandler:
    def __init__(self, server_url, version):
        self.VERSION = version
        self.SERVER = server_url
        self.hostname = "Undefined"
        self.hosting = False
        self.code = ""
        self.s = None
        self.clients = {}

    def generate_scramble(self, length=5):
        scramble = ''.join(random.choice(string.ascii_uppercase) for _ in range(length))
        print(f"[generate_scramble] Generated room code: {scramble}")
        return scramble

    def register(self, port):
        data_to_send = {
            "room_code": self.code,
            "port": port
        }

        print(f"[register] Sending registration to {self.SERVER}/reg with: {data_to_send}")
        try:
            response = requests.post(f"{self.SERVER}/reg", json=data_to_send)
            print(f"[register] POST {self.SERVER}/reg → Status: {response.status_code}")

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

    def handle_clien(self,clientSock,clientAdd):
        print(f"[Client Handler] Started thread for client: {clientAdd}")
        clientSock.settimeout(None)
        try:
            while self.hosting:
                try:
                    data = clientSock.recv(1024).decode()
                    if not data:
                        print(f"[handle_client] {clientAdd} disconnected")
                        break

                    try:
                        msg = json.loads(data)
                    except json.JSONDecodeError:
                        print(f"[handle_client] Invalid JSON from {clientAdd}: {data}")
                        continue

                    if msg.get("type") == "msgtxt":
                        sender = self.clients.get(clientAdd,"Undefined")
                        print(f"[handle_client] Message from {sender}: {msg.get('cont')}")
                        clientSock.send("msg recv".encode())
                    else:
                        clientSock.send("Un req".encode())


                except ConnectionResetError:
                    print(f"[handle_client] Connection reset by {clientAdd}")
                    break
        finally:
            clientSock.close()
            if clientAdd in self.clients:
                del self.clients[clientAdd]
            print(f"[handle_client] Thread for {clientAdd} exiting")


    def handle_clients_connection(self):
        print("[handle_clients] Hosting loop started.")
        while self.hosting:
            try:
                print("[handle_clients] Waiting for connection...")
                client_socket, client_address = self.s.accept()
                print(f"[handle_clients] Connection from {client_address}")

                client_socket.settimeout(60)
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

                if client_address in self.clients:
                    print(msg)
                    print("!!!!Unexpected Behavior message not renderd!!!!")
                    client_socket.send("800".encode())
                    client_socket.close()
                elif msg.get("type") == "handshake":
                    if "name" in msg and "version" in msg:
                        print(f"[handle_clients] Handshake from {msg['name']} version {msg['version']}")
                        if msg.get("version") == self.VERSION:
                            self.clients[client_address] = msg['name']
                            client_socket.send("Handshake accepted".encode())
                            thread = threading.Thread(target=self.handle_clien,args=(client_socket,client_address), daemon=True)
                            thread.start()
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

    def start_hosting_thread(self):
        print("[start_hosting_thread] Starting thread...")
        thread = threading.Thread(target=self.handle_clients_connection, daemon=True)
        thread.start()
        print("[start_hosting_thread] Thread started.")

    def setup_host(self,hostname):
        print("[setup_host] Creating socket...")
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('0.0.0.0', 0))
        ip, port = self.s.getsockname()
        print(f"[setup_host] Socket bound to 0.0.0.0:{port}")
        self.s.listen(2)
        print("[setup_host] Socket now listening...")

        self.code = self.generate_scramble()
        self.register(port)

        self.hostname = hostname
        self.hosting = True
        self.start_hosting_thread()

        print(f"[setup_host] Hosting ready. IP: {ip}, Port: {port}, Code: {self.code}")
        return ip, port, self.code

    def close_host(self):
        print("[close_host] Closing host...")
        self.hosting = False
        if self.s:
            self.s.close()
            print("[close_host] Socket closed.")
