# main.py - Backend sencillo para Programanova

from flask import Flask, request, jsonify
from flask_cors import CORS
import os

# =========================
# INICIAR FLASK + CORS
# =========================
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# =========================
# RUTA RAÍZ (SALUD)
# =========================
@app.route("/", methods=["GET"])
def health():
    return "Backend Programanova funcionando 💚", 200

# =========================
# RUTA /chat (POST)
# =========================
@app.route("/chat", methods=["POST"])
def chat():
    # Leer el JSON del cuerpo
    data = request.get_json(silent=True) or {}
    text = (data.get("mensaje") or "").strip()

    # Si no viene el campo mensaje, devolvemos error 400
    if not text:
        return jsonify({"error": "Falta el campo 'mensaje'"}), 400

    # Respuesta DEMO
    response = {
        "respuesta": f"🤖 Nova recibió: {text}",
        "emocion": "neutral",
        "intencion": "consulta",
        "resultado": f"El usuario dijo: {text}"
    }

    return jsonify(response), 200

# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
