from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

# ============================
#   INICIAR FLASK
# ============================
app = Flask(
    __name__,
    static_folder="frontend",     # Carpeta frontend
    static_url_path=""            # Para servir index / css / js directamente
)

# HABILITAR CORS (clave para que el navegador pueda POSTEAR /chat)
CORS(app)

# ============================
#   RUTAS FRONTEND
# ============================

# Ruta raíz -> index.html
@app.route("/")
def index():
    return app.send_static_file("index.html")

# Cualquier archivo estático (js, css, imágenes…)
@app.route("/<path:ruta>")
def files(ruta):
    return send_from_directory("frontend", ruta)

# ============================
#   API /chat
# ============================

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    text = data.get("mensaje", "").strip()

    # --- Respuesta DEMO básica ---
    response = {
        "respuesta": f"🤖 Nova recibió: {text}",
        "emocion": "neutral",
        "intencion": "consulta",
        "resumen": f"El usuario dijo: {text}"
    }

    return jsonify(response)


# ============================
#   RUN SERVER
# ============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
