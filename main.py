# ==== Imports ====
import socket
import threading
import json
import requests

# Internal imports
import UI
from UI import SaladCord
from host import HostHandler


# ==== Main Application ====
class MainApp:
    def __init__(self):
        # ---- Basic Config ----
        self.VERSION = "0.7.0"
        self.SERVER = "https://ip-pointer.onrender.com/"

        # ---- Networking ----
        self.sock = None
        self.connected = False
        self.hosting = False
        self.host_ip = ""
        self.host_port = 0
        self.username = "Vladik"

        # ---- UI ----
        self.app, self.window = UI.ui_start()
        self.window.buttonEvent.connect(self.process_button)

        # ---- Hosting ----
        self.host = HostHandler(self.SERVER, self.VERSION)

        # ---- Button actions ----
        self.button_actions = {
            "send": self.send_message,
            "host": self.setup_host,
            "connReq": self.connectRequest,
            "conn": self.connectRequest,
        }

    # =========================
    # ---- Networking: Client ----
    # =========================
    def get_ip(self, code):
        """Fetch IP + port from server using room code."""
        try:
            response = requests.get(f"{self.SERVER}/get?room_code={code}")
            print(f"{self.SERVER}/get?room_code={code}")
            if response.ok:
                try:
                    data = response.json()
                    print("Received IP data:", data)
                    return data
                except json.JSONDecodeError:
                    print("Server responded but did not send JSON.")
                    print("Raw response:", response.text)
            else:
                print(f"Server returned error {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")

    def connectRequest(self):
        if self.connected != True:
            self.window.regWindowEvent.emit()

    def connect(self, code = None):
        if self.connected == True: return

        if code == None:
            code = self.window.codePrompt.toPlainText()

        data = self.get_ip(code)
        if data:
            host_ip = data.get("ip")
            host_port = data.get("port")

            if not host_ip or not host_port:
                print("Invalid server response (missing ip/port).")
                return

            if self.hosting and code == self.host.code:
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

    def listen_server_loop(self):
        """Background loop for receiving server messages."""
        print("[listen_server_loop] Listening to server...")
        while self.connected:
            print("200")
            try:
                data = self.sock.recv(1024)
                if not data:
                    break
                print("[listen_server_loop] code: recv1 message received decoding")
                try:
                    print(data.decode())
                    msg = json.loads(data.decode())
                except json.JSONDecodeError:
                    print(f"[listen_server_loop] Invalid JSON from server: {data}")
                    continue

                if msg.get('type') == "mirormsg":
                    self.window.msgEvent.emit(self.username, msg.get("cont"), 3,False)
                    print(f"[listen_server_loop] code: recv2 message received with contents: {msg.get("cont")}")
                else:
                    print(f"[listen_server_loop] code: recv2 message received with contents: {msg}")

            except Exception as e:
                print(f"[listen_server_loop] Error receiving message: {e}")
                break

    # =========================
    # ---- Networking: Hosting ----
    # =========================
    def setup_host(self, hostname = "Server"):
        self.hosting = True
        self.host_ip, self.host_port, code = self.host.setup_host(hostname)
        self.connect(code)

    # =========================
    # ---- UI Actions ----
    # =========================
    def send_message(self):
        """Send a chat message to server/host."""
        if self.connected:
            text = self.window.prompt.toPlainText()
            if text == "": return
            msg = {
                "type": "msgtxt",
                "cont": text
            }
            json_data = json.dumps(msg).encode()
            try:
                self.sock.send(json_data)
            except Exception as e:
                print(f"Failed to send message: {e}")
        else:
            print("Not connected to any host!")
    def process_button(self, action_id: str):
        """Map button clicks to actions."""
        action = self.button_actions.get(action_id)
        if action:
            action()
        else:
            print("No action is bound to this id or id doesn't exist")


# ==== Run App ====
if __name__ == "__main__":
    app = MainApp()
    #app.setup_host("server")
    app.app.exec()
