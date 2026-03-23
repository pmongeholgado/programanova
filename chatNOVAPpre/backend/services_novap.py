# backend/services_novap.py

from openai import OpenAI
from backend.nova_identity import NOVA_SYSTEM_PROMPT
from backend.memory_store import get_history, append_message
from backend.config_novap import OPENAI_API_KEY, DEFAULT_MODEL, DEFAULT_TEMPERATURE
    
# 🔹 crear cliente IA
client = OpenAI(api_key=OPENAI_API_KEY)


# 🔥 NORMALIZADOR MEJORADO (CLAVE REAL)
def fix_format(text: str) -> str:
    import re

    t = text.strip()

    # 🔥 Separar frases en párrafos reales
    t = re.sub(r'([a-z0-9])\.\s+(?=[A-ZÁÉÍÓÚÑ])', r'\1.\n\n', t)

    # 🔥 Convertir " - " en lista vertical
    t = re.sub(r'\s-\s', '\n- ', t)

    # 🔥 Separar listas numeradas
    t = re.sub(r'(\d+\.\s)', r'\n\1', t)

    # 🔥 Separar títulos si vienen pegados
    t = re.sub(r'(#{1,6}\s*)', r'\n\n\1', t)

    # 🔥 Limpiar saltos duplicados
    t = re.sub(r'\n{3,}', '\n\n', t)

    return t.strip()


def generate_reply(chat_id: str, message: str) -> str:
    """
    Genera respuesta de NOVA usando memoria persistente.
    """

    try:
        append_message(chat_id, "user", message)

        history = get_history(chat_id)

        messages = [
            {
                "role": "system",
                "content": NOVA_SYSTEM_PROMPT + """

FORMATO ESTRICTO OBLIGATORIO (MARKDOWN REAL):

- Cada título en su propia línea
- Cada subtítulo en su propia línea
- Cada punto de lista en una línea nueva
- Usa listas reales con guiones:

    - punto uno
    - punto dos
    - punto tres

- Separa párrafos con una línea en blanco

PROHIBIDO:
- usar " - " en la misma línea para separar ideas
- escribir texto continuo con símbolos
- juntar títulos y texto en la misma línea

RESPUESTA:
Devuelve SIEMPRE texto con saltos de línea reales y markdown válido.
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

        # 🔹 Aplicar normalización mejorada
        reply = fix_format(reply)

        append_message(chat_id, "assistant", reply)

        return reply

    except Exception as e:
        return f"Error IA: {str(e)}"


def generate_reply_stream(chat_id: str, message: str):
    """
    Genera respuesta de NOVA en streaming.
    """

    append_message(chat_id, "user", message)

    history = get_history(chat_id)

    messages = [
        {
            "role": "system",
            "content": NOVA_SYSTEM_PROMPT + """

FORMATO ESTRICTO OBLIGATORIO (MARKDOWN REAL):

- Cada título en su propia línea
- Cada subtítulo en su propia línea
- Cada punto de lista en una línea nueva
- Usa listas reales con guiones:

  - punto uno
  - punto dos
  - punto tres

- Separa párrafos con una línea en blanco

PROHIBIDO:
- usar " - " en la misma línea para separar ideas
- escribir texto continuo con símbolos
- juntar títulos y texto en la misma línea

RESPUESTA:
Devuelve SIEMPRE texto con saltos de línea reales y markdown válido.
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
            formatted = fix_format(reply_full)
            yield formatted

    # 🔹 NORMALIZACIÓN FINAL (CLAVE REAL)
    reply_full = fix_format(reply_full)
    
    append_message(chat_id, "assistant", reply_full)
