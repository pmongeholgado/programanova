from flask import Flask, send_from_directory
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SITIO_DIR = os.path.join(BASE_DIR, "sitio")

app = Flask(__name__, static_folder=SITIO_DIR)

@app.route('/')
def index():
    return send_from_directory(SITIO_DIR, 'index.html')

@app.route('/<path:archivo>')
def archivos(archivo):
    return send_from_directory(SITIO_DIR, archivo)

if __name__ == '__main__':
    puerto = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=puerto)
