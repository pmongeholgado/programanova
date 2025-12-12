from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from openai import OpenAI

# =========================
# CONFIGURACIÓN OPENAI
# =========================
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# =========================
# APP
# =========================
app = FastAPI(title="Programa Nova Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # producción OK (frontend separado)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# MODELOS
# =========================
class ChatRequest(BaseModel):
    message: str


class GenerarRequest(BaseModel):
    titulo: str
    num_diapositivas: int
    contenido: str


# =========================
# ENDPOINT RAÍZ
# =========================
@app.get("/")
def root():
    return {
        "status": "ok",
        "mensaje": "Backend Programa Nova activo"
    }


# =========================
# CHAT CON NOVA (IA REAL)
# =========================
@app.post("/chat")
def chat_nova(data: ChatRequest):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres Nova, una IA colaboradora creada junto a Pablo. "
                        "Respondes con claridad, humanidad y estructura."
                    )
                },
                {
                    "role": "user",
                    "content": data.message
                }
            ]
        )

        texto = response.choices[0].message.content.strip()

        return {
            "respuesta": texto,
            "emocion": "activa",
            "intencion": "asistencia",
            "resultado": "OK",
            "resumen": "Mensaje procesado correctamente"
        }

    except Exception as e:
        return {
            "error": "Error procesando el mensaje",
            "detalle": str(e)
        }


# =========================
# GENERADOR DE PRESENTACIONES (IA REAL)
# =========================
@app.post("/generar")
def generar_presentacion(data: GenerarRequest):
    try:
        prompt = f"""
Genera una estructura de presentación profesional.

Título: {data.titulo}
Número de diapositivas: {data.num_diapositivas}

Contenido base:
{data.contenido}

Devuelve:
- Título de cada diapositiva
- Contenido resumido por diapositiva
- Estilo claro, profesional y didáctico
"""

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres un generador experto de presentaciones profesionales."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        resultado = response.choices[0].message.content.strip()

        return {
            "mensaje": "Presentación generada correctamente",
            "resultado": resultado
        }

    except Exception as e:
        return {
            "error": "Error generando la presentación",
            "detalle": str(e)
        }
