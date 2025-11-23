from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__, static_folder='backend/frontend', static_url_path='')

# Habilitar CORS para permitir llamadas desde tu dominio
CORS(app)

# Ruta principal -> entrega index.html
@app.route('/')
def index():
    return send_from_directory('backend/frontend', 'index.html')

# Ruta dinámica -> entrega cualquier archivo o carpeta (css, js, assets…)
@app.route('/<path:ruta>')
def archivos(ruta):
    return send_from_directory('backend/frontend', ruta)

# 🚨 ENDPOINT REAL DE IA — NUESTRO ORQUESTADOR
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()

    mensaje = data.get("mensaje", "").strip()

    if not mensaje:
        return jsonify({
            "respuesta": "No entendí el mensaje.",
            "emocion": "neutra",
            "intencion": "desconocida",
            "resumen": "Vacío"
        })

    # --- AQUÍ IRÁ TU LÓGICA REAL DE IA ---
    # Por ahora devolvemos simulación funcional
    respuesta = f"Recibí tu mensaje: {mensaje}"
    emocion = "neutral"
    intencion = "conversación"
    resumen = f"El usuario dijo: {mensaje}"

    return jsonify({
        "respuesta": respuesta,
        "emocion": emocion,
        "intencion": intencion,
        "resumen": resumen
    })

# Railway
if __name__ == '__main__':
    puerto = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=puerto)
