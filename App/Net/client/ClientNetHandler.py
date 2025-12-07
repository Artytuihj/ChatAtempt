import json
import queue
import socket
import threading
from App.Net.general.RegServerTransporter import RegServerTransporter as regServer

class ClientNetHandler:

    def __init__(self, handlerMap, username, VERSION):
        self.connected = False
        self.sock = None
        self.hosting = False
        self.host_ip = ""
        self.host_port = 0
        self.msgQueue = queue.Queue()
        self.handlerMap = handlerMap
        self.username = username
        self.VERSION = VERSION

    def ReceiveLoop(self):
        print("[ReceiveLoop] Listening to server...")
        while self.connected:
            try:
                data = self.sock.recv(1024)
                if not data:
                    print("[ReceiveLoop] Connection closed by server")
                    self.connected = False
                    break
                try:
                    msg = json.loads(data.decode())
                except json.JSONDecodeError:
                    print(f"[ReceiveLoop] Invalid JSON: {data}")
                    continue  # skip this message
                if not isinstance(msg, dict):
                    print(f"[ReceiveLoop] Received not-a-dict message, wrapping: {msg}")
                    msg = {"type": "raw", "cont": msg}  # wrap string messages safely
                self.msgQueue.put(msg)
            except Exception as e:
                print(f"[ReceiveLoop] Error receiving message: {e}")
                self.connected = False
                break

    def Dispatch(self):
        """Process messages from the queue."""
        while self.connected:
            try:
                msg = self.msgQueue.get(timeout=0.1)

                action = self.handlerMap.get(msg["type"])
                if action:
                    argsList = [v for k, v in msg.items() if k != "type"]
                    action(*argsList)
                else:
                    print(f"[Dispatcher] No handler for msg type: {msg.get('type')}")
            except queue.Empty:
                continue

    def connect(self, code=None):
        if self.connected:
            return

        if code is None:
            code = input("Enter server code: ")

        try:
            data = regServer().get_ip(code)
            if not data:
                print("[connect] Failed to get IP from server")
                return

            host_ip = data.get("ip")
            host_port = data.get("port")
            if not host_ip or not host_port:
                print("[connect] Invalid server response (missing ip/port).")
                return

            if self.hosting:
                host_ip = "127.0.0.1"

            handshake = {"type": "handshake", "name": self.username, "version": self.VERSION}
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host_ip, host_port))
            self.sock.send(json.dumps(handshake).encode())
            response = self.sock.recv(1024).decode()
            print("Server response:", response)

            # Start background threads
            self.connected = True
            threading.Thread(target=self.ReceiveLoop, daemon=True).start()
            threading.Thread(target=self.Dispatch, daemon=True).start()

        except Exception as e:
            print(f"[connect] Failed: {e}")

    def setup_host(self, hostname, host):
        self.hosting = True
        self.host_ip, self.host_port, code = host.setup_host(hostname)
        self.connect(code)
