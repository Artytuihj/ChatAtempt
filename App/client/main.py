# ==== Imports ====
import json

from win32com.server.policy import regSpec

import App.Net.general.RegServerTransporter
# Internal imports
from App.client import UI
from App.server.host import HostHandler
from App.Net.client.ClientNetHandler import ClientNetHandler as clientNet
from App.Net.general.RegServerTransporter import  RegServerTransporter as RegServer



# ==== Main Application ====
class MainApp:
    def __init__(self):
        # ---- Basic Config ----
        self.VERSION = "0.7.0"
        # ---- UI ----
        self.app, self.window = UI.ui_start()
        self.window.buttonEvent.connect(self.process_button)

        # ---- Hosting ----
        self.host = HostHandler(self.VERSION)

        # ---- Networking ----
        self.username = "Vladik"
        self.handlerMap = {
            "mirormsg": self.accseptMsg,  # {"type":"msgrecv", "msgid":45}
        }
        self.net = clientNet(self.handlerMap)

        # ---- Button actions ----
        self.button_actions = {
            "send": self.send_message,
            "host": self.setup_host,
            "connReq": self.connectRequest,
            "conn": self.net.connect,
        }

    # =========================
    # ---- Networking: Client ----
    # =========================
    def connectRequest(self, Value):
        if not self.net.connected:
                self.window.regWindowEvent.emit()

    # =========================
    # ---- Networking: Hosting ----
    # =========================
    def setup_host(self, hostname = "Server"):
        self.net.setup_host(hostname, self.host)

    # =========================
    # ---- UI Actions ----
    # =========================
    def send_message(self, text):
        """Send a chat message to server/host."""
        if self.connected:
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
    def accseptMsg(self, *args):
        msg = args[0]
        self.window.msgEvent.emit(self.username, msg.get("cont"), 3, False)


# ==== Run App ====
if __name__ == "__main__":
    app = MainApp()
    #app.setup_host("server")
    app.app.exec()
