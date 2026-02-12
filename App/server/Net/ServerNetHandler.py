from typing import Any, Dict, Optional, Tuple


class ServerNetHandler:
    """
    Skeleton for signaling + host-side WebRTC coordination.
    Fill each method yourself while learning.
    """

    def __init__(self, version: str = "1.0.1") -> None:
        self.VERSION = version
        self.hosting = False
        self.code: Optional[str] = None
        self.hostname: str = "Undefined"
        self.rooms: Dict[str, Dict[str, Any]] = {}

    # =========================
    # ---- Host lifecycle ----
    # =========================
    def setup_host(self, hostname: str) -> str:
        """
        1) Validate hostname.
        2) Generate/store room code.
        3) Mark hosting as active.
        4) Initialize room state.
        5) Return the room code.
        """
        raise NotImplementedError("Implement setup_host()")

    def close_host(self, room_code: str) -> None:
        """
        1) Close peer/data-channel resources for this room.
        2) Remove room from memory.
        3) Update hosting status if no rooms remain.
        """
        raise NotImplementedError("Implement close_host()")

    # =========================
    # ---- Signaling API ----
    # =========================
    def handle_offer(self, room_code: str, offer_sdp: str, offer_type: str) -> Tuple[str, str]:
        """
        Called by your Flask /reg endpoint.

        Expected return:
        (answer_sdp, answer_type)
        """
        raise NotImplementedError("Implement handle_offer()")

    def build_answer_payload(self, answer_sdp: str, answer_type: str) -> Dict[str, str]:
        """
        Convert answer pieces into the JSON shape Flask should return.
        """
        raise NotImplementedError("Implement build_answer_payload()")

    # =========================
    # ---- Validation ----
    # =========================
    def validate_offer(self, room_code: str, offer_sdp: str, offer_type: str) -> None:
        """
        Raise ValueError with clear messages for bad/missing inputs.
        """
        raise NotImplementedError("Implement validate_offer()")

    def room_exists(self, room_code: str) -> bool:
        """
        Return True/False for room existence checks.
        """
        raise NotImplementedError("Implement room_exists()")

    # =========================
    # ---- aiortc hooks ----
    # =========================
    async def create_peer_connection(self, room_code: str) -> Any:
        """
        Create/return RTCPeerConnection for a room.
        """
        raise NotImplementedError("Implement create_peer_connection()")

    async def apply_remote_offer(self, room_code: str, offer_sdp: str, offer_type: str) -> None:
        """
        Set remote description from the client offer.
        """
        raise NotImplementedError("Implement apply_remote_offer()")

    async def create_and_set_local_answer(self, room_code: str) -> Tuple[str, str]:
        """
        1) pc.createAnswer()
        2) pc.setLocalDescription(answer)
        3) return (local_sdp, local_type)
        """
        raise NotImplementedError("Implement create_and_set_local_answer()")

    # =========================
    # ---- Utility ----
    # =========================
    def generate_scramble(self, length: int = 16) -> str:
        """
        Return a generated room code (A-Z/0-9 or your preferred charset).
        """
        raise NotImplementedError("Implement generate_scramble()")

