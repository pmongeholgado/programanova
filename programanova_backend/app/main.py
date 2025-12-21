from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# CORS DEFINITIVO (una sola vez, sin after_request)
CORS(
    app,
    resources={r"/*": {"origins": "https://programanovapresentaciones.com"}},
    supports_credentials=False
)

@app.route("/status", methods=["GET"])
def status():
    return jsonify({"status": "ok"})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
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
    data = request.get_json()
    return jsonify({
        "mensaje": "Petición recibida correctamente (demo sin IA todavía)."
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
