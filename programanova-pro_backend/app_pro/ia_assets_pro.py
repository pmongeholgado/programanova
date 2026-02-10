# app/ia_assets.py
import os
import json
import base64
from typing import Any, Dict, Union

# ============================
# FALLBACKS (seguros)
# ============================

def _fallback_png_base64(text: str = "NOVA PRO") -> str:
    try:
        from PIL import Image, ImageDraw  # pillow
        img = Image.new("RGB", (1024, 1024), color=(255, 255, 255))  # fondo blanco
        draw = ImageDraw.Draw(img)
        msg = (text or "NOVA PRO")[:60]
        draw.text((60, 80), "Imagen PRO (fallback)", fill=(203, 213, 225))
        draw.text((60, 140), msg, fill=(96, 165, 250))
        import io
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        return b64
    except Exception as e:
        import traceback
        b64 = _fallback_png_base64(prompt)
        print("❌ IMAGEN EXCEPTION (OpenAI):", repr(e))
        traceback.print_exc()
        print("❌ EXCEPTION -> usando fallback len =", len(b64))
        return _data_url_from_b64png(b64)

        # Si Pillow no está instalado, devolvemos un PNG mínimo (1x1) para que NUNCA sea vacío
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMB/6X8Z6QAAAAASUVORK5CYII="

def _data_url_from_b64png(b64_png: str) -> str:
    if not b64_png:
        return ""
    return f"data:image/png;base64,{b64_png}"

def _fallback_chart_spec(title: str = "Datos", seed: int = 10) -> Dict[str, Any]:
    labels = ["A", "B", "C", "D"]
    values = [seed, max(1, seed - 3), max(1, seed - 6), max(1, seed - 8)]
    return {"type": "bar", "labels": labels, "values": values, "title": title or "Datos"}

def _get_openai_client():
    api_key = os.environ.get("OPENAI_API_KEY") or "").strip()
    if not api_key:
        return None
    try:
        from openai import OpenAI
        return OpenAI(api_key=api_key)
    except Exception:
        return None

# ============================
# API: IMAGEN (SYNC)
# ============================

def generate_image_data_url(
    prompt: str,
    *,
    model: str = "gpt-image-1",
    size: str = "1024x1024",
) -> str:
    client = _get_openai_client()
    if client is None:
        b64 = _fallback_png_base64(prompt)
        return _data_url_from_b64png(b64)
        
    try:
        resp = client.images.generate(
            model=model,
            prompt=prompt,
            size=size,
            response_format="b64_json"
        )

        b64_png = ""
        img_url = ""
        used_fallback = False

        # Caso SDK objeto
        if hasattr(resp, "data") and resp.data:
            d0 = resp.data[0]
            # b64 directo
            if hasattr(d0, "b64_json") and d0.b64_json:
                b64_png = d0.b64_json
            # o URL
            elif hasattr(d0, "url") and d0.url:
                img_url = d0.url

        # Caso dict
        elif isinstance(resp, dict):
            d0 = (resp.get("data") or [{}])[0] or {}
            b64_png = d0.get("b64_json", "") or ""
            img_url = d0.get("url", "") or ""

        # ✅ Si vino URL, la descargamos y la convertimos a base64
        if (not b64_png) and img_url:
            try:
                import requests
                r = requests.get(img_url, timeout=25)
                if r.ok and r.content:
                    b64_png = base64.b64encode(r.content).decode("utf-8")
            except Exception:
                pass
        
        # ✅ Fallback si no se pudo
        if not b64_png:
            used_fallback = True
            b64_png = _fallback_png_base64(prompt)

        if used_fallback:
            print("⚠️ FALLBACK ACTIVADO -> usando PNG fallback len =", len(b64_png))
        else:
            print("✅ IMAGEN REAL OK -> b64 recibido len =", len(b64_png))
                                                               
        return _data_url_from_b64png(b64_png)
                                                                
    except Exception:
        b64 = _fallback_png_base64(prompt)
        print("❌ EXCEPTION -> usando fallback len =", len(b64))
        return _data_url_from_b64png(b64)

# ============================
# API: GRÁFICO (SYNC)
# ============================

def generate_chart_spec(
    topic: Union[str, Dict[str, Any]],
    *,
    model: str = "gpt-4o-mini",
) -> Dict[str, Any]:
    """
    Acepta:
    - topic: "texto"
    - topic: {"title": "...", "contexto": "..."}
    Devuelve:
      { "type": "bar|line|pie", "labels": [...], "values": [...], "title": "..." }
    """
    # Convertimos a string usable
    if isinstance(topic, dict):
        title = str(topic.get("title") or "Datos")
        contexto = str(topic.get("contexto") or "")
        tema = f"{title}. {contexto}".strip()
    else:
        tema = str(topic or "Datos")
        title = tema

    client = _get_openai_client()
    if client is None:
        return _fallback_chart_spec(title=title or "Datos", seed=10)

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
        f"Tema de la diapositiva: {tema}\n"
        "Reglas: labels y values deben tener la misma longitud."
    )

    try:
        resp = client.responses.create(
            model=model,
            input=prompt,
            response_format={"type": "json_schema", "json_schema": schema},
        )

        txt = ""
        if hasattr(resp, "output_text"):
            txt = resp.output_text or ""
        elif isinstance(resp, dict):
            txt = resp.get("output_text", "") or ""

        data = json.loads(txt) if txt else None
        if not data:
            return _fallback_chart_spec(title=title or "Datos", seed=12)

        labels = data.get("labels", [])
        values = data.get("values", [])
        if not labels or not values or len(labels) != len(values):
            return _fallback_chart_spec(title=data.get("title") or title or "Datos", seed=12)

        return {
            "type": data.get("type", "bar"),
            "title": data.get("title") or (title or "Datos"),
            "labels": labels,
            "values": values,
        }

    except Exception:
        return _fallback_chart_spec(title=title or "Datos", seed=12)

import os
import base64
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generar_imagenes_ppt(texto_completo: str, output_dir: str = "generated_images"):
    """
    Genera EXACTAMENTE 4 imágenes basadas en el texto del PPT.
    Devuelve una lista con las rutas de las 4 imágenes.
    """

    os.makedirs(output_dir, exist_ok=True)

    prompts = [
        f"Imagen profesional de portada para una presentación sobre: {texto_completo}. "
        f"Estilo tecnológico, moderno, limpio, tonos azules y grises, sin texto.",

        f"Ilustración clara y profesional que represente procesos o funcionamiento relacionado con: {texto_completo}. "
        f"Estilo corporativo, diagramático, limpio, sin texto.",

        f"Imagen visual que represente beneficios, impacto y valor del tema: {texto_completo}. "
        f"Estilo empresarial, moderno, inspirador, sin texto.",

        f"Imagen futurista y tecnológica que represente visión y futuro del tema: {texto_completo}. "
        f"Estilo innovador, elegante, profesional, sin texto."
    ]

    image_paths = []

    for idx, prompt in enumerate(prompts, start=1):
        result = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024"
        )

        image_base64 = result.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)

        image_path = os.path.join(output_dir, f"imagen_{idx}.png")
        with open(image_path, "wb") as f:
            f.write(image_bytes)

        image_paths.append(image_path)

    return image_paths

