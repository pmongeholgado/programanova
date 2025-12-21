from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__)

# =========================
# CORS (PRODUCCIÓN)
# =========================
ALLOWED_ORIGINS = [
    "https://programanovapresentaciones.com",
    "https://www.programanovapresentaciones.com",
]

CORS(
    app,
    resources={r"/*": {"origins": ALLOWED_ORIGINS}},
    supports_credentials=False,
)

@app.after_request
def add_cors_headers(response):
    origin = request.headers.get("Origin")
    if origin in ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Vary"] = "Origin"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


# =========================
# HEALTH CHECKS
# =========================
@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "status": "Programa Nova Backend activo",
        "endpoints": ["/status", "/ping", "/chat", "/generar"]
    }), 200

@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "status": "ok",
        "message": "Backend funcionando",
        "autor": "Nova & Pablo"
    }), 200

@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"alive": True}), 200


# =========================
# ENDPOINT /chat (DEMO)
# =========================
@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return ("", 204)

    data = request.get_json(silent=True) or {}
    mensaje = (data.get("mensaje") or "").strip()

    if not mensaje:
        return jsonify({
            "respuesta": "No se recibió ningún mensaje.",
            "emocion": "neutral",
            "intencion": "error",
            "resultado": "KO",
            "resumen": "Mensaje vacío",
            "ultima_actualizacion": datetime.utcnow().isoformat()
        }), 400

    return jsonify({
        "respuesta": f"Nova recibió tu mensaje: {mensaje}",
        "emocion": "neutral",
        "intencion": "demo",
        "resultado": "OK",
        "resumen": f"Mensaje procesado correctamente: '{mensaje}'",
        "ultima_actualizacion": "ahora mismo"
    }), 200


# =========================
# ENDPOINT /generar (DEMO SEGURO)
# =========================
@app.route("/generar", methods=["POST", "OPTIONS"])
def generar():
    if request.method == "OPTIONS":
        return ("", 204)

    data = request.get_json(silent=True) or {}

    titulo = (data.get("titulo") or "Sin título").strip()
    num_diapositivas = data.get("num_diapositivas", 5)
    contenido = (data.get("contenido") or "").strip()

    if not contenido:
        return jsonify({
            "mensaje": "⚠️ No se recibió contenido para generar.",
            "estado": "KO"
        }), 400

    # DEMO: todavía sin IA
    return jsonify({
        "mensaje": "✅ Petición recibida correctamente (demo sin IA todavía).",
        "titulo": titulo,
        "num_diapositivas": num_diapositivas,
        "estado": "OK",
        "timestamp": datetime.utcnow().isoformat()
    }), 200


# =========================
# LOCAL RUN (solo local)
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
