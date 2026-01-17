# ============================
# Programa Nova - Backend REAL (PRO)
# main_pro.py (FINAL)
# ============================

import os
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from openai import OpenAI

from app.ia_assets import generate_image_data_url, generate_chart_spec

import traceback

# ============================
# CONFIGURACIÓN OPENAI
# ============================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY or OPENAI_API_KEY.strip() == "":
    raise RuntimeError("❌ Backend PRO detenido: falta OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)
print("✅ Backend PRO iniciado con IA activa")

# ============================
# APP FASTAPI
# ============================

app = FastAPI(
    title="Programa Nova Backend",
    version="1.0.0",
    description="Backend real con IA para Nova Presentaciones"
)
api = APIRouter(prefix="/api")

# ============================
# CORS (UNO SOLO, sin duplicados)
# ============================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://programanovapresentaciones.com",
        "https://www.programanovapresentaciones.com",
    ],
    allow_credentials=False,
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


# ============================
# ENDPOINT RAÍZ (UNO SOLO)
# ============================

@app.get("/")
def root():
    return {
        "status": "ok",
        "mensaje": "Programa Nova Backend PRO operativo",
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
                {"role": "system", "content": "Eres Nova, IA colaborativa del proyecto Programa Nova."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_output_tokens=500
        )

        texto = ""
        try:
            if hasattr(response, "output_text") and response.output_text:
                texto = response.output_text.strip()
            elif hasattr(response, "output") and response.output:
                for item in response.output:
                    if item.get("type") == "message":
                        for content in item.get("content", []):
                            if content.get("type") == "output_text":
                                texto += content.get("text", "")
                texto = texto.strip()
        except Exception as e:
            texto = f"Error procesando respuesta del modelo: {str(e)}"

        if not texto:
            texto = "Respuesta vacía del modelo."

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

def decide_needs(title: str):
    t = title.lower()
    return {
        "image": any(k in t for k in ["imagen", "portada", "impacto", "futuro", "cierre", "demo"]),
        "chart": any(k in t for k in ["grafico", "gráfico", "datos", "comparativa", "roadmap"])
    }

@app.post("/generar", response_model=GenerarResponse)
async def generar_presentacion(data: GenerarRequest):
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
                {"role": "system", "content": "Eres un generador profesional de presentaciones."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_output_tokens=700
        )

        texto = getattr(response, "output_text", "") or ""
        texto = texto.strip()

        lineas = [l.strip() for l in texto.split("\n") if l.strip()]

        slides = []
        current_title = None
        current_bullets = []

        for linea in lineas:
            if linea[0].isdigit() and "." in linea[:4]:
                if current_title:
                    needs = decide_needs(current_title)
                    slide = {
                        "title": current_title,
                        "bullets": current_bullets,
                        "needs": needs
                    }

                    if needs.get("image"):
                        slide["imageData"] = generate_image_data_url(
                            f"Imagen profesional para diapositiva titulada '{current_title}'"
                        )

                    if needs.get("chart"):
                        slide["chartSpec"] = generate_chart_spec({
                            "title": current_title,
                            "bullets": current_bullets
                        })

                    slides.append(slide)

                current_title = linea.split(".", 1)[1].strip()
                current_bullets = []
            else:
                current_bullets.append(linea.lstrip("- ").strip())

        if current_title:
            needs = decide_needs(current_title)
            slide = {
                "title": current_title,
                "bullets": current_bullets,
                "needs": needs
            }

            if needs.get("image"):
                slide["imageData"] = generate_image_data_url(
                    f"Imagen profesional para diapositiva titulada '{current_title}'"
                )

            if needs.get("chart"):
                slide["chartSpec"] = generate_chart_spec({
                    "title": current_title,
                    "bullets": current_bullets
                })

            slides.append(slide)

        return GenerarResponse(
            mensaje="Presentación generada correctamente con IA real (imagenes + graficos)",
            estructura=slides
        )

    except Exception as e:
        print("🔥 ERROR en /generar PRO:", str(e))
        print(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "where": "/generar",
                "message": str(e),
                "trace": traceback.format_exc()
            }
        )

# ============================
# IA ASSETS (IMAGEN + GRÁFICO)
# ============================

class ImagenRequest(BaseModel):
    titulo: str = ""
    prompt: str = ""


class ImagenResponse(BaseModel):
    dataUrl: str


class GraficoRequest(BaseModel):
    titulo: str = ""
    contexto: str = ""


class GraficoResponse(BaseModel):
    type: str
    title: str
    labels: list
    values: list


@app.post("/generar-imagen", response_model=ImagenResponse)
def generar_imagen(data: ImagenRequest):
    prompt = data.prompt or f"Imagen profesional para: {data.titulo}"
    data_url = generate_image_data_url(prompt)
    return {"dataUrl": data_url}


@app.post("/generar-grafico", response_model=GraficoResponse)
def generar_grafico(data: GraficoRequest):
    spec = generate_chart_spec({
        "title": data.titulo,
        "contexto": data.contexto
    })
    return spec
    
app.include_router(api)
