from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

# ============================
# INICIAR FLASK
# ============================
app = Flask(
    __name__,
    static_folder="frontend",
    static_url_path=""
)

# HABILITAR CORS
CORS(app)

# ============================
# RUTAS FRONTEND
# ============================

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/<path:ruta>")
def files(ruta):
    return send_from_directory("frontend", ruta)

# ============================
# API /chat
# ============================

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

# ============================
# RUN SERVER
# ============================
if __name__ == "__main__":
    # ATENCIÓN: Railway usa el puerto 8080
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
