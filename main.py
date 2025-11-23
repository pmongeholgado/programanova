from flask import Flask, request, jsonify, send_from_directory
import os

app = Flask(
    __name__,
    static_folder="../frontend",
    static_url_path=""
)

@app.route("/")
def home():
    return send_from_directory("../frontend", "index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_text = data.get("mensaje", "")

    # ---- Simulación IA mínima ----
    response_text = f"Tu pregunta fue: {user_text}"
    emotion = "neutral"
    intention = "consulta"
    summary = "El usuario realizó una pregunta directa."

    return jsonify({
        "respuesta": response_text,
        "emocion": emotion,
        "intencion": intention,
        "resumen": summary
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
