from flask import Flask, jsonify
from flask_cors import CORS

# Crear la app de Flask
app = Flask(__name__)
CORS(app)

# Ruta principal (/)
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "ok",
        "message": "API Programanova funcionando",
        "autor": "Nova & Pablo"
    })

# Ruta de salud (/status)
@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "status": "ok",
        "message": "Backend funcionando",
        "autor": "Nova & Pablo"
    })
