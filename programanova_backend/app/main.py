from flask import Flask, request, jsonify
from flask_cors import CORS
import os

# ======================================
# INIT FLASK
# ======================================
app = Flask(__name__)

# CORS permitido a todo
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=False)

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

# ======================================
# HEALTH CHECK (Railway no debe apagar el contenedor)
# ======================================
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

# ======================================
# ENDPOINT /chat
# ======================================
@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():

    # Preflight OPTIONS
    if request.method == "OPTIONS":
        return ("", 204)

    data = request.get_json(silent=True) or {}
    text = (data.get("mensaje") or "").strip()

    if not text:
        return jsonify({"error": "Falta el campo 'mensaje'"}), 400

    # DEMO RESPONSE
    respuesta = {
        "respuesta": f"Nova recibió tu mensaje: {text}",
        "emocion": "neutral",
        "intencion": "demo",
        "resultado": "OK",
        "resumen": f"Mensaje procesado correctamente: '{text}'",
        "ultima_actualizacion": "ahora mismo"
    }

    return jsonify(respuesta), 200

# ======================================
# RUN LOCAL ONLY (Railway ignora esto)
# ======================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
