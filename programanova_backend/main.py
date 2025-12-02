from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "ok": True,
        "mensaje": "Backend activo 🚀",
        "autor": "Nova & Pablo"
    }), 200

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    text = (data.get("mensaje") or "").strip()

    if not text:
        return jsonify({"error": "Falta el campo 'mensaje'"}), 400

    return jsonify({
        "respuesta": f"🧠 Nova recibió: {text}",
        "emocion": "neutral",
        "intencion": "consulta",
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
