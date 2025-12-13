from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import openai

# ======================================================
# CONFIGURACIÓN OPENAI
# ======================================================

openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    print("⚠️ WARNING: OPENAI_API_KEY no está configurada")

# ======================================================
# APP FASTAPI
# ======================================================

app = FastAPI(
    title="Programa Nova Backend",
    description="Backend oficial del Programa Nova Presentaciones",
    version="1.0.0"
)

# ======================================================
# CORS (frontend Vercel + pruebas)
# ======================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # luego lo cerramos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================================================
# MODELOS
# ======================================================

class GenerarRequest(BaseModel):
    titulo: str | None = "Presentación generada con Nova"
    num_diapositivas: int = 10
    contenido: str

class GenerarResponse(BaseModel):
    slides: list[str]
    resumen: str

# ======================================================
# ENDPOINT /generar (IA REAL)
# ======================================================

@app.post("/generar", response_model=GenerarResponse)
async def generar_presentacion(data: GenerarRequest):
    """
    Genera el contenido de una presentación usando IA real.
    Devuelve textos de diapositivas estructurados.
    """

    if not data.contenido.strip():
        raise HTTPException(status_code=400, detail="Contenido vacío")

    try:
        prompt = f"""
Eres Nova, una IA experta en creación de presentaciones profesionales.

TÍTULO:
{data.titulo}

CONTENIDO BASE:
{data.contenido}

INSTRUCCIONES:
- Genera {data.num_diapositivas} diapositivas
- Cada diapositiva debe ser clara, profesional y concisa
- Devuelve SOLO texto, sin markdown
- Cada diapositiva separada por '---'
- Al final añade un resumen ejecutivo
"""

        completion = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Eres Nova, asistente profesional de presentaciones."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
        )

        raw_text = completion.choices[0].message.content.strip()

        bloques = raw_text.split("---")
        slides = [b.strip() for b in bloques if b.strip()]

        resumen = slides[-1] if len(slides) > 1 else "Presentación generada correctamente."

        return GenerarResponse(
            slides=slides[:-1],
            resumen=resumen
        )

    except Exception as e:
        print("❌ ERROR /generar:", e)
        raise HTTPException(status_code=500, detail="Error generando la presentación")

# ======================================================
# HEALTHCHECK
# ======================================================

@app.get("/")
async def root():
    return {
        "status": "OK",
        "service": "Programa Nova Backend",
        "ia": "activa"
    }
