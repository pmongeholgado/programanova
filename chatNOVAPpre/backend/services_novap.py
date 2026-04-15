from openai import OpenAI
from backend.nova_identity import NOVA_SYSTEM_PROMPT
from backend.memory_store import get_history, append_message
from backend.config_novap import OPENAI_API_KEY, DEFAULT_MODEL, DEFAULT_TEMPERATURE, GENESIOS_URL
import requests

client = OpenAI(api_key=OPENAI_API_KEY)

# URL directa de respaldo de GENESIOS (no toca config, solo refuerza el puente)
GENESIOS_FALLBACK_URL = "http://82.223.115.253:8000/interactuar"


def is_special_genesios_request(message: str) -> bool:
    m = (message or "").lower()

    image_words = [
        "imagen", "imágenes", "image", "images",
        "dibuja", "dibujar", "crea una imagen", "genera una imagen",
        "render", "foto", "picture", "illustration"
    ]

    audio_words = [
        "voz", "audio", "habla", "leer", "léelo", "leelo",
        "pronuncia", "reproduce", "escuchar"
    ]

    return any(word in m for word in image_words + audio_words)


def wants_image(message: str) -> bool:
    m = (message or "").lower()
    image_words = [
        "imagen", "imágenes", "image", "images",
        "dibuja", "dibujar", "crea una imagen", "genera una imagen",
        "render", "foto", "picture", "illustration"
    ]
    return any(word in m for word in image_words)


def wants_audio(message: str) -> bool:
    m = (message or "").lower()
    audio_words = [
        "voz", "audio", "habla", "leer", "léelo", "leelo",
        "pronuncia", "reproduce", "escuchar"
    ]
    return any(word in m for word in audio_words)


def absolutize_url(base_url: str, maybe_relative: str | None) -> str | None:
    if not maybe_relative:
        return None

    if maybe_relative.startswith("http://") or maybe_relative.startswith("https://"):
        return maybe_relative

    if maybe_relative.startswith("/"):
        if "://" in base_url:
            origin = base_url.split("://", 1)
            scheme = origin[0]
            host = origin[1].split("/", 1)[0]
            return f"{scheme}://{host}{maybe_relative}"

    return maybe_relative


def call_genesios_once(endpoint_url: str, message: str) -> dict:
    response = requests.post(
        endpoint_url,
        json={"mensaje": message},
        headers={"Content-Type": "application/json"},
        timeout=(10, 90)
    )
    response.raise_for_status()
    data = response.json()

    reply = (data.get("respuesta") or "").strip()

    # GENESIOS puede devolver image_url o visual
    image_url = data.get("image_url") or data.get("visual")
    audio_url = data.get("audio_url")

    image_url = absolutize_url(endpoint_url, image_url)
    audio_url = absolutize_url(endpoint_url, audio_url)

    if reply or image_url or audio_url:
        return {
            "reply": reply or "Respuesta recibida desde GENESIOS.",
            "image_url": image_url,
            "audio_url": audio_url,
            "error": None
        }

    return {
        "reply": "No se pudo obtener una respuesta válida de GENESIOS.",
        "image_url": None,
        "audio_url": None,
        "error": "No se pudo obtener una respuesta válida de GENESIOS."
    }


def generate_reply_with_genesios(message: str) -> dict:
    endpoints = [GENESIOS_URL, GENESIOS_FALLBACK_URL]
    last_error = None

    for endpoint in endpoints:
        try:
            result = call_genesios_once(endpoint, message)

            # Si pide imagen, exigir image_url real
            if wants_image(message) and not result.get("image_url"):
                last_error = f"GENESIOS respondió sin image_url desde {endpoint}"
                continue

            # Si pide audio, exigir audio_url real
            if wants_audio(message) and not result.get("audio_url"):
                last_error = f"GENESIOS respondió sin audio_url desde {endpoint}"
                continue

            return result

        except Exception as e:
            last_error = f"{endpoint} -> {str(e)}"

    return {
        "reply": "",
        "image_url": None,
        "audio_url": None,
        "error": last_error or "Error al conectar con GENESIOS."
    }


