# ==== Imports ====
import random
import string
import threading

# ==== Internal Imports ====
import App.server.Net.FlaskServer as flask
import App.server.Net.ServerNetHandler as net

# ==== Host Handler ====
class HostHandler:
    def __init__(self, version):
        # ---- Basic Config ----
        self.VERSION = "1.0.1"
        self.hostname = "Undefined"
        self.code = ""


    # =========================
    # ---- Setup & Teardown ----
    # =========================

    def generate_scramble(self, length=16):
        """Generate a random uppercase room code."""
        scramble = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))
        print(f"[generate_scramble] Generated room code: {scramble}")
        return scramble

    # =========================
    # ---- Threads ----
    # =========================
    def start_hosting_thread(self):
        """Run hosting loop in a background thread."""
        print("[start_hosting_thread] Starting thread...")
        thread = threading.Thread(target=self.handle_clients_connection, daemon=True)
        thread.start()
        print("[start_hosting_thread] Thread started.")
