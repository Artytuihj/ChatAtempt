import json , asyncio , queue , socket, threading
from App.Net.general.RegServerTransporter import RegServerTransporter as regServer
from aiortc import  RTCPeerConnection, RTCSessionDescription
import logging


class ClientNetHandler:

    def __init__(self, handlerMap, username, VERSION):
        self.connected = False
        self.pc = RTCPeerConnection()
        self.channel = None
        self.hosting = False
        self.msgQueue = queue.Queue()
        self.handlerMap = handlerMap
        self.username = username
        self.VERSION = VERSION
        self.logger = logging.getLogger("[ClientNetHandler]")
        self.logger.setLevel(logging.DEBUG)
        self.regServer = regServer()

    async def Connect(self, code):
        pc = self.pc
        if not code:
            self.logger.error("[connect] no code provided (yo how tf did this function even run?!)")
            return


        result = self.regServer.getOffer(code)
        if result:
            self.logger.warning(f"[Connect] Server did not return an offer for code {code}")

        offerSdp, offerType = result
        offer = RTCSessionDescription(sdp=offerSdp, type=offerType)
        await self.pc.setRemoteDescription(offer)

        @pc.on("datachannel")
        def OnConnectionEstablished( channel):
            self.channel = channel
            self.logger.info("[OnConnectionEstablished] early connection established sending handshake")
            handshake = {"type": "handshake", "name": self.username, "version": self.VERSION}
            if self.channel:
                self.channel.send(json.dumps(handshake))
                self.logger.info("[OnConnectionEstablished] handshake sent waiting for response")


            @channel.on("message")
            def OnIncomingData(data):
                try:
                    if not data:
                        self.logger.warning("[OnIncomingData] Connection closed by server")
                        return

                    if isinstance(data, bytes):
                        data = data.decode()
                    try:

                        msg = json.loads(data)
                    except json.JSONDecodeError:
                        self.logger.warning(f"[OnIncomingData] Invalid JSON: {data}")
                        msg = {"type": "raw", "cont": data}

                    if not isinstance(msg, dict):
                        self.logger.warning(f"[OnIncomingData] Received not-a-dict message, wrapping: {msg}")
                        msg = {"type": "raw", "cont": msg}
                    self.logger.info(msg)
                    self.msgQueue.put(msg)

                except Exception as e:
                    self.logger.error(f"[OnIncomingData] Error receiving message: {e}")
                    return

    def Dispatch(self):
        while self.connected:
            try:
                msg = self.msgQueue.get(timeout=0.1)

                action = self.handlerMap.get(msg["type"])
                if action:
                    argsList = []
                    for key, value in msg.items():
                        if key != "type":
                            argsList.append(value)

                    self.logger.info(f"[Dispatch] dispatched message: {msg}, to: {action}")
                    action(*argsList)

                else:
                    self.logger.warning(f"[Dispatch] No handler for msg type: {msg.get('type')}")
            except queue.Empty:
                continue

    def setup_host(self, hostname, host):
        self.hosting = True
        code = host.setup_host(hostname)
        self.Connect(code)
