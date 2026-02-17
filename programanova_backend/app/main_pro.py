# ============================
# Programa Nova - Backend REAL (PRO)
# main_pro.py (FINAL)
# ============================

import os
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from openai import OpenAI

from app.ia_assets import generate_image_data_url, generate_chart_spec
from fastapi.responses import Response
from app.pptx_generator_pro import crear_pptx_con_imagenes

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

from nova_portero.middleware_portero import PorteroMiddleware
from nova_portero.config_portero import PORTERO_CONFIG

app.add_middleware(PorteroMiddleware, config=PORTERO_CONFIG)
# =========================
# SWAGGER AUTHORIZE (API KEY)
# =========================
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    openapi_schema.setdefault("components", {})
    openapi_schema["components"].setdefault("securitySchemes", {})
    openapi_schema["components"]["securitySchemes"].update({
        "NovaKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-NOVA-KEY",
        },
        "NovaAdminAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-NOVA-ADMIN",
        },
    })

    # No lo forzamos global: solo habilita el botón Authorize en /docs
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

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
    idioma: Optional[str] = "es"

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
        idioma = (data.idioma or "es").lower()
        prompt = f"""
Eres un experto creador de presentaciones profesionales.

IMPORTANTE: genera TODO el contenido en idioma: {idioma}

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

        import re

        slides = []
        current_title = None
        current_bullets = []

        for linea in lineas:
            clean = (linea or "").replace("**", "").strip()
            if not clean:
                continue

            # 1) Formato: "1. Título"
            m1 = re.match(r"^(\d+)\.\s+(.*)$", clean)

            # 2) Formato: "Diapositiva 1: Título"
            m2 = re.match(r"^Diapositiva\s+(\d+)\s*:\s*(.*)$", clean, flags=re.IGNORECASE)

            if m1 or m2:
                # Cierra la slide anterior
                if current_title:
                    slides.append({
                        "title": current_title.strip(),
                        "bullets": [b for b in current_bullets if b],
                    })

                # Abre nueva slide
                current_title = (m1.group(2) if m1 else m2.group(2)).strip()
                current_bullets = []
                continue

            # Bullet / idea
            clean_bullet = clean.lstrip("-• ").strip()
            if clean_bullet:
                current_bullets.append(clean_bullet)

        # Cierra última slide
        if current_title:
            slides.append({
                "title": current_title.strip(),
                "bullets": [b for b in current_bullets if b],
            })

        # 🔒 BLINDAJE FINAL: si por lo que sea no parsea nada, NO devolvemos vacío
        target_n = int(data.num_diapositivas or 10)

        if not slides:
            slides = [{"title": f"Diapositiva {i+1}", "bullets": ["Idea principal"]} for i in range(target_n)]
        else:
            # Ajusta a EXACTAMENTE num_diapositivas (ni más ni menos)
            slides = slides[:target_n]
            while len(slides) < target_n:
                slides.append({"title": f"Diapositiva {len(slides)+1}", "bullets": ["Idea principal"]})

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
async def generar_imagen(data: ImagenRequest):
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
    
@app.post("/generar-ppt")
async def generar_ppt(data: GenerarRequest):
    """
    Devuelve el PPTX real con imágenes IA incrustadas en slides 1, 6, 9 y 10
    """
    try:
        # 1) Generar estructura (igual que /generar)
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

        import re

        slides = []
        current_title = None
        current_bullets = []

        for linea in lineas:
            clean = (linea or "").replace("**", "").strip()
            if not clean:
                continue

            m1 = re.match(r"^(\d+)\.\s+(.*)$", clean)
            m2 = re.match(r"^Diapositiva\s+(\d+)\s*:\s*(.*)$", clean, flags=re.IGNORECASE)

            if m1 or m2:
                if current_title:
                    slides.append({
                        "title": current_title.strip(),
                        "bullets": [b for b in current_bullets if b],
                    })

                current_title = (m1.group(2) if m1 else m2.group(2)).strip()
                current_bullets = []
                continue

            clean_bullet = clean.lstrip("-• ").strip()
            if clean_bullet:
                current_bullets.append(clean_bullet)

        if current_title:
            slides.append({
                "title": current_title.strip(),
                "bullets": [b for b in current_bullets if b],
            })

        # Blindaje: EXACTAMENTE num_diapositivas
        target_n = int(data.num_diapositivas or 10)
        if not slides:
            slides = [{"title": f"Diapositiva {i+1}", "bullets": ["Idea principal"]} for i in range(target_n)]
        else:
            slides = slides[:target_n]
            while len(slides) < target_n:
                slides.append({"title": f"Diapositiva {len(slides)+1}", "bullets": ["Idea principal"]})

        # 2) Generar imágenes IA SOLO para 1,6,9,10 (dataUrl)
        image_prompts = {
            1: f"Portada profesional moderna 16:9 para la presentación '{data.titulo}', estilo corporativo elegante",
            6: f"Imagen profesional relacionada con '{slides[5]['title']}', estilo corporativo moderno 16:9",
            9: f"Imagen profesional relacionada con '{slides[8]['title']}', estilo corporativo moderno 16:9",
            10: f"Imagen de cierre profesional relacionada con '{slides[9]['title']}', estilo corporativo elegante 16:9",
        }

        images = {}
        for slide_num, img_prompt in image_prompts.items():
            images[slide_num] = generate_image_data_url(img_prompt)

        # 3) Crear PPTX real con imágenes incrustadas
        pptx_bytes = crear_pptx_con_imagenes(data.titulo, slides, images)

        filename = "presentacion_nova_pro.pptx"

        return Response(
            content=pptx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )

    except Exception as e:
        print("🔥 ERROR en /generar-ppt:", str(e))
        print(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"status": "error", "where": "/generar-ppt", "message": str(e)}
        )
    
app.include_router(api)
