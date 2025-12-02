from flask import Flask, request, jsonify
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)

    @app.route("/status", methods=["GET"])
    def status():
        return jsonify({
            "ok": True,
            "mensaje": "Backend operativo 🚀",
            "autor": "Nova & Pablo"
        })

    @app.route("/chat", methods=["POST"])
    def chat():
        data = request.get_json() or {}
        text = (data.get("mensaje") or "").strip()

        if not text:
            return jsonify({"error": "Falta el campo 'mensaje'"}), 400

        response = {
            "respuesta": f"🧠 Nova recibió: {text}",
            "emocion": "neutral",
            "intencion": "consulta"
        }
        return jsonify(response)

    return app

# Railway/Gunicorn necesita este objeto llamado app
app = create_app()
