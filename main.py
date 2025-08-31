import requests
import socket
import threading
import json
import UI
from UI import SaladCord
from host import HostHandler

class mainApp():
    def __init__(self):
        self.VERSION = "0.6.8"
        self.SERVER = "https://ippointer.onrender.com"
        self.s = None
        self.app, self.window = UI.ui_start()

        self.host = HostHandler(self.SERVER,self.VERSION)

        self.connected = False
        self.hosting = False
        self.host_ip = ""
        self.host_port = 0
        self.username = "Vladik"


        # Button actions
        self.window.buttonEvent.connect(self.process_button)

        self.button_actions = {
            "send": self.on_send
        }

    def get_ip(self, code):
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

    def connect(self, code):
        data = self.get_ip(code)
        if data:
            host_ip = data["ip"]
            if self.hosting and code == self.host.code:
                host_ip = "127.0.0.1"
            host_port = data["port"]
            handshake = {
                "type": "handshake",
                "name": self.username,
                "version": self.VERSION
            }
            json_data = json.dumps(handshake).encode()
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.s.connect((host_ip, host_port))
                self.s.send(json_data)
                response = self.s.recv(1024).decode()
                print("Server response:", response)
                thread = threading.Thread(target=self.listen_to_server, daemon=True)
                thread.start()
                self.connected = True
            except Exception as e:
                print(f"Failed to connect: {e}")

    def listen_to_server(self):
        while self.connected:
            try:
                data = self.s.recv(1024)
                if not data:
                    break
                msg = json.loads(data.decode())

                if msg.get("mirormsg"):

            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    def setup_host(self, hostname):
        self.hosting = True
        self.host_ip, self.host_port, code = self.host.setup_host(hostname)
        self.connect(code)

    # -----Buttons
    def on_send(self):
        if self.connected:
            text = self.window.prompt.toPlainText()
            msg = {
                "type":"msgtxt",
                "cont":text
            }
            json_data = json.dumps(msg).encode()
            try:
                self.s.send(json_data)
            except Exception as e:
                print(f"Failed To send message: {e}")
        else:
            print("Not connected to any host!")

    def process_button(self, action_id: str):
        action = self.button_actions.get(action_id)
        if action:
            action()
        else:
            print("No action is bound to this id or id doesn't exist")


app = mainApp()
app.setup_host("server")
app.app.exec()