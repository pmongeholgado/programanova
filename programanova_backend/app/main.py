from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json # Importante para procesar la respuesta estructurada
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

app = Flask(__name__)

# CORS GLOBAL (Mantengo tu configuración que es correcta)
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
    return response

# ===============================
# CHAT (AHORA REAL Y ESTRUCTURADO)
# ===============================
@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return "", 204

    data = request.get_json(silent=True) or {}
    text = (data.get("mensaje") or "").strip()

    if not text:
        return jsonify({"error": "Falta el mensaje"}), 400

    try:
        # Llamada real a OpenAI pidiendo formato JSON
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Eres Nova. Responde SIEMPRE en formato JSON con estas llaves: respuesta, emocion, intencion, resultado, resumen. Sé breve y profesional."},
                {"role": "user", "content": text}
            ],
            response_format={ "type": "json_object" } # Forzamos a que responda JSON
        )

        # Parseamos la respuesta de la IA
        ai_response = json.loads(response.choices[0].message.content)
        
        return jsonify(ai_response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===============================
# GENERADOR (OPTIMIZADO PARA CONTENIDO)
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
        return jsonify({"error": "Falta el contenido"}), 400

    prompt = f"""
    Genera el contenido para una presentación de {num_diapositivas} diapositivas.
    Título: {titulo}
    Contenido base: {contenido}
    
    Para cada diapositiva indica: Título de la slide y Puntos clave.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Eres un experto en diseño de presentaciones profesionales."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        return jsonify({
            "status": "ok",
            "autor": "Nova & Pablo",
            "resultado": response.choices[0].message.content
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "detalle": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
