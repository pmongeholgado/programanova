# ============================
# Programa Nova - Backend REAL
# main.py (FINAL)
# ============================

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from openai import OpenAI
import stripe
from app.ia_assets import generate_image_data_url

# ============================
# CONFIGURACIÓN OPENAI
# ============================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("❌ OPENAI_API_KEY no está definida en las variables de entorno")

client = OpenAI(api_key=OPENAI_API_KEY)

# ============================
# CONTADOR SENCILLO PORTADA
# ============================

VISITAS_FILE = Path("contador_visitas_nova.json")


def leer_contador_visitas():
    try:
        if VISITAS_FILE.exists():
            data = json.loads(VISITAS_FILE.read_text(encoding="utf-8"))
            return int(data.get("visitas", 0))
    except Exception:
        return 0
    return 0


def guardar_contador_visitas(total):
    VISITAS_FILE.write_text(
        json.dumps({"visitas": total}, ensure_ascii=False),
        encoding="utf-8"
    )
# ============================
# CONFIGURACIÓN STRIPE
# ============================

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")

if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

# ============================
# APP FASTAPI
# ============================

app = FastAPI(
    title="Programa Nova Backend",
    version="1.0.0",
    description="Backend real con IA para Nova Presentaciones"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://programanovapresentaciones.com",
        "https://www.programanovapresentaciones.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
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

class ImagenRequest(BaseModel):
    titulo: Optional[str] = "Imagen Nova"
    prompt: str


class ImagenResponse(BaseModel):
    ok: bool
    dataUrl: str
    
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

# ============================
# CONTADOR VISITAS PORTADA
# ============================

@app.post("/contador-visita")
def contador_visita():
    total = leer_contador_visitas() + 1
    guardar_contador_visitas(total)

    return {
        "ok": True,
        "visitas": total
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

        texto = response.output_text.strip()

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
# ============================
# GENERADOR DE IMÁGENES (IA REAL)
# ============================

@app.post("/generar-imagen", response_model=ImagenResponse)
def generar_imagen(data: ImagenRequest):
    try:
        prompt_final = (data.prompt or "").strip()
        if not prompt_final:
            prompt_final = f"Imagen profesional sobre: {data.titulo}"

        data_url = generate_image_data_url(prompt_final)

        return ImagenResponse(
            ok=True,
            dataUrl=data_url
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# ============================
# STRIPE CHECKOUT PORTERO
# ============================

@app.post("/crear-checkout-portero")
def crear_checkout_portero():

    if not STRIPE_SECRET_KEY:
        raise HTTPException(status_code=500, detail="Stripe no configurado")

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "eur",
                        "product_data": {
                            "name": "Acceso inicial Edificio Nova"
                        },
                        "unit_amount": 90,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url="https://programanovapresentaciones.com?acceso=ok",
            cancel_url="https://programanovapresentaciones.com?acceso=cancel",
        )

        return {"url": session.url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
   
