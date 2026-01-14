# backend/ia_assets.py
import os
import json
import base64
from typing import Any, Dict, List, Optional

# Fallback seguro: genera una imagen PNG simple si no hay IA disponible
def _fallback_png_base64(text: str = "NOVA PRO") -> str:
    try:
        from PIL import Image, ImageDraw, ImageFont  # pillow
        img = Image.new("RGB", (1024, 1024), color=(15, 23, 42))  # fondo oscuro
        draw = ImageDraw.Draw(img)
        msg = text[:60]
        draw.text((60, 80), "Imagen PRO (fallback)", fill=(203, 213, 225))
        draw.text((60, 140), msg, fill=(96, 165, 250))
        import io
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        return b64
    except Exception:
        # Si Pillow no está instalado, devolvemos vacío (el frontend pondrá fallback de texto)
        return ""

def _data_url_from_b64png(b64_png: str) -> str:
    if not b64_png:
        return ""
    return f"data:image/png;base64,{b64_png}"

def _fallback_chart_spec(title: str = "Datos", seed: int = 10) -> Dict[str, Any]:
    # Un gráfico simple y estable para que el PPT siempre tenga contenido
    labels = ["A", "B", "C", "D"]
    values = [seed, max(1, seed - 3), max(1, seed - 6), max(1, seed - 8)]
    return {"type": "bar", "labels": labels, "values": values, "title": title or "Datos"}

def _get_openai_client():
    """
    Usamos el SDK oficial openai-python.
    Si no está instalado o no hay API key, devolvemos None y se usará fallback.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        from openai import OpenAI
        return OpenAI(api_key=api_key)
    except Exception:
        return None

async def generate_image_data_url(
    prompt: str,
    *,
    model: str = "gpt-image-1",
    size: str = "1024x1024",
) -> str:
    """
    Devuelve un data URL PNG listo para PptxGenJS:
      "data:image/png;base64,...."
    """
    client = _get_openai_client()
    if client is None:
        b64 = _fallback_png_base64(prompt)
        return _data_url_from_b64png(b64)

    # Llamada a generación de imagen
    try:
        # API Images: client.images.generate(...)
        # La respuesta suele traer data[0].b64_json
        resp = client.images.generate(
            model=model,
            prompt=prompt,
            size=size,
        )
        b64_png = ""
        if hasattr(resp, "data") and resp.data and hasattr(resp.data[0], "b64_json"):
            b64_png = resp.data[0].b64_json or ""
        elif isinstance(resp, dict):
            b64_png = (resp.get("data") or [{}])[0].get("b64_json", "") or ""

        if not b64_png:
            # fallback si la API devuelve algo inesperado
            b64_png = _fallback_png_base64(prompt)

        return _data_url_from_b64png(b64_png)

    except Exception:
        b64 = _fallback_png_base64(prompt)
        return _data_url_from_b64png(b64)

async def generate_chart_spec(
    topic: str,
    *,
    model: str = "gpt-4.1-mini",
) -> Dict[str, Any]:
    """
    Devuelve un chartSpec compatible con tu exportador:
      { "type": "bar|line|pie", "labels": [...], "values": [...], "title": "..." }
    """
    client = _get_openai_client()
    if client is None:
        return _fallback_chart_spec(title=topic or "Datos", seed=10)

    schema = {
        "name": "chart_spec",
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "type": {"type": "string", "enum": ["bar", "line", "pie"]},
                "title": {"type": "string"},
                "labels": {"type": "array", "items": {"type": "string"}, "minItems": 3, "maxItems": 8},
                "values": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 8},
            },
            "required": ["type", "title", "labels", "values"],
        },
    }

    prompt = (
        "Genera un gráfico simple y coherente para una diapositiva de PowerPoint.\n"
        "Devuelve SOLO JSON válido con campos: type, title, labels, values.\n"
        f"Tema de la diapositiva: {topic}\n"
        "Reglas: labels y values deben tener la misma longitud."
    )

    try:
        # Respuestas API (recomendada). Si tu SDK no soporta response_format json_schema,
        # caerá al fallback sin romper.
        resp = client.responses.create(
            model=model,
            input=prompt,
            response_format={"type": "json_schema", "json_schema": schema},
        )

        # Extraer texto JSON
        txt = ""
        if hasattr(resp, "output_text"):
            txt = resp.output_text or ""
        elif isinstance(resp, dict):
            txt = resp.get("output_text", "") or ""

        data = json.loads(txt) if txt else None
        if not data:
            return _fallback_chart_spec(title=topic or "Datos", seed=12)

        # Normalización mínima
        labels = data.get("labels", [])
        values = data.get("values", [])
        if not labels or not values or len(labels) != len(values):
            return _fallback_chart_spec(title=data.get("title") or topic or "Datos", seed=12)

        return {
            "type": data.get("type", "bar"),
            "title": data.get("title") or (topic or "Datos"),
            "labels": labels,
            "values": values,
        }

    except Exception:
        return _fallback_chart_spec(title=topic or "Datos", seed=12)
