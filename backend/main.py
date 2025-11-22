from flask import Flask, send_from_directory
import os

# Ruta del directorio donde están tus archivos HTML, CSS, JS, imágenes, etc.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SITIO_DIR = os.path.join(BASE_DIR, "sitio")

app = Flask(__name__, static_folder=SITIO_DIR, static_url_path='')

# Página principal → entrega index.html
@app.route('/')
def index():
    return send_from_directory(SITIO_DIR, 'index.html')

# Cualquier otro archivo dentro de /sitio (css, js, imágenes, otras páginas…)
@app.route('/<path:archivo>')
def servir_archivos(archivo):
    return send_from_directory(SITIO_DIR, archivo)

if __name__ == '__main__':
    # Railway asigna automáticamente un puerto → lo obtenemos
    puerto = int(os.environ.get("PORT", 8000))
    
    # Ejecutar aplicación en modo producción
    app.run(host='0.0.0.0', port=puerto)
