from flask import Flask, request, jsonify, send_from_directory
import os

# FRONTEND desde carpeta frontend (la detecta al estar dentro del backend)
app = Flask(
    __name__,
    static_folder="frontend",
    static_url_path=""
)

# Ruta principal
@app.route("/")
def home():
    return send_from_directory("frontend", "index.html")

# API CHAT
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    text = data.get("mensaje", "")

    response = {
        "respuesta": f"📩 Recibido del usuario: {text}",
        "emocion": "neutral",
        "intencion": "consulta",
        "resumen": f"El usuario escribió: {text}"
    }
    return jsonify(response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
