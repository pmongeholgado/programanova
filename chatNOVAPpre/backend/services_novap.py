from openai import OpenAI
from backend.nova_identity import NOVA_SYSTEM_PROMPT
from backend.memory_store import get_history, append_message
from backend.config_novap import OPENAI_API_KEY, DEFAULT_MODEL, DEFAULT_TEMPERATURE

client = OpenAI(api_key=OPENAI_API_KEY)

# 🔥 HEMOS ELIMINADO LA FUNCIÓN fix_format POR COMPLETO.
# Ya no machacamos el texto, dejamos que OpenAI envíe el Markdown puro.

def generate_reply(chat_id: str, message: str) -> str:

    try:
        append_message(chat_id, "user", message)

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

        # 🔥 El texto va puro. Ya no hay fix_format.
        append_message(chat_id, "assistant", reply)

        return reply

    except Exception as e:
        return f"Error IA: {str(e)}"


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

    # 🔥 El texto se guarda en la memoria puro. Ya no hay fix_format.
    append_message(chat_id, "assistant", reply_full)
