from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "ok", "mensaje": "Backend Programanova funcionando"})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    mensaje = data.get("mensaje", "Sin mensaje")
    
    return jsonify({
        "respuesta": f"Recibido: {mensaje}",
        "emocion": "neutral",
        "intencion": "demo",
        "resumen": f"El usuario dijo: {mensaje}"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
