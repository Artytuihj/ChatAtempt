# ==== Imports ====
import requests
import socket
import json
import random
import string
import threading
from App.Net.general.RegServerTransporter import  RegServerTransporter as RegServer


# ==== Host Handler ====
class HostHandler:
    def __init__(self, version):
        # ---- Basic Config ----
        self.VERSION = version
        self.hostname = "Undefined"
        self.hosting = False
        self.code = ""

        # ---- Networking ----
        self.sock = None
        self.clients = {}    # { address: {"name": str, "sock": socket} }

    # =========================
    # ---- Setup & Teardown ----
    # =========================
    def setup_host(self, hostname):

        print("[setup_host] Creating socket...")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('0.0.0.0', 0))
        ip, port = self.sock.getsockname()
        print(f"[setup_host] Socket bound to 0.0.0.0:{port}")
        self.sock.listen(2)
        print("[setup_host] Socket now listening...")

        self.code = self.generate_scramble()
        RegServer.register(port)

        self.hostname = hostname
        self.hosting = True
        self.start_hosting_thread()

        print(f"[setup_host] Hosting ready. IP: {ip}, Port: {port}, Code: {self.code}")
        return ip, port, self.code
    def close_host(self):
        """Stop hosting and close socket."""
        print("[close_host] Closing host...")
        self.hosting = False
        if self.sock:
            self.sock.close()
            print("[close_host] Socket closed.")

    # =========================
    # ---- Registration ----
    # =========================
    def generate_scramble(self, length=16):
        """Generate a random uppercase room code."""
        scramble = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))
        print(f"[generate_scramble] Generated room code: {scramble}")
        return scramble


    # =========================
    # ---- Client Handling ----
    # =========================
    def handle_client(self, client_sock, client_addr):
        """Handle a connected client (threaded)."""
        print(f"[handle_client] Started thread for client: {client_addr}")
        client_sock.settimeout(None)

        try:
            while self.hosting:
                try:
                    data = client_sock.recv(1024).decode()
                    if not data:
                        print(f"[handle_client] {client_addr} disconnected")
                        break

                    try:
                        msg = json.loads(data)
                    except json.JSONDecodeError:
                        print(f"[handle_client] Invalid JSON from {client_addr}: {data}")
                        continue

                    if msg.get("type") == "msgtxt":
                        sender = self.clients.get(client_addr, {}).get("name", "Undefined")
                        print(f"[handle_client] Message from {sender}: {msg.get('cont')}")
                        status = self.broadcast(json.dumps({
                            "type": "mirormsg",
                            "cont": msg.get("cont")
                        }))
                        if status != 0:
                            client_sock.send(json.dumps({"type":"msgrecv", "msgid":45}).encode())
                        else:
                            print("[handle_client][Broadcast] Failed to mirror message")
                    else:
                        client_sock.send("406".encode())

                except ConnectionResetError:
                    print(f"[handle_client] Connection reset by {client_addr}")
                    break
        finally:
            client_sock.close()
            if client_addr in self.clients:
                del self.clients[client_addr]
            print(f"[handle_client] Thread for {client_addr} exiting")

    def broadcast(self, msg):
        """Send message to all connected clients."""
        print("[broadcast] Attempting...")
        for addr, data in list(self.clients.items()):
            try:
                data["sock"].send(msg.encode())
                print(f"[broadcast] Sent to {addr} ({data['name']})")
                return 1
            except Exception as e:
                print(f"[broadcast] Error sending to {addr} ({data.get('name')}): {e}")
                return 0

    def handle_clients_connection(self):
        """Main server loop: accept clients and perform handshake."""
        print("[handle_clients] Hosting loop started.")
        while self.hosting:
            try:
                print("[handle_clients] Waiting for connection...")
                client_sock, client_addr = self.sock.accept()
                print(f"[handle_clients] Connection from {client_addr}")

                client_sock.settimeout(60)
                try:
                    data = client_sock.recv(1024).decode()
                    print(f"[handle_clients] Received raw data: {data}")
                except socket.timeout:
                    print("[handle_clients] ERROR: Client sent nothing in 60s.")
                    client_sock.close()
                    continue

                try:
                    msg = json.loads(data)
                    print(f"[handle_clients] Parsed JSON: {msg}")
                except json.JSONDecodeError:
                    print("[handle_clients] ERROR: Failed to decode handshake JSON.")
                    client_sock.close()
                    continue

                # ---- Handshake ----
                if client_addr in self.clients:
                    print("[handle_clients] ERROR: Duplicate client connection.")
                    client_sock.send("800".encode())
                    client_sock.close()
                elif msg.get("type") == "handshake":
                    if "name" in msg and "version" in msg:
                        print(f"[handle_clients] Handshake from {msg['name']} v{msg['version']}")
                        if msg.get("version") == self.VERSION:
                            self.clients[client_addr] = {
                                "name": msg["name"],
                                "sock": client_sock
                            }
                            client_sock.send("Handshake accepted".encode())
                            thread = threading.Thread(
                                target=self.handle_client,
                                args=(client_sock, client_addr),
                                daemon=True
                            )
                            thread.start()
                            print(f"[handle_clients] Handshake accepted for {msg['name']}")
                        else:
                            print("[handle_clients] ERROR: Invalid version.")
                            client_sock.send("Invalid Version".encode())
                            client_sock.close()
                    else:
                        print("[handle_clients] ERROR: Invalid handshake structure.")
                        client_sock.send("Invalid handshake".encode())
                        client_sock.close()
                else:
                    print("[handle_clients] ERROR: Unknown message type.")
                    client_sock.send("Unknown request".encode())
                    client_sock.close()

            except OSError:
                print("[handle_clients] Socket closed, exiting loop.")
                break

    # =========================
    # ---- Threads ----
    # =========================
    def start_hosting_thread(self):
        """Run hosting loop in a background thread."""
        print("[start_hosting_thread] Starting thread...")
        thread = threading.Thread(target=self.handle_clients_connection, daemon=True)
        thread.start()
        print("[start_hosting_thread] Thread started.")
