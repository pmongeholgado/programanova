from flask import Flask, send_from_directory
import os

app = Flask(__name__, static_folder='sitio', static_url_path='')

@app.route('/')
def index():
    return send_from_directory('sitio', 'index.html')

@app.route('/<path:archivo>')
def archivos(archivo):
    return send_from_directory('sitio', archivo)

if __name__ == '__main__':
    puerto = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=puerto)
