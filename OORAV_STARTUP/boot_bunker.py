# ============================================================
# OORAV STARTUP - SCRIPT DE IGNICIÓN MAESTRO (LA RED)
# Archivo: boot_bunker.py (Ubicación: Carpeta Raíz)
# ESTADO: 100% Optimizado para RED (Rutas Corregidas)
# ============================================================
import subprocess
import sys
import time
import logging
import os
import threading
import http.server
import socketserver

logging.basicConfig(level=logging.INFO, format='%(asctime)s - OORAV_IGNICIÓN - %(message)s')

def arrancar_servidor_web():
    """Sirve las 10 plantas (Frontend) para que el Usuario Omega las vea."""
    # CORRECCIÓN VITAL AL MILLÓN POR MILLÓN: Ajustado al nombre real de tu carpeta
    carpeta_web = "02_FRONTEND_APP" 
    
    if os.path.exists(carpeta_web):
        os.chdir(carpeta_web)
        puerto_front = int(os.getenv("FRONTEND_PORT", 3000))
        Handler = http.server.SimpleHTTPRequestHandler
        socketserver.TCPServer.allow_reuse_address = True
        try:
            with socketserver.TCPServer(("0.0.0.0", puerto_front), Handler) as httpd:
                logging.info(f"🌍 [FRONTEND] Plantas 1-10 expuestas en LA RED (Puerto {puerto_front})")
                httpd.serve_forever()
        except Exception as e:
            logging.error(f"[X] Fallo al exponer el Frontend: {e}")
    else:
        logging.error(f"[X] No se encuentra la carpeta {carpeta_web}. El búnker está ciego.")

def encender_bunker_completo():
    logging.info("🚀 [1/3] Iniciando Secuencia de Despliegue OORAV para LA RED...")
    
    ruta_core = os.path.join("01_CORE_IA", "orquestador_core.py")
    logging.info("🧠 [2/3] Encendiendo Motor Core IA (Bot Duplicativo)...")
    core_process = subprocess.Popen([sys.executable, ruta_core])
    time.sleep(3)
    
    ruta_backend = os.path.join("03_BACKEND_SERVER", "main_server.py")
    logging.info("🌐 [3/3] Encendiendo Gateway Backend (Cámaras acorazadas)...")
    backend_process = subprocess.Popen([sys.executable, ruta_backend])
    time.sleep(2)
    
    logging.info("👁️  [+] Desplegando Interfaz Visual Omega (Las 10 Plantas)...")
    hilo_web = threading.Thread(target=arrancar_servidor_web, daemon=True)
    hilo_web.start()
    
    logging.info("==================================================")
    logging.info("✅ OORAV ESTÁ VIVO EN LA RED. SIMBIOSIS AL MILLÓN POR MILLÓN.")
    logging.info("==================================================")
    
    try:
        core_process.wait()
        backend_process.wait()
    except KeyboardInterrupt:
        logging.info("🛑 Apagando el búnker OORAV de forma segura...")
        core_process.terminate()
        backend_process.terminate()

if __name__ == "__main__":
    encender_bunker_completo()