import requests
import socket
import sys
import UI
from UI import SaladCord
import host

# URL of your Replit server
SERVER = "https://ippointer.onrender.com"
app,window = UI.ui_start()

connected = False
hosting = False
host_ip = ""
host_port = 0


def get_ip(code):
    url = f"{SERVER}/get?room_code={code}"
    response = requests.get(url)
    print(response.status_code)
    print(response.json())
def setup_host(hostname):
    host_ip,host_port = host.setup_host(SERVER,hostname)


#region -----Buttons
def on_send():
    if connected:
        text = window.prompt.toPlainText()
        window.send_message("You", text,6)

button_actions = {
        "send": on_send
    }
def proces_button(msg_id: str):
    print("1")
    action = button_actions.get(msg_id)
    if action:
        action()

    else:
        print("No action is bound to this id or id dosent exist")
#endregion





window.buttonEvent.connect(proces_button)
sys.exit(app.exec())