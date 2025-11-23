from flask import Flask, send_from_directory
import os

# Crear la aplicación Flask
# static_folder='backend/frontend' → aquí está tu web completa
app = Flask(__name__, static_folder='backend/frontend', static_url_path='')

# Ruta principal → entrega index.html
@app.route('/')
def index():
    return send_from_directory('backend/frontend', 'index.html')

# Ruta dinámica → entrega cualquier archivo o carpeta
@app.route('/<path:archivo>')
def archivos(archivo):
    return send_from_directory('backend/frontend', archivo)

# Ejecutar servidor (Railway asigna puerto automáticamente)
if __name__ == '__main__':
    puerto = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=puerto)
