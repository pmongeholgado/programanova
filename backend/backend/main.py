from flask import Flask, send_from_directory
import os

app = Flask(__name__, static_folder='.')

@app.route('/')
def index():
    return send_from_directory('sitio', 'index.html')

@app.route('/<path:ruta>')
def archivos(ruta):
    return send_from_directory('.', ruta)

if __name__ == '__main__':
    puerto = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=puerto)
