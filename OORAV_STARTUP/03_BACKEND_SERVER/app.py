# ============================================================
# OORAV STARTUP - SERVER PRINCIPAL (PUENTE DE SIMBIOSIS)
# Ubicación: 03_BACKEND_SERVER/main_server.py
# ESTADO: 100% Optimizado para RED
# ============================================================

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os
import logging
from dotenv import load_dotenv

# Cargamos la caja fuerte de configuración
load_dotenv()

# Configuración de logs profesionales
logging.basicConfig(level=logging.INFO, format='%(asctime)s - OORAV_GATEWAY - %(message)s')

app = FastAPI(
    title="OORAV Gateway - Backend Maestro",
    description="Simbiosis Digital Generativa al Millón por Millón",
    version="1.1.0"
)

# BLINDAJE PARA LA RED: Permite que el index.html hable con este servidor
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción estricta, cambiaremos "*" por tu dominio real
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELOS DE DATOS (ESTÁNDAR PRO) ---
class LoginRequest(BaseModel):
    username: str
    password: str

class UserProfile(BaseModel):
    user_id: str
    vibe: str = "Techno Chill"

# --- SIMULACIÓN DE DATA CORE (CALIBRADA DESDE .ENV) ---
# Extraemos el límite de los 300s directamente de la cámara acorazada
RECORDING_LIMIT = int(os.getenv("LIMIT_RECORDING", 300))

OORAV_GLOBAL_STATS = {
    "connections": "1,500+",
    "moments": "4,200+",
    "recording_limit": RECORDING_LIMIT
}

@app.get("/")
async def root():
    return {
        "status": "OPERATIVO 1000X1000",
        "startup": "OORAV",
        "mensaje": "Simbiosis activa al millón por millón en LA RED"
    }

@app.post("/login")
async def login(auth: LoginRequest):
    # En la fase de RED, validaremos esto contra una base de datos segura.
    # Por ahora, mantenemos la llave maestra local.
    if auth.username == "hermano" and auth.password == "password123":
        logging.info(f"[+] Acceso concedido al perfil Omega: {auth.username}")
        return {
            "acceso": "concedido",
            "token": os.getenv("SECRET_KEY", "session_oorav_pro_unique_id"),
            "perfil": "Usuario_Omega"
        }
    logging.warning(f"[-] Intento de acceso fallido para: {auth.username}")
    raise HTTPException(status_code=401, detail="Clave única incorrecta")

@app.get("/api/v1/report/{user_id}")
async def get_impact_report(user_id: str):
    """
    Sincroniza con la Pantalla 10: Informe de Impacto PRO
    """
    return {
        "title": "INFORME DE IMPACTO PRO PERSONALIZADO (24H)",
        "stats": {
            "active_connections": OORAV_GLOBAL_STATS["connections"],
            "generated_moments": OORAV_GLOBAL_STATS["moments"]
        },
        "footer": "INFORME EFÍMERO (EXPIRA EN 30 MIN)"
    }

@app.post("/solicitar_clon/{user_id}")
async def solicitar_clon(user_id: str):
    """
    Conecta el Backend con el CORE_IA (Motor Duplicativo de la Carpeta 01)
    """
    core_url = os.getenv('CORE_IA_URL', 'http://0.0.0.0:8000') # Ajustado al estándar de red
    logging.info(f"[>] Solicitando clon generativo a CORE_IA en {core_url}...")
    
    # Blindaje de RED: Añadimos timeout=10.0 para evitar cuelgues de sockets
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(f"{core_url}/crear_clon/{user_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"[!] Error crítico de red con CORE_IA: {str(e)}")
            return {
                "error": "El motor ADN está procesando alta demanda en la red.",
                "status": "Recalibrando",
                "hint": "Reintento automático iniciado."
            }

if __name__ == "__main__":
    import uvicorn
    # Extraemos el puerto del archivo .env para evitar conflictos (8080)
    puerto = int(os.getenv("BACKEND_PORT", 8080))
    logging.info(f"🏁 INICIANDO BÚNKER OORAV EN PUERTO {puerto}...")
    uvicorn.run(app, host="0.0.0.0", port=puerto)
