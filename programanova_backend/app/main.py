from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime

app = Flask(__name__)

# CORS permitido a todo (frontend en Vercel)
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


# ============================
# HEALTH CHECKS
# ============================
@app.route("/", methods=["GET"])
def root():
    return jsonify({"ok": True, "message": "API operativa", "autor": "Nova & Pablo"}), 200

@app.route("/status", methods=["GET"])
def status():
    return jsonify({"status": "ok", "message": "Backend funcionando", "autor": "Nova & Pablo"}), 200

@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"alive": True}), 200


# ============================
# OPENAI (lazy import + safe)
# ============================
def _get_openai_client():
    """
    Devuelve un cliente OpenAI si:
      - está instalado el paquete
      - existe OPENAI_API_KEY
    Si no, devuelve None (y la app NO se cae).
    """
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None

    try:
        from openai import OpenAI
        return OpenAI(api_key=api_key)
    except Exception:
        # ImportError o cualquier problema -> no tumbamos el servidor
        return None


def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ============================
# ENDPOINT /chat (IA real)
# ============================
@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return ("", 204)

    data = request.get_json(silent=True) or {}
    text = (data.get("mensaje") or "").strip()

    if not text:
        return jsonify({"error": "Falta el campo 'mensaje'"}), 400

    client = _get_openai_client()

    # Fallback demo si no hay cliente (pero NUNCA se cae)
    if client is None:
        respuesta = {
            "respuesta": f"Nova recibió tu mensaje: {text}",
            "emocion": "neutral",
            "intencion": "demo",
            "resultado": "OK",
            "resumen": f"Mensaje procesado correctamente: '{text}'",
            "ultima_actualizacion": "ahora mismo",
        }
        return jsonify(respuesta), 200

    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    prompt = f"""
Devuelve SOLO JSON válido con estas claves:
respuesta, emocion, intencion, resultado, resumen

Usuario: {text}
"""

    try:
        r = client.responses.create(
            model=model,
            input=prompt,
        )

        # Intentamos sacar texto
        out_text = getattr(r, "output_text", None) or ""

        # Si el modelo devuelve JSON como texto, lo parseamos.
        # Si no, lo metemos en "respuesta".
        try:
            obj = json.loads(out_text)
            obj["ultima_actualizacion"] = "ahora mismo"
            return jsonify(obj), 200
        except Exception:
            return jsonify({
                "respuesta": out_text.strip() or "Nova no pudo generar una respuesta.",
                "emocion": "neutral",
                "intencion": "chat",
                "resultado": "OK",
                "resumen": "Respuesta generada por IA.",
                "ultima_actualizacion": "ahora mismo",
            }), 200

    except Exception as e:
        # Error de OpenAI (cuota, key, red, etc.) -> NO tumbamos el server
        return jsonify({
            "respuesta": "⚠️ Hubo un problema conectando con la IA, pero el backend sigue vivo.",
            "emocion": "neutral",
            "intencion": "error_openai",
            "resultado": "ERROR",
            "resumen": str(e)[:300],
            "ultima_actualizacion": "ahora mismo",
        }), 200


# ============================
# ENDPOINT /generar (base)
# ============================
@app.route("/generar", methods=["POST", "OPTIONS"])
def generar():
    if request.method == "OPTIONS":
        return ("", 204)

    data = request.get_json(silent=True) or {}
    titulo = (data.get("titulo") or "Presentación").strip()
    num = int(data.get("num_diapositivas") or 8)
    contenido = (data.get("contenido") or "").strip()

    if not contenido:
        return jsonify({"ok": False, "message": "Falta 'contenido'"}), 400

    client = _get_openai_client()

    # Demo sin IA: devuelve estructura mínima
    if client is None:
        slides = []
        for i in range(1, num + 1):
            slides.append({"titulo": f"{titulo} — Slide {i}", "bullets": ["(demo) Contenido pendiente de IA real"]})
        return jsonify({"ok": True, "modo": "demo", "titulo": titulo, "slides": slides}), 200

    model = os.getenv("OPENAI_MODEL_GENERAR", os.getenv("OPENAI_MODEL", "gpt-4.1-mini"))

    prompt = f"""
Crea un esquema de presentación en JSON con:
titulo (string), slides (array)
Cada slide: titulo (string), bullets (array de strings)

Titulo: {titulo}
Num diapositivas: {num}
Contenido base:
{contenido}

Devuelve SOLO JSON.
"""

    try:
        r = client.responses.create(model=model, input=prompt)
        out_text = getattr(r, "output_text", None) or ""

        obj = json.loads(out_text)
        obj["ok"] = True
        obj["modo"] = "ia"
        return jsonify(obj), 200

    except Exception as e:
        return jsonify({
            "ok": False,
            "message": "Error generando con IA",
            "detail": str(e)[:300],
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
