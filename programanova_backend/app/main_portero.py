# main_portero.py
# Arranque seguro: envuelve la app existente SIN modificarla

from app.main_pro import app  # 👈 IMPORT REAL SEGÚN TU DOCKERFILE

from nova_portero.middleware_portero import PorteroMiddleware
from nova_portero.config_portero import PORTERO_CONFIG

# Activamos el Portero como "capa envolvente"
app.add_middleware(PorteroMiddleware, config=PORTERO_CONFIG)
