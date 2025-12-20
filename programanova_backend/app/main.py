from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)

# =========================
# CORS (igual que antes)
# =========================
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=False,
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "OPTIONS"],
)

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


# =========================
# ENDPOINT EXISTENTE /chat
# (NO SE TOCA)
# =========================
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True, silent=True) or {}
    mensaje = data.get("mensaje", "")

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
    })


# =========================
# NUEVO ENDPOINT /generar
# (CORAZÓN – MODO DEMO SEGURO)
# =========================
@app.route("/generar", methods=["POST"])
def generar():
    data = request.get_json(force=True, silent=True) or {}

    titulo = data.get("titulo", "Sin título")
    num_diapositivas = data.get("num_diapositivas", 5)
    contenido = data.get("contenido", "")

    if not contenido:
        return jsonify({
            "mensaje": "⚠️ No se recibió contenido para generar.",
            "estado": "KO"
        }), 400

    # DEMO: no IA todavía
    return jsonify({
        "mensaje": "✅ Petición recibida correctamente (demo sin IA todavía).",
        "titulo": titulo,
        "num_diapositivas": num_diapositivas,
        "estado": "OK",
        "timestamp": datetime.utcnow().isoformat()
    })


# =========================
# ROOT (opcional, seguro)
# =========================
@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "status": "Programa Nova Backend activo",
        "endpoints": ["/chat", "/generar"]
    })
