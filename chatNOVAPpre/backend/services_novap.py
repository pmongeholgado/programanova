from openai import OpenAI
from backend.nova_identity import NOVA_SYSTEM_PROMPT
from backend.memory_store import get_history, append_message
from backend.config_novap import OPENAI_API_KEY, DEFAULT_MODEL, DEFAULT_TEMPERATURE, GENESIOS_URL
import requests

client = OpenAI(api_key=OPENAI_API_KEY)


def generate_reply_with_genesios(message: str) -> dict:
    try:
        response = requests.post(
            GENESIOS_URL,
            json={"mensaje": message},
            timeout=60
        )
        response.raise_for_status()
        data = response.json()

        reply = data.get("respuesta", "").strip()
        image_url = data.get("image_url")
        audio_url = data.get("audio_url")

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

    except Exception as e:
        return {
            "reply": "",
            "image_url": None,
            "audio_url": None,
            "error": f"Error IA: {str(e)}"
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

        # 3. Respaldo actual de chatNOVAP (no se pierde nada)
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
