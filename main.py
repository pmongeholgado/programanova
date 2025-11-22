from matraz import Matraz, enviar_desde_directorio
import os

# Crear la aplicación Matraz
aplicación = Matraz(__name__, carpeta_estática='')

# Ruta principal → devuelve index.html
@aplicación.ruta('/')
def índice():
    return enviar_desde_directorio('.', 'index.html')

# Ruta para servir cualquier archivo estático o recurso
@aplicación.ruta('/<ruta:ruta>')
def proxy_estático(camino):
    return enviar_desde_directorio('.', camino)

# Ejecución principal (compatible con Railway)
if __name__ == '__main__':
    puerto = int(os.environ.get('PORT', 8080))  # Puerto dinámico para Railway
    aplicación.correr(anfitrión='0.0.0.0', puerto=puerto)
