from flask import Flask, request, jsonify, send_from_directory
import os

# Crear app Flask
app = Flask(
    __name__,
    static_folder="frontend",  # Carpeta con index y assets
    static_url_path=""         # Sirve los archivos en /
)

# ---- RUTA PRINCIPAL ----
@app.route("/")
def home():
    return app.send_static_file("index.html")

# ---- API CHAT ----
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    text = data.get("mensaje", "")

    response = {
        "respuesta": f"📨 Recibido: {text}",
        "emocion": "neutral",
        "intencion": "consulta",
        "resumen": f"El usuario escribió: {text}"
    }

    return jsonify(response)

# ---- EJECUCIÓN ----
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
