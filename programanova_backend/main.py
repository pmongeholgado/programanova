from flask import Flask, request, jsonify
from flask_cors import CORS
import os

# =============================
# INICIAR FLASK
# =============================
app = Flask(__name__)
CORS(app)

# =============================
# RUTA RAÍZ (CHECK)
# =============================
@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "ok",
        "mensaje": "Backend Programanova funcionando ✔️🚀"
    }), 200

# =============================
# API /chat
# =============================
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    mensaje = data.get("mensaje", "").strip()

    if not mensaje:
        return jsonify({"error": "El campo 'mensaje' es obligatorio"}), 400

    # ---- RESPUESTA DEMO ----
    return jsonify({
        "respuesta": f"🤖 Nova recibió: {mensaje}",
        "emocion": "neutral",
        "intencion": "demo",
        "resumen": f"El usuario dijo: {mensaje}"
    }), 200


# =============================
# RUN SERVER (IMPORTANTÍSIMO)
# =============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
