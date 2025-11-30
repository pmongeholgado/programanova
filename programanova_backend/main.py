from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# --------------- test de vida real ---------------
@app.route("/", methods=["GET"])
def index():
    return "🟢 Backend Programanova operativo", 200


# --------------- API CHAT ---------------
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    text = data.get("mensaje", "").strip()

    if not text:
        return jsonify({"error": "Falta el campo 'mensaje'"}), 400

    response = {
        "respuesta": f"🤖 Nova recibió: {text}",
        "emocion": "neutral",
        "intencion": "consulta",
        "resumen": f"El usuario dijo: {text}"
    }

    return jsonify(response)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
