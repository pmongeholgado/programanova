from flask import Flask, request, jsonify

# =========================
# INICIAR FLASK
# =========================
app = Flask(__name__)

# =========================
# RUTA RAÍZ (SALUD / CHECK)
# =========================
@app.route("/", methods=["GET"])
def health():
    return "Backend Programanova OK", 200

# =========================
# API /chat
# =========================
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    text = (data.get("mensaje") or "").strip()

    # Respuesta DEMO muy sencilla
    return jsonify({
        "ok": True,
        "mensaje_recibido": text,
        "respuesta": f"Nova recibió: {text}",
    })


# =========================
# RUN SERVER (solo local)
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
