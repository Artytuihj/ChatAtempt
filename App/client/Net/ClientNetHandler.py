import json, queue, threading

from pygame.examples.video import answer

from App.client.Net.RegServerTransporter import RegServerTransporter as regServer
from aiortc import  RTCPeerConnection, RTCSessionDescription
import logging


class ClientNetHandler:

    def __init__(self, handlerMap, username, VERSION):
        self.connected = False
        self.pc = RTCPeerConnection()
        self.channel = None
        self.msgQueue = queue.Queue()
        self.handlerMap = handlerMap
        self.username = username
        self.VERSION = VERSION
        self.logger = logging.getLogger("[ClientNetHandler]")
        self.logger.setLevel(logging.DEBUG)
        self.regServer = regServer()
        self.dispatchThread = None

    async def Connect(self, code):
        pc = self.pc

        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)

        response = self.regServer.register(code,pc.localDescription.sdp, pc.localDescription.type)
        if not response:
            raise RuntimeError("No answer from signaling server")

        serverAnswer = RTCSessionDescription(sdp=response["answer_sdp"], type=response["answer_type"])
        await pc.setRemoteDescription(serverAnswer)


        @pc.on("datachannel")
        def OnConnectionEstablished( channel):
            self.channel = channel
            self.logger.info("[OnConnectionEstablished] early connection established sending handshake")
            handshake = {"type": "handshake", "name": self.username, "version": self.VERSION, "status":"request"}
            if self.channel:
                self.channel.send(json.dumps(handshake))
                self.dispatchThread = threading.Thread(target=self.Dispatch(), daemon=True).start()
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
                        msg = {"type": "raw", "cont": data}
                        self.logger.warning(f"[OnIncomingData] Invalid JSON: {data}")

                    if not isinstance(msg, dict):
                        msg = {"type": "raw", "cont": msg}
                        self.logger.warning(f"[OnIncomingData] Received not-a-dict message, wrapping: {msg}")

                    if self.connected:
                        self.logger.info(msg)
                        self.msgQueue.put(msg)
                    else:
                        if msg["type"] == "handshake":
                            self.logger.info("[OnIncomingData] handshake received processing")
                            if msg["version"] == self.VERSION:
                                self.logger.info("[OnIncomingData] handshake version is matching")
                                if msg["status"] == "accept":
                                    self.logger.info("[OnIncomingData] handshake accepted")
                                    self.connected = True
                                elif msg["status"] == "declined":
                                    self.logger.info("[OnIncomingData] handshake declined closing data channel")
                                    self.closeConnection("handshake declined by server")
                                    return
                        elif msg.get("type") == "raw":
                            content = msg.get("cont")
                            self.logger.warning(
                                f"[OnIncomingData] Raw message received, attempting recovery: {content}")

                            try:
                                recovered = json.loads(content)
                                if isinstance(recovered, dict) and recovered.get("type") == "handshake":
                                    self.logger.info("[OnIncomingData] Recovered a handshake from raw message, processing")
                                    if msg["version"] == self.VERSION:
                                        self.logger.info("[OnIncomingData] handshake version is matching")
                                        if msg["status"] == "accept":
                                            self.logger.info("[OnIncomingData] handshake accepted")
                                            self.connected = True
                                        elif msg["status"] == "declined":
                                            self.logger.info("[OnIncomingData] handshake declined closing data channel")
                                            self.closeConnection("handshake declined by server")
                            except Exception:
                                self.logger.warning(
                                    "[OnIncomingData] Could not recover anything from raw message, skipping")
                        else:
                            self.logger.warning(f"[OnIncomingData] raw unknown package received: {msg}")
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
        code = host.setup_host(hostname)
        self.Connect(code)

    def closeConnection(self, reason):
        self.logger.warning(reason)
        self.channel.close()
        self.dispatchThread.stop()
        self.connected = False
