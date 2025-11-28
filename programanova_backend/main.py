from flask import Flask, request, jsonify
from flask_cors import CORS
import os

# ================================
# INICIAR FLASK
# ================================
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# ================================
# RUTA RAÍZ /check
# ================================
@app.route("/", methods=["GET"])
def health():
    return "Backend Programanova funcionando 💚", 200

# ================================
# RUTA /chat
# ================================
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    text = (data.get("mensaje") or "").strip()

    if not text:
        return jsonify({"error": "Falta el campo 'mensaje'"}), 400

    response = {
        "respuesta": f"🤖 Nova recibió: {text}",
        "emocion": "neutral",
        "intencion": "consulta",
        "resultado": f"El usuario dijo: {text}"
    }

    return jsonify(response), 200

# ================================
# RUN SERVER
# ================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
