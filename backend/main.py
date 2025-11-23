from flask import Flask, send_from_directory
import os

# Ruta absoluta hacia la carpeta frontend dentro de backend
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')

# Ruta principal → sirve index.html
@app.route('/')
def serve_index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

# Ruta para cualquier archivo dentro del frontend (CSS, JS, imágenes, assets…)
@app.route('/<path:archivo>')
def serve_static(archivo):
    return send_from_directory(FRONTEND_DIR, archivo)

# Railway asigna el puerto automáticamente → recogerlo
if __name__ == '__main__':
    puerto = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=puerto)
