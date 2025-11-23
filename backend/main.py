from flask import Flask, send_from_directory
import os

# Servidor Flask
app = Flask(__name__)

# === RUTA PRINCIPAL ===
@app.route('/')
def root():
    return send_from_directory('sitio', 'index.html')

# === RUTA FRONTEND: JS, CSS, IMÁGENES, FONTS, ETC. ===
@app.route('/frontend/<path:archivo>')
def frontend(archivo):
    return send_from_directory('frontend', archivo)

# === RUTA GLOBAL: ASSETS/LOGOS/ICONS ===
@app.route('/assets/<path:archivo>')
def assets(archivo):
    return send_from_directory('frontend/assets', archivo)

# === API DE EJEMPLO ===
@app.route('/api/info')
def info():
    return {"status": "online", "proyecto": "Programanova"}

# === ARRANQUE ===
if __name__ == '__main__':
    puerto = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=puerto)
