from flask import Flask, request, jsonify, send_from_directory
import os

# Iniciar Flask
app = Flask(__name__,
            static_folder="frontend",  # Aquí están index.html, style.css, app.js
            static_url_path="")

# 👉 Ruta principal sirve el frontend real
@app.route("/")
def index():
    return send_from_directory("frontend", "index.html")

# 👉 Cualquier archivo del frontend
@app.route("/<path:ruta>")
def archivos(ruta):
    return send_from_directory("frontend", ruta)

# 💬 API CHAT
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    text = data.get("mensaje", "")

    response = {
        "respuesta": f"🤖 Nova recibió: {text}",
        "emocion": "neutra",
        "intencion": "consulta",
        "resumen": f"El usuario dijo: {text}"
    }
    return jsonify(response)

# 🚀 RUN
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
