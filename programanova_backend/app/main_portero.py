# main_portero.py
# Arranque seguro: envuelve la app existente SIN modificarla

from main import app  # <- importa tu app actual (NO se toca main.py)

from nova_portero.middleware_portero import PorteroMiddleware
from nova_portero.config_portero import PORTERO_CONFIG

# Activamos el Portero como "capa envolvente"
app.add_middleware(PorteroMiddleware, config=PORTERO_CONFIG)
