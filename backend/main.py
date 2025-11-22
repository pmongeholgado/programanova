from flask import Flask, send_from_directory
import os

app = Flask(__name__, static_folder='sitio')

# Ruta principal -> carga index.html desde /backend/sitio/
@app.route('/')
def index():
    return send_from_directory('sitio', 'index.html')

# Cualquier archivo de la carpeta sitio (CSS, JS, imágenes…)
@app.route('/<path:ruta>')
def archivos(ruta):
    return send_from_directory('sitio', ruta)

if __name__ == '__main__':
    # Railway asigna automáticamente un puerto → lo recogemos
    puerto = int(os.environ.get('PORT', 8000))
    
    # Ejecutar la aplicación
    app.run(host='0.0.0.0', port=puerto)
