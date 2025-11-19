# -*- coding: utf-8 -*-

from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

"""
API del Orquestador IA.

Aquí definimos también la función `procesar_mensaje` para evitar depender
de un módulo externo `main` que está dando problemas al empaquetar con PyInstaller.
"""

# === Importamos la lógica del orquestador ===
try:
    from orchestrator.intent_router import route_intent as _route_intent
except Exception:
    _route_intent = None

try:
    from orchestrator.emotion_manager import analyze_emotion as _analyze_emotion
except Exception:
    _analyze_emotion = None

try:
    from orchestrator.tone_manager import analyze_tone as _analyze_tone
except Exception:
    _analyze_tone = None

try:
    from orchestrator.summary_generator import generate_summary as _generate_summary
except Exception:
    _generate_summary = None


def procesar_mensaje(texto: str):
    """
    Función principal que procesa un mensaje de texto y devuelve:
    - emoción (str)
    - intención (str)
    - respuesta (str)
    - resumen (dict o str)

    Usa los módulos del orquestador si están disponibles.
    Si algo falla, devuelve valores seguros por defecto.
    """

    # Intención
    if _route_intent is not None:
        try:
            intencion = _route_intent(texto)
        except Exception:
            intencion = "desconocida"
    else:
        intencion = "desconocida"

    # Emoción
    if _analyze_emotion is not None:
        try:
            emocion = _analyze_emotion(texto)
        except Exception:
            emocion = "neutra"
    else:
        emocion = "neutra"

    # Tono / respuesta preliminar
    if _analyze_tone is not None:
        try:
            resp = _analyze_tone(texto)
            # Nos aseguramos de que la respuesta SIEMPRE sea texto
            respuesta = resp if isinstance(resp, str) else str(resp)
        except Exception:
            # Si algo falla, devolvemos el propio texto como respuesta básica
            respuesta = texto
    else:
        # Si no hay analizador de tono, también devolvemos el texto original
        respuesta = texto

    # Resumen
    if _generate_summary is not None:
        try:
            resumen = _generate_summary(texto)
        except Exception:
            resumen = {"resumen": texto[:200]}
    else:
        resumen = {"resumen": texto[:200]}

    return emocion, intencion, respuesta, resumen


# === Definición de la API FastAPI ===

app = FastAPI(title="AI Orchestrator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatInput(BaseModel):
    mensaje: str


class ChatResponse(BaseModel):
    emocion: str
    intencion: str
    respuesta: str
    resumen: dict
    timestamp: str


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(data: ChatInput):
    emocion, intencion, respuesta, resumen = procesar_mensaje(data.mensaje)
    from datetime import datetime
    return ChatResponse(
        emocion=emocion,
        intencion=intencion,
        respuesta=respuesta,
        resumen=resumen,
        timestamp=datetime.now().isoformat()
    )


if __name__ == "__main__":
    # Ejecutar el servidor Uvicorn cuando se lance api_server.py directamente
    uvicorn.run(app, host="0.0.0.0", port=8000)
  
