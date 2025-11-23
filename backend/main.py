from flask import Flask, request, jsonify, send_from_directory
import os

# Servir el frontend desde la carpeta /frontend
app = Flask(__name__, static_folder="frontend", static_url_path="")

# Ruta principal → devuelve index.html
@app.route("/")
def home():
    return send_from_directory("frontend", "index.html")

# Ruta para servir archivos estáticos (css, js, imágenes…)
@app.route("/<path:ruta>")
def static_files(ruta):
    return send_from_directory("frontend", ruta)

# --- API CHAT ---
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    text = data.get("mensaje", "")

    response = {
        "respuesta": f"Recibido por Nova: {text}",
        "emocion": "neutral",
        "intencion": "consulta",
        "resumen": f"El usuario escribió: {text}"
    }
    return jsonify(response)


# 🚀 Ejecutar en Railway
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
