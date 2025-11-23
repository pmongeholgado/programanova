from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='/')
CORS(app)

# Servir index
@app.route('/')
def home():
    return send_from_directory(FRONTEND_DIR, 'index.html')

# Servir archivos estáticos
@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(FRONTEND_DIR, path)

# Endpoint IA
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    mensaje = data.get('mensaje', '').strip()

    if not mensaje:
        return jsonify({
            "respuesta": "No entendí el mensaje.",
            "emocion": "neutra",
            "intencion": "desconocida",
            "resumen": "Vacío"
        })

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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
