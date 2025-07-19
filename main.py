import requests
import socket
import sys
import UI
from UI import SaladCord
import host
import json
#region variables

VERSION = "0.6.3"
# URL of your Replit server
SERVER = "https://ippointer.onrender.com"
app,window = UI.ui_start()

connected = False
hosting = False
host_ip = ""
host_port = 0

username = "Vladik"
#endregion

def get_ip(code):
    try:
        response = requests.get(f"{SERVER}/get?room_code={code}")
        print(f"{SERVER}/room_code?={code}")
        if response.ok:
            try:
                data = response.json()
                print("Received IP data:", data)
                return data
            except requests.exceptions.JSONDecodeError:
                print("Server responded but did not send JSON.")
                print("Raw response:", response.text)
        else:
            print(f"Server returned error {response.status_code}:")
            print(response.text)

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

def connect(code):
    global host_ip,host_port,username,VERSION,connected
    data = get_ip(code)
    print(1)
    if data:
        host_ip = data["ip"]
        if hosting:
            host_ip = "127.0.0.1"
        host_port = data["port"]
        handshake = {
              "type": "handshake",
              "name": username,
              "version": VERSION
            }
        json_data = json.dumps(handshake).encode()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print(2)
            s.connect((host_ip, host_port))
            s.send(json_data)
            response = s.recv(1024).decode()
            print("Server response:", response)
            connected = True

def setup_host(hostname):
    global VERSION,host_port,host_ip,hosting
    hosting = True
    host_ip,host_port,code = host.setup_host(SERVER,hostname,VERSION)
    connect(code)

#region -----Buttons
def on_send():
    if connected:
        text = window.prompt.toPlainText()
        window.send_message("You", text,6)

button_actions = {
        "send": on_send
    }
def proces_button(action_id: str):
    action = button_actions.get(action_id)
    if action:
        action()

    else:
        print("No action is bound to this id or id dosent exist")
#endregion

window.buttonEvent.connect(proces_button)
setup_host("server")
sys.exit(app.exec())