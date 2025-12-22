from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime

app = Flask(__name__)

# ✅ CORS real (no solo "*") para tu dominio y previews
ALLOWED_ORIGINS = [
    "https://programanovapresentaciones.com",
    "https://www.programanovapresentaciones.com",
    # Vercel previews (si necesitas):
    # "https://programanova-*.vercel.app",
]

CORS(
    app,
    resources={r"/*": {"origins": ALLOWED_ORIGINS}},
    supports_credentials=False,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "OPTIONS"],
)

@app.after_request
def add_cors_headers(response):
    # Por si algún proxy/edge se pone tonto, reforzamos:
    origin = request.headers.get("Origin", "")
    if origin in ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Vary"] = "Origin"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


# =========================
# HEALTH
# =========================
@app.route("/", methods=["GET"])
def root():
    return jsonify({"ok": True, "message": "API operativa", "autor": "Nova & Pablo"}), 200

@app.route("/status", methods=["GET"])
def status():
    return jsonify({"status": "ok", "message": "Backend funcionando", "autor": "Nova & Pablo"}), 200

@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"alive": True}), 200


# =========================
# CHAT (DEMO o REAL)
# =========================
@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return ("", 204)

    data = request.get_json(silent=True) or {}
    text = (data.get("mensaje") or "").strip()
    if not text:
        return jsonify({"error": "Falta el campo 'mensaje'"}), 400

    # ✅ ANTI-CRASH: si no hay API KEY, NO se cae el servidor.
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()

    if not api_key:
        # Modo DEMO estable
        respuesta = {
            "respuesta": f"Nova recibió tu mensaje: {text}",
            "emocion": "neutral",
            "intencion": "demo",
            "resultado": "OK",
            "resumen": f"Mensaje procesado correctamente: '{text}'",
            "ultima_actualizacion": "ahora mismo"
        }
        return jsonify(respuesta), 200

    # 🔥 Aquí irá el CORAZÓN REAL (cuando tengas clave y quieras activarlo)
    # Por ahora, devolvemos un placeholder que NO rompe nada:
    respuesta = {
        "respuesta": f"(IA real pendiente de activar) Recibí: {text}",
        "emocion": "neutral",
        "intencion": "ia_pendiente",
        "resultado": "OK",
        "resumen": "Backend listo para IA real cuando haya clave.",
        "ultima_actualizacion": datetime.utcnow().isoformat() + "Z"
    }
    return jsonify(respuesta), 200


# =========================
# GENERAR (DEMO)
# =========================
@app.route("/generar", methods=["POST", "OPTIONS"])
def generar():
    if request.method == "OPTIONS":
        return ("", 204)

    data = request.get_json(silent=True) or {}
    titulo = (data.get("titulo") or "").strip()
    num = data.get("num_diapositivas")
    contenido = (data.get("contenido") or "").strip()

    if not contenido:
        return jsonify({"ok": False, "error": "Falta 'contenido'"}), 400

    return jsonify({
        "ok": True,
        "mensaje": "Petición recibida correctamente (demo sin IA todavía).",
        "titulo": titulo,
        "num_diapositivas": num,
    }), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
