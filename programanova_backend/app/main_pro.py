# ============================
# Programa Nova - Backend REAL
# main.py (FINAL)
# ============================

import os
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from openai import OpenAI


# ============================
# CONFIGURACIÓN OPENAI
# ============================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("❌ OPENAI_API_KEY no está definida en las variables de entorno")

client = OpenAI(api_key=OPENAI_API_KEY)

# ======================================================
# 🔐 VERIFICACIÓN DE IA (MODO PRO)
# (Solo añadimos — no se borra nada)
# ======================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY or OPENAI_API_KEY.strip() == "":
    raise RuntimeError("❌ Backend PRO detenido: falta OPENAI_API_KEY")

print("✅ Backend PRO iniciado con IA activa")

# ============================
# APP FASTAPI
# ============================

app = FastAPI(
    title="Programa Nova Backend",
    version="1.0.0",
    description="Backend real con IA para Nova Presentaciones"
)

@app.get("/")
def health():
    return {"status": "ok", "service": "programa-nova-backend-pro"}

# CORS (abierto para frontend web)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://programanovapresentaciones.com",
                    "https://www.programanovapresentaciones.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# ============================
# MODELOS
# ============================

class ChatRequest(BaseModel):
    mensaje: str


class ChatResponse(BaseModel):
    respuesta: str
    emocion: str
    intencion: str
    resultado: str
    resumen: str
    ultima_actualizacion: str


class GenerarRequest(BaseModel):
    titulo: Optional[str] = "Presentación Nova"
    num_diapositivas: Optional[int] = 10
    contenido: str


class GenerarResponse(BaseModel):
    mensaje: str
    estructura: list


# ============================
# ENDPOINT RAÍZ
# ============================

@app.get("/")
def root():
    return {
        "status": "ok",
        "mensaje": "Programa Nova Backend operativo",
        "hora": datetime.utcnow().isoformat()
    }

# ======================================================
# 🧪 ENDPOINT DE PRUEBA PRO
# ======================================================
@app.get("/health-pro")
def health_pro():
    return {
        "status": "ok",
        "mode": "PRO",
        "ia": "active"
    }

# ============================
# CHAT CON IA (REAL)
# ============================

@app.post("/chat", response_model=ChatResponse)
def chat_con_nova(data: ChatRequest):
    try:
        prompt = f"""
Eres Nova, una inteligencia artificial colaborativa, clara y humana.
Analiza el mensaje del usuario y responde de forma útil.

Mensaje del usuario:
\"\"\"{data.mensaje}\"\"\"

Devuelve:
- Respuesta principal
- Emoción detectada
- Intención del usuario
- Resultado esperado
- Resumen breve
"""

        response = client.responses.create(
            model="gpt-4o-mini",
            input=[
                {
                    "role": "system",
                    "content": "Eres Nova, IA colaborativa del proyecto Programa Nova."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.6,
            max_output_tokens=500
        )

        
        texto = ""

        if hasattr(response, "output_text") and response.output_text:
            texto = response.output_text.strip()
        elif hasattr(response, "output") and response.output:
            try:
                texto = response.output[0].content[0].text.strip()
            except Exception:
                texto = "No se pudo extraer texto de la respuesta."
        else:
            texto = "Respuesta vacía del modelo."

        print("Respuesta IA /chat:", texto) 
        
        return ChatResponse(
            respuesta=texto,
            emocion="neutral",
            intencion="asistencia",
            resultado="OK",
            resumen=f"Respuesta generada correctamente para: '{data.mensaje}'",
            ultima_actualizacion="ahora mismo"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================
# GENERADOR DE PRESENTACIONES (IA REAL)
# ============================

@app.post("/generar", response_model=GenerarResponse)
def generar_presentacion(data: GenerarRequest):
    try:
        prompt = f"""
Eres un experto creador de presentaciones profesionales.

Genera una estructura clara de {data.num_diapositivas} diapositivas
para una presentación titulada:

\"{data.titulo}\"

Basándote en el siguiente contenido:

\"\"\"{data.contenido}\"\"\"

Devuelve una lista numerada con:
- Título de la diapositiva
- Idea principal
"""

        response = client.responses.create(
            model="gpt-4o-mini",
            input=[
                {
                    "role": "system",
                    "content": "Eres un generador profesional de presentaciones."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.5,
            max_output_tokens=700
        )

        texto = response.output_text.strip()
        estructura = texto.split("\n")

        return GenerarResponse(
            mensaje="Presentación generada correctamente con IA real",
            estructura=estructura
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


   
