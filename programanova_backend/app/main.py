from flask import Flask, request, jsonify
from flask_cors import CORS
import os

# ===================================
# INIT FLASK
# ===================================
app = Flask(__name__)

# ===================================
# CORS PERMITIDO A TODO
# ===================================
CORS(app, resources={r"/*": {"origins": "*"}},
     supports_credentials=False,
     allow_headers=["Content-Type", "Authorization"],
     expose_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "OPTIONS"]
)

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


# ===================================
# HEALTH CHECK
# ===================================
@app.route("/", methods=["GET"])
def root():
    return jsonify({"ok": True, "message": "API operativa", "autor": "Nova & Pablo"}), 200


@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "status": "ok",
        "message": "Backend funcionando",
        "autor": "Nova & Pablo",
    }), 200


@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"alive": True}), 200


# ===================================
# ENDPOINT CHAT (YA FUNCIONAL)
# ===================================
@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():

    if request.method == "OPTIONS":
        return "", 204

    data = request.get_json(silent=True) or {}
    text = (data.get("mensaje") or "").strip()

    if not text:
        return jsonify({"error": "Falta el campo 'mensaje'"}), 400

    respuesta = {
        "respuesta": f"Nova recibió tu mensaje: {text}",
        "emocion": "neutral",
        "intencion": "demo",
        "resultado": "OK",
        "resumen": f"Mensaje procesado correctamente: '{text}'",
        "ultima_actualizacion": "ahora mismo"
    }

    return jsonify(respuesta), 200


# ===================================================
# 🆕 ENDPOINT NUEVO: /generar (SIN GPT, SIN IA AÚN)
# ===================================================
@app.route("/generar", methods=["POST", "OPTIONS"])
def generar():

    if request.method == "OPTIONS":
        return "", 204

    data = request.get_json(silent=True) or {}
    tema = (data.get("tema") or "").strip()

    if not tema:
        return jsonify({"error": "Falta el campo 'tema'"}), 400

    # Respuesta inicial de prueba
    diapositivas_demo = [
        {"titulo": "Introducción", "contenido": f"Presentación sobre {tema}"},
        {"titulo": "Punto clave 1", "contenido": "Desarrollo del primer punto"},
        {"titulo": "Conclusión", "contenido": "Ideas finales y cierre"},
    ]

    return jsonify({
        "ok": True,
        "mensaje": "Generador operativo",
        "tema": tema,
        "diapositivas": diapositivas_demo
    }), 200


# ===================================
# RUN LOCAL (IGNORADO POR RENDER)
# ===================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
