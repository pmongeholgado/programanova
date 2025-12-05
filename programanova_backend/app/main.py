from flask import Flask, request, jsonify
from flask_cors import CORS
import os

# ================================
# INIT FLASK
# ================================
app = Flask(__name__)

# CORS abierto para la demo (Vercel -> Railway)
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=False,
)

# Añadimos cabeceras CORS extra en TODAS las respuestas
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


# ================================
# HEALTH CHECK
# ================================
@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "status": "ok",
        "message": "Backend funcionando",
        "autor": "Nova & Pablo",
    })


# ================================
# ENDPOINT /chat
# ================================
@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    # Preflight CORS (OPTIONS) -> respuesta vacía pero OK
    if request.method == "OPTIONS":
        return ("", 204)

    data = request.get_json(silent=True) or {}
    text = (data.get("mensaje") or "").strip()

    if not text:
        return jsonify({"error": "Falta el campo 'mensaje'"}), 400

# Solo se usa si ejecutaras lrespuesta = {
        "respuesta": f"🧠 Nova recibió tu mensaje: {text}",
        "emocion": "neutral",
        "intencion": "demo",
        "resultado": "OK",
        "resumen": f"Mensaje procesado correctamente: '{text}'",
        "ultima_actualizacion": "ahora mismo"
    }
    return jsonify(respuesta), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
