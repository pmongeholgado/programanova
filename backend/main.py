from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

# ================================
# INICIAR FLASK
# ================================
app = Flask(
    __name__,
    static_folder="frontend",       # Carpeta donde está index.html
    static_url_path=""              # Sirve archivos estáticos directamente
)

# Permitir CORS (muy importante para que el navegador pueda llamar a /chat)
CORS(app)

# ================================
# RUTAS FRONTEND
# ================================
# Ruta raíz -> index.html
@app.route("/")
def index():
    return app.send_static_file("index.html")

# Servir archivos estáticos (css, js, imágenes…)
@app.route("/<path:archivo>")
def servir_archivo(archivo):
    return send_from_directory("frontend", archivo)

# ================================
# API /chat
# ================================
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    text = data.get("mensaje", "").strip()

    if not text:
        return jsonify({"error": "Falta el campo 'mensaje'"}), 400

    # --- Respuesta DEMO básica ---
    response = {
        "respuesta": f"🤖 Nova recibió: {text}",
        "emocion": "neutral",
        "intencion": "consulta",
        "resumen": f"El usuario dijo: {text}"
    }

    return jsonify(response)

# ================================
# RUN SERVER
# ================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
