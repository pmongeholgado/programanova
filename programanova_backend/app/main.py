from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# ✅ CORS correcto (una sola vez, global)
CORS(app, resources={
    r"/*": {
        "origins": [
            "https://programanovapresentaciones.com",
            "https://www.programanovapresentaciones.com"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "status": "ok",
        "service": "programanova-backend"
    })

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    mensaje = data.get("mensaje", "")
    return jsonify({
        "respuesta": f"Nova recibió tu mensaje: {mensaje}",
        "emocion": "neutral",
        "intencion": "demo",
        "resultado": "OK",
        "resumen": f"Mensaje procesado correctamente: '{mensaje}'",
        "ultima_actualizacion": "ahora mismo"
    })

@app.route("/generar", methods=["POST"])
def generar():
    data = request.json or {}
    return jsonify({
        "mensaje": "Petición recibida correctamente (demo sin IA todavía)."
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
