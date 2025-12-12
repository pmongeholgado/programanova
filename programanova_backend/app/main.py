from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import requests

app = Flask(__name__)

# CORS permitido a todo (como ya tenías)
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
# HEALTH CHECKS
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
# /chat (demo estable - NO lo rompemos)
# =========================
@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return ("", 204)

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
        "ultima_actualizacion": "ahora mismo",
    }
    return jsonify(respuesta), 200

# =========================
# /generar (CORAZÓN: IA real si hay OPENAI_API_KEY)
# =========================
def _demo_generar(titulo: str, n: int, contenido: str):
    n = max(1, min(int(n or 8), 20))
    bullets = [b.strip("-• \t") for b in contenido.splitlines() if b.strip()]
    bullets = bullets[: max(8, n * 3)]

    diapositivas = []
    for i in range(n):
        base = bullets[i*3:(i+1)*3]
        diapositivas.append({
            "n": i + 1,
            "titulo": f"Diapositiva {i+1}",
            "puntos": base if base else [f"Punto {i+1}.1", f"Punto {i+1}.2"]
        })

    return {
        "modo": "demo",
        "titulo": titulo or "Presentación (demo)",
        "diapositivas": diapositivas,
        "resumen": "Respuesta demo (sin IA). Activa OPENAI_API_KEY para IA real."
    }

def _openai_generar_json(titulo: str, n: int, contenido: str):
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini").strip()

    if not api_key:
        return None, "OPENAI_API_KEY no configurada"

    system = (
        "Eres un asistente que crea guiones de diapositivas para presentaciones. "
        "Devuelve SOLO JSON válido (sin texto extra)."
    )

    user = {
        "titulo": titulo,
        "num_diapositivas": n,
        "contenido": contenido
    }

    prompt = f"""
Crea una presentación a partir del contenido.

REGLAS:
- Devuelve SOLO un JSON válido.
- Estructura EXACTA:
{{
  "titulo": "string",
  "diapositivas": [
    {{
      "n": 1,
      "titulo": "string",
      "puntos": ["string", "string", "string"]
    }}
  ],
  "resumen": "string"
}}
- "diapositivas" debe tener exactamente {n} elementos.
- "puntos": 3 a 5 puntos por diapositiva, frases cortas.
- Mantén el idioma español.
- No inventes datos técnicos si no están en el contenido: si faltan, usa formulación prudente.

INPUT:
{json.dumps(user, ensure_ascii=False)}
""".strip()

    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "temperature": 0.3,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        # Si el modelo lo soporta, fuerza JSON:
        "response_format": {"type": "json_object"},
        "max_tokens": 1800,
    }

    r = requests.post(url, headers=headers, json=payload, timeout=60)

    if r.status_code != 200:
        return None, f"OpenAI error {r.status_code}: {r.text}"

    content_text = (r.json().get("choices", [{}])[0].get("message", {}) or {}).get("content", "")
    if not content_text:
        return None, "OpenAI no devolvió contenido"

    try:
        data = json.loads(content_text)
        return data, None
    except Exception:
        return None, "La respuesta de OpenAI no era JSON válido"

@app.route("/generar", methods=["POST", "OPTIONS"])
def generar():
    if request.method == "OPTIONS":
        return ("", 204)

    data = request.get_json(silent=True) or {}
    titulo = (data.get("titulo") or "").strip()
    contenido = (data.get("contenido") or "").strip()
    num_diapositivas = data.get("num_diapositivas") or data.get("slides") or 8

    try:
        n = int(num_diapositivas)
    except Exception:
        n = 8
    n = max(1, min(n, 20))

    if not contenido:
        return jsonify({"error": "Falta 'contenido'"}), 400

    # 1) Intentar IA real
    ai_json, err = _openai_generar_json(titulo, n, contenido)
    if ai_json:
        ai_json["modo"] = "ia"
        return jsonify(ai_json), 200

    # 2) Fallback demo (para no romper nada)
    demo = _demo_generar(titulo, n, contenido)
    demo["nota"] = f"Fallback por: {err}"
    return jsonify(demo), 200

# =========================
# RUN LOCAL ONLY
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
