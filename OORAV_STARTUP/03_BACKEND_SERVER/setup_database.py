# ============================================================
# OORAV STARTUP - FORJA DE BASE DE DATOS (SQLITE)
# Ubicación: 03_BACKEND_SERVER/setup_database.py
# ESTADO: 100% Optimizado para RED
# ============================================================

import sqlite3
import logging
import os

# Configuración de logs profesionales
logging.basicConfig(level=logging.INFO, format='%(asctime)s - OORAV_DB - %(message)s')

def inicializar_bunker_datos():
    """
    Crea el archivo database.db en formato binario correcto y 
    levanta las tablas necesarias para la Simbiosis en LA RED.
    """
    # BLINDAJE PARA LA RED: Ruta absoluta para evitar que el servidor Linux 
    # guarde la base de datos en el directorio raíz o temporal por error.
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_db = os.path.join(directorio_actual, "database.db")
    
    conexion = None
    try:
        conexion = sqlite3.connect(ruta_db)
        cursor = conexion.cursor()

        # BLINDAJE DE INTEGRIDAD: Activar validación de claves foráneas en SQLite
        cursor.execute("PRAGMA foreign_keys = ON;")

        logging.info(f"[+] Forjando estructura de la base de datos OORAV en: {ruta_db}")

        # 1. Tabla de Perfiles Omega (Identidad Digital)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario TEXT PRIMARY KEY,
            vibe_base TEXT,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # 2. Tabla de Momentos (El pulso global)
        # Aquí se guardan los registros tras los 300 segundos exactos de captura auditiva
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS momentos_simbiosis (
            id_momento INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario TEXT,
            cita_generada TEXT,
            tiempo_captura INTEGER DEFAULT 300,
            FOREIGN KEY(id_usuario) REFERENCES usuarios(id_usuario)
        )
        ''')

        conexion.commit()
        logging.info("🏁 Base de datos blindada, estructurada y lista al 1000X1000.")

    except Exception as e:
        logging.error(f"[X] Error crítico forjando la base de datos en la red: {e}")
    finally:
        # Garantiza que el archivo se libere siempre, evitando bloqueos (database is locked)
        if conexion:
            conexion.close()

if __name__ == "__main__":
    inicializar_bunker_datos()