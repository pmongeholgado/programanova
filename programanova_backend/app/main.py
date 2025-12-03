from flask import Flask, jsonify
from flask_cors import CORS

# Crear la app de Flask
app = Flask(__name__)
CORS(app)

# Ruta de salud (/status)
@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "status": "ok",
        "message": "Backend funcionando",
        "autor": "Nova & Pablo"
    })
