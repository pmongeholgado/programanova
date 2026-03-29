from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
import sys
import os
from dotenv import load_dotenv

# 1. Cargar las variables de entorno del archivo .env
load_dotenv()

# 2. Configuración de rutas dinámicas para la red
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.duplicativo_beta import BotDuplicativo

# 🔥 SELLO DE ÉLITE: El nombre oficial y tu autoría en la raíz de la API
app = FastAPI(
    title="ALTEGRIOS - Sistema de IA Generativa de Pablo Monge",
    description="IA Real Generativa 100% Gratuita. Creado en Cáceres, España."
)

# 3. Servir imágenes estáticas (para que el bot sea "físico" y muestre su icono en la red)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 4. Obtener configuración desde el entorno
BOT_ID = os.getenv("BOT_ID", "bot_alpha_01")
MODEL_PATH = os.getenv("MODEL_PATH", "/app/brain/modelos/llm-local.bin")

# 5. Inicializamos el bot con la configuración de red
bot = BotDuplicativo(bot_id=BOT_ID, model_path=MODEL_PATH)

class UserRequest(BaseModel):
    mensaje: str

@app.post("/interactuar")
async def interactuar_con_bot(request: UserRequest):
    print(f"Procesando interacción en la red para: {request.mensaje}")
    
    # Lógica generativa propia y mimetización (análisis profundo)
    respuesta = bot.interact(request.mensaje)
    
    return {
        "bot_id": bot.bot_id, 
        "respuesta": respuesta,
        "visual": f"/static/images/genesis_resonator_manifestation.webp",
        "autor": "Pablo Monge (Cáceres, España)", # 🔥 Tu firma inseparable
        "tecnologia": "ALTEGRIOS - Uso libre y gratuito"
    }

if __name__ == "__main__":
    import uvicorn
    # En la red, el puerto suele ser definido por el orquestador
    puerto = int(os.getenv("PORT", 8000))
    print(f"--- NÚCLEO GENERATIVO ALTEGRIOS ACTIVO EN PUERTO {puerto} ---")
    uvicorn.run(app, host="0.0.0.0", port=puerto)