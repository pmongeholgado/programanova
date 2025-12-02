from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.get("/status")
def status():
    return jsonify({"status": "ok", "message": "Backend funcionando!"})
