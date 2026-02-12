import requests
import json
import logging



class RegServerTransporter:
    def __init__(self):
        self.SERVER = "http://fanichatatmept.duckdns.org/"
        self.logger = logging.getLogger("[RegServerTransporter]")
        self.logger.setLevel(logging.DEBUG)

    def register(self, code, offer_sdp, offer_type):
        payload = {
            "room_code": code,
            "offer_sdp": offer_sdp,
            "offer_type":offer_type
        }
        try:
            response = requests.get(f"{self.SERVER}/reg", json=payload, timeout=10)
            self.logger.info(f"[OfferReceiver] {self.SERVER}/reg json={payload}")
            if response.ok:
                try:
                    data = response.json()
                    self.logger.info("[OfferReceiver] Received Answer data:", data)
                    return data
                except json.JSONDecodeError:
                    self.logger.warning("[OfferReceiver] Server responded but did not send JSON.")
                    self.logger.warning("[OfferReceiver] Raw response:", response.text)
            else:
                self.logger.error(f"[OfferReceiver] Server returned error {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            self.logger.warning(f"[OfferReceiver] Request failed: {e}")

    #def bs(self, port, code):
        #"""Register room code and offer with central server."""
        #data_to_send = {
         #   "room_code": code,
        #    "port": port
        #}

        #self.logger.info(f"[register] Sending registration to {self.SERVER}/reg with: {data_to_send}")
        #try:
           # response = requests.post(f"{self.SERVER}/reg", json=data_to_send)
           # self.logger.info(f"[register] POST {self.SERVER}/reg → Status: {response.status_code}")

            #if response.ok:
             #   try:
              #      self.logger.info(f"[register] JSON Response: {response.json()}")
              #  except json.JSONDecodeError:
              #      self.logger.warning("[register] Server responded but did not return JSON.")
              #      self.logger.warning("Raw response:", response.text)
            #else:
             #   self.logger.error(f"[register] Server returned error {response.status_code}.")
             #   self.logger.error("Error content:", response.text)

       # except requests.exceptions.RequestException as e:
          #  self.logger.warning(f"[register] Request failed: {e}")