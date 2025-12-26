from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

app = Flask(__name__)

# 🔥 CORS DEFINITIVO Y GLOBAL
CORS(
    app,
    resources={r"/*": {"origins": [
        "https://programanovapresentaciones.com",
        "https://www.programanovapresentaciones.com"
    ]}},
    supports_credentials=False,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "OPTIONS"]
)

@app.after_request
def add_cors_headers(response):
    origin = request.headers.get("Origin")
    allowed = {
        "https://programanovapresentaciones.com",
        "https://www.programanovapresentaciones.com",
    }
    if origin in allowed:
        response.headers["Access-Control-Allow-Origin"] = origin

    response.headers["Vary"] = "Origin"
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
# GENERADOR 
# ===============================
@app.route("/generar", methods=["POST", "OPTIONS"])
def generar():
    if request.method == "OPTIONS":
        return ("", 204)

    data = request.get_json(silent=True) or {}

    titulo = (data.get("titulo") or "").strip()
    contenido = (data.get("contenido") or "").strip()
    num_diapositivas = data.get("num_diapositivas", 10)

    if not contenido:
        return jsonify({
            "error": "Falta el contenido para generar la presentación"
        }), 400

    prompt = f"""
Eres Nova, una IA experta en crear presentaciones profesionales.

Genera una presentación titulada:
"{titulo or 'Presentación generada por Nova'}"

A partir del siguiente contenido:

{contenido}

Estructura la respuesta en {num_diapositivas} diapositivas.
Cada diapositiva debe tener:
- Título
- 3 a 5 puntos clave claros y concisos
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Eres Nova, una IA creadora de presentaciones claras y profesionales."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        texto_generado = response.choices[0].message.content

        return jsonify({
            "status": "ok",
            "autor": "Nova & Pablo",
            "resultado": texto_generado
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "mensaje": "Error generando la presentación con IA",
            "detalle": str(e)
        }), 500

# ===============================
# RUN
# ===============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
