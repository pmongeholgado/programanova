from flask import Flask, send_from_directory
import os

app = Flask(
    __name__,
    static_folder='../frontend',        # Carpeta con TU WEB COMPLETA
    static_url_path=''                 # Esto permite servir /index.html directamente
)

# Ruta principal → muestra index.html del frontend
@app.route('/')
def raiz():
    return send_from_directory('../frontend', 'index.html')


# Rutas para cualquier archivo: CSS, JS, imágenes, assets, páginas…
@app.route('/<path:ruta>')
def archivos(ruta):
    return send_from_directory('../frontend', ruta)


if __name__ == '__main__':
    puerto = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=puerto)
