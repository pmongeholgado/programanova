from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import datetime
import requests

# =========================================
# INIT FLASK
# =========================================
app = Flask(__name__)

# CORS (abierto para la web)
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=False,
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "OPTIONS"],
)


# =========================================
# CONFIG GPT (OpenAI)
# =========================================
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini").strip()
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").strip()
OPENAI_TIMEOUT = int(os.environ.get("OPENAI_TIMEOUT", "45"))

def now_str():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def call_openai_chat(system_prompt: str, user_prompt: str) -> str:
    """
    Llamada directa a OpenAI Chat Completions vía HTTP (sin dependencia extra).
    Devuelve texto.
    """
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY no configurada")

    url = f"{OPENAI_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": OPENAI_MODEL,
        "temperature": 0.4,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    r = requests.post(url, headers=headers, json=payload, timeout=OPENAI_TIMEOUT)
    if r.status_code >= 400:
        raise RuntimeError(f"OpenAI error {r.status_code}: {r.text}")

    data = r.json()
    text = (
    data.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
)

    return text


# =========================================
# HEALTH CHECKS
# =========================================
@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "ok": True,
        "message": "API operativa",
        "autor": "Nova & Pablo",
        "time": now_str()
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


# =========================================
# ENDPOINT /chat  (GPT REAL)
# =========================================
@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    # Preflight
    if request.method == "OPTIONS":
        return ("", 204)

    data = request.get_json(silent=True) or {}
    texto = (data.get("mensaje") or "").strip()

    if not texto:
        return jsonify({"error": "Falta el campo 'mensaje'"}), 400

    # Si no hay API KEY, no rompemos: devolvemos demo estable
    if not OPENAI_API_KEY:
        return jsonify({
            "respuesta": f"Nova recibió tu mensaje (modo demo): {texto}",
            "emocion": "neutral",
            "intencion": "demo",
            "resultado": "OK",
            "resumen": f"Mensaje procesado correctamente (sin GPT): '{texto}'",
            "ultima_actualizacion": "ahora mismo"
        }), 200

    # GPT real
    try:
        system_prompt = (
            "Eres Nova, asistente del proyecto Programa Nova Presentaciones. "
            "Responde en español de forma clara y útil. "
            "Devuelve SIEMPRE una respuesta corta y profesional."
        )

        user_prompt = (
            "Usuario dice:\n"
            f"{texto}\n\n"
            "Responde con un texto breve (2-6 líneas) y útil."
        )

        gpt_text = call_openai_chat(system_prompt, user_prompt).strip()

        # Estructura “bonita” para el frontend
        return jsonify({
            "respuesta": gpt_text,
            "emocion": "neutral",
            "intencion": "asistencia",
            "resultado": "OK",
            "resumen": "Respuesta generada por GPT correctamente.",
            "ultima_actualizacion": "ahora mismo"
        }), 200

    except Exception as e:
        return jsonify({
            "respuesta": "⚠️ Nova no pudo generar respuesta ahora mismo.",
            "emocion": "neutral",
            "intencion": "error",
            "resultado": "ERROR",
            "resumen": f"Fallo en GPT: {str(e)}",
            "ultima_actualizacion": "ahora mismo"
        }), 200


# =========================================
# ENDPOINT /generar (GPT REAL)
# Devuelve estructura de presentación (sin crear PPT todavía)
# =========================================
@app.route("/generar", methods=["POST", "OPTIONS"])
def generar():
    if request.method == "OPTIONS":
        return ("", 204)

    data = request.get_json(silent=True) or {}
    titulo = (data.get("titulo") or "").strip()
    num_diapositivas = data.get("num_diapositivas")
    contenido = (data.get("contenido") or "").strip()

    # Validación
    try:
        num = int(num_diapositivas) if num_diapositivas is not None else 10
    except Exception:
        num = 10

    if not contenido:
        return jsonify({"error": "Falta el campo 'contenido'"}), 400

    if not titulo:
        titulo = "Presentación generada por Nova"

    # Si no hay API KEY → modo demo, pero estable
    if not OPENAI_API_KEY:
        slides_demo = []
        for i in range(1, num + 1):
            slides_demo.append({
                "n": i,
                "titulo": f"Diapositiva {i}",
                "bullets": [
                    "Punto clave 1 (demo)",
                    "Punto clave 2 (demo)",
                    "Punto clave 3 (demo)"
                ],
                "narrativa": "Narrativa demo para esta diapositiva."
            })

        return jsonify({
            "mensaje": "✅ Petición recibida correctamente (modo demo sin IA todavía).",
            "titulo": titulo,
            "num_diapositivas": num,
            "slides": slides_demo
        }), 200

    # GPT real
    try:
        system_prompt = (
            "Eres Nova, un generador de presentaciones. "
            "Devuelves SIEMPRE JSON válido, sin texto extra."
        )

        # Pedimos un JSON estructurado
        user_prompt = f"""
Genera una estructura de presentación en formato JSON.

REGLAS:
- Devuelve SOLO JSON válido.
- Debe tener estas claves raíz EXACTAS:
  "titulo", "num_diapositivas", "slides"
- "slides" es un array de {num} objetos.
- Cada slide debe tener:
  "n" (número),
  "titulo" (string),
  "bullets" (array de 3 a 6 strings),
  "narrativa" (string breve, 2-4 líneas)

DATOS:
- Título: {titulo}
- Contenido base (resumir y estructurar):
{contenido}
"""

        raw = call_openai_chat(system_prompt, user_prompt).strip()

        # Intento parseo JSON seguro (si GPT mete algo raro, lo controlamos)
        try:
            parsed = json.loads(raw)
        except Exception:
            # Segundo intento: recortar si viene con basura
            start = raw.find("{")
            end = raw.rfind("}")
            if start != -1 and end != -1 and end > start:
                parsed = json.loads(raw[start:end+1])
            else:
                raise RuntimeError("GPT no devolvió JSON válido.")

        # Garantías mínimas
        parsed["titulo"] = parsed.get("titulo") or titulo
        parsed["num_diapositivas"] = parsed.get("num_diapositivas") or num
        parsed["slides"] = parsed.get("slides") or []

        return jsonify({
            "mensaje": "✅ Estructura generada por GPT correctamente.",
            "data": parsed
        }), 200

    except Exception as e:
        return jsonify({
            "mensaje": "❌ Error generando estructura con GPT.",
            "error": str(e)
        }), 200


# =========================================
# RUN LOCAL ONLY (Render ignora esto, pero sirve para local)
# =========================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