# 🔥 NUEVA CAPA SUAVE (NO ROMPE NADA)
def enforce_structure_soft(text: str) -> str:
    import re

    t = text.strip()

    # 👉 listas en vertical si vienen mal
    t = re.sub(r'\s-\s', '\n- ', t)

    # 👉 asegurar salto antes de títulos
    t = re.sub(r'(#{1,6}\s)', r'\n\n\1', t)

    # 👉 limpiar saltos excesivos
    t = re.sub(r'\n{3,}', '\n\n', t)

    return t.strip()


def generate_reply(chat_id: str, message: str):
    try:
        append_message(chat_id, "user", message)

        # 1. Intentar primero con GENESIOS
        genesios_result = generate_reply_with_genesios(message)

        # 2. Si GENESIOS responde bien, usar esa respuesta completa
        if not genesios_result.get("error"):
            reply = enforce_structure_soft(genesios_result.get("reply", ""))

            result = {
                "reply": reply,
                "image_url": genesios_result.get("image_url"),
                "audio_url": genesios_result.get("audio_url"),
                "error": None
            }

            append_message(chat_id, "assistant", result["reply"])
            return result

        # 3. Si es una petición especial (imagen/voz), NO tapar el fallo con fallback
        if is_special_genesios_request(message):
            return {
                "reply": "No se pudo completar correctamente la petición especial en GENESIOS.",
                "image_url": None,
                "audio_url": None,
                "error": genesios_result.get("error") or "Error al conectar con GENESIOS."
            }

        # 4. Respaldo actual de chatNOVAP solo para texto normal
        history = get_history(chat_id)

        messages = [
            {
                "role": "system",
                "content": NOVA_SYSTEM_PROMPT + """

FORMATO OBLIGATORIO (ESTRICTO):

Responde SIEMPRE en Markdown real.

Ejemplo de estructura obligatoria:

### Título principal

Texto del párrafo.

### Sección

- Punto uno
- Punto dos
- Punto tres

Reglas obligatorias:
- Usa saltos de línea reales (\n)
- Usa listas con "-"
- Separa párrafos con línea en blanco
- NO escribas texto en una sola línea
"""
            },
            *history
        ]

        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=messages,
            temperature=DEFAULT_TEMPERATURE,
        )

        reply = response.choices[0].message.content.strip()
        reply = enforce_structure_soft(reply)

        append_message(chat_id, "assistant", reply)

        return {
            "reply": reply,
            "image_url": None,
            "audio_url": None,
            "error": None
        }

    except Exception as e:
        return {
            "reply": "",
            "image_url": None,
            "audio_url": None,
            "error": f"Error IA: {str(e)}"
        }


def generate_reply_stream(chat_id: str, message: str):
    append_message(chat_id, "user", message)

    history = get_history(chat_id)

    messages = [
        {
            "role": "system",
            "content": NOVA_SYSTEM_PROMPT + """

FORMATO OBLIGATORIO (ESTRICTO):

Responde SIEMPRE en Markdown real.

Ejemplo:

### Título

Texto.

- Punto uno
- Punto dos

Reglas:
- Saltos de línea reales
- Nada en una sola línea
"""
        },
        *history
    ]

    stream = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=messages,
        temperature=DEFAULT_TEMPERATURE,
        stream=True
    )

    reply_full = ""

    for chunk in stream:
        if chunk.choices[0].delta.content:
            token = chunk.choices[0].delta.content
            reply_full += token
            yield token  # 🔥 streaming limpio

    # 🔥 SOLO AQUÍ AL FINAL (NO TOCA STREAMING)
    reply_full = enforce_structure_soft(reply_full)

    append_message(chat_id, "assistant", reply_full)
