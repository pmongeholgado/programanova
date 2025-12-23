from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)

# 🔥 CORS DEFINITIVO Y GLOBAL
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=False,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "OPTIONS"]
)

# 🔒 Forzar headers incluso en errores
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


# ===============================
# HEALTH CHECKS
# ===============================
@app.route("/", methods=["GET"])
def root():
    return jsonify({"ok": True}), 200

@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "status": "ok",
        "message": "Backend funcionando",
        "autor": "Nova & Pablo"
    }), 200


# ===============================
# CHAT
# ===============================
@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return "", 204

    data = request.get_json(silent=True) or {}
    text = (data.get("mensaje") or "").strip()

    if not text:
        return jsonify({"error": "Falta el mensaje"}), 400

    return jsonify({
        "respuesta": f"Nova recibió tu mensaje: {text}",
        "emocion": "neutral",
        "intencion": "demo",
        "resultado": "OK",
        "resumen": f"Mensaje procesado correctamente: '{text}'",
        "ultima_actualizacion": "ahora mismo"
    }), 200


# ===============================
# GENERADOR (demo)
# ===============================
@app.route("/generar", methods=["POST", "OPTIONS"])
def generar():
    if request.method == "OPTIONS":
        return "", 204

    data = request.get_json(silent=True) or {}

    return jsonify({
        "message": "Petición recibida correctamente (demo sin IA todavía)"
    }), 200


# ===============================
# RUN
# ===============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
