from flask import Flask, request, jsonify, send_from_directory
import os

# 1. Servimos el frontend completo
app = Flask(
    __name__,
    static_folder="backend/frontend",
    static_url_path=""
)

# 2. Ruta principal → index.html
@app.route("/")
def home():
    return send_from_directory("backend/frontend", "index.html")

# 3. Endpoint dinámico: || chat ||
#    — este endpoint es vital para que el frontend funcione —
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    text = data.get("mensaje", "")

    ### !!! RESPUESTA SIMULADA — PARA PROBAR EN PRODUCCIÓN !!!
    response = {
        "respuesta": f"📩 Recibido: {text}",
        "emocion": "neutral",
        "intencion": "consulta",
        "resumen": f"El usuario escribió: {text}"
    }
    return jsonify(response)

# 4. Railway
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
