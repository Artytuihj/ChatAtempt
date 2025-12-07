import json
import queue
import socket
import threading
from App.Net.general.RegServerTransporter import RegServerTransporter as regServer

from sympy.codegen import While


class ClientNetHandler:

    def __init__(self, handlerMap):
        self.connected = False
        self.sock = None
        self.hosting = False
        self.host_ip = ""
        self.host_port = 00000
        self.msgQueue = queue.Queue()
        self.handlerMap = handlerMap



    def ReceiveLoop(self):
        """Background loop for receiving server messages."""
        print("[ReceiveLoop] Listening to server...")
        while self.connected:
            try:
                data = self.sock.recv(1024)
                if not data:
                    print(f"[ReceiveLoop] ReceiveLoop terminated")
                    break
                print("[ReceiveLoop] code: recv1 message received decoding")
                try:
                    msg = json.loads(data.decode())
                    self.msgQueue.put(msg)
                except json.JSONDecodeError:
                    print(f"[ReceiveLoop] Invalid JSON from server: {data}")
                    continue
            except Exception as e:
                print(f"[ReceiveLoop] Error receiving message: {e}")
                print(f"[ReceiveLoop] ReceiveLoop terminated")
                break

    def Dispatch(self, msg):
        while True:
            try:
                msg = self.msgQueue.get(timeout=0.1)

                print(f"[Dispatcher] code: recv2 message received with contents: {msg.get("cont")}")

                action = self.handlerMap.get(msg["type"])
                if action:

                    print(f"[Dispatcher] popped queue starting dispatch")

                    argsList = []
                    for key, value in msg.items():
                        if key != "type":
                            argsList.append(value)

                    action(*argsList)
                else:
                    print(f"[Dispatcher] code: recv2 message received but no action attached: {msg}")
            except self.msgQueue.empty():
                pass

    def connect(self, code = None):
        if self.connected: return

        if code == None:
            code = input("no code provided. Enter Code:")

        data = regServer.get_ip(code)
        if data:
            host_ip = data.get("ip")
            host_port = data.get("port")

            if not host_ip or not host_port:
                print("Invalid server response (missing ip/port).")
                return

            if self.hosting:
                host_ip = "127.0.0.1"

            handshake = {
                "type": "handshake",
                "name": self.username,
                "version": self.VERSION
            }
            json_data = json.dumps(handshake).encode()

            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.sock.connect((host_ip, host_port))
                self.sock.send(json_data)
                response = self.sock.recv(1024).decode()
                print("Server response:", response)

                thread = threading.Thread(target=self.listen_server_loop, daemon=True)
                thread.start()
                self.connected = True
            except Exception as e:
                print(f"Failed to connect: {e}")

    def setup_host(self, hostname, host):
        self.hosting = True
        self.host_ip, self.host_port, code = host.setup_host(hostname)
        self.connect(code)
