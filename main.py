from flask import Flask, send_from_directory
import os

app = Flask(__name__)

# ----------------------------
# 1) LANDING PROFESIONAL (Página pública)
# ----------------------------
@app.route('/')
def landing():
    return send_from_directory('sitio', 'index.html')

@app.route('/sitio/<path:archivo>')
def sitio_archivos(archivo):
    return send_from_directory('sitio', archivo)

# ----------------------------
# 2) ORQUESTADOR IA (Interfaz dinámica)
# ----------------------------
@app.route('/orquestador')
def orquestador():
    return send_from_directory('Interfaz', 'index.html')

@app.route('/Interfaz/<path:archivo>')
def interfaz_archivos(archivo):
    return send_from_directory('Interfaz', archivo)

# ----------------------------
# 3) Servir archivos de la raíz si alguien los pide (solo por compatibilidad)
# ----------------------------
@app.route('/<path:archivo>')
def raiz_archivos(archivo):
    return send_from_directory('.', archivo)

# ----------------------------
# 4) EJECUCIÓN
# ----------------------------
if __name__ == '__main__':
    puerto = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=puerto)
