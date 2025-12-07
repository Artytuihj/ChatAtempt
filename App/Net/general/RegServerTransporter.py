import requests
import json

class RegServerTransporter:
    def __init__(self):
       self.SERVER = "https://ip-pointer.onrender.com/"

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

    def register(self, port):
        """Register room code and port with central server."""
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
                except json.JSONDecodeError:
                    print("[register] Server responded but did not return JSON.")
                    print("Raw response:", response.text)
            else:
                print(f"[register] Server returned error {response.status_code}.")
                print("Error content:", response.text)

        except requests.exceptions.RequestException as e:
            print(f"[register] Request failed: {e}")