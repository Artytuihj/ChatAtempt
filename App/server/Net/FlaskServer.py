from flask import Flask, jsonify, request
import os


class FlaskServer:
    def __init__(self, server_net=None):
        self.server_net = server_net
        self.app = Flask(__name__)
        self._register_routes()

    def _register_routes(self):
        @self.app.route("/")
        def home():
            return "..."

        @self.app.route("/reg", methods=["POST"])
        def reg():
            data = request.get_json(silent=True) or {}
            room_code = data.get("room_code")
            offer_sdp = data.get("offer_sdp")
            offer_type = data.get("offer_type")

            if not room_code or not offer_sdp or not offer_type:
                return jsonify({"error": "missing fields"}), 400

            if self.server_net is None:
                return jsonify({"error": "server handler not configured"}), 503

            try:
                answer_sdp, answer_type = self.server_net.handle_offer(
                    room_code, offer_sdp, offer_type
                )
                payload = self.server_net.build_answer_payload(answer_sdp, answer_type)
                return jsonify(payload), 200
            except NotImplementedError:
                return jsonify({"error": "server handler not implemented"}), 501
            except ValueError as err:
                return jsonify({"error": str(err)}), 400

        @self.app.route("/Health")
        def health_check():
            return "OK", 200

    def get_app(self):
        return self.app

    def run(self, host="0.0.0.0", port=5000):
        self.app.run(host=host, port=port)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    FlaskServer().run(port=port)
