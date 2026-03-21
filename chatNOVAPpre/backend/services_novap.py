# backend/services_novap.py

from openai import OpenAI
from backend.nova_identity import NOVA_SYSTEM_PROMPT
from backend.memory_store import get_history, append_message
from backend.config_novap import OPENAI_API_KEY, DEFAULT_MODEL, DEFAULT_TEMPERATURE

# 🔹 crear cliente IA
client = OpenAI(api_key=OPENAI_API_KEY)


def generate_reply(chat_id: str, message: str) -> str:
    """
    Genera respuesta de NOVA usando memoria persistente.
    """

    try:
        # 🔹 1. Guardar mensaje del usuario primero
        append_message(chat_id, "user", message)

        # 🔹 2. Obtener historial actualizado
        history = get_history(chat_id)

        # 🔹 3. Construir mensajes para OpenAI
        messages = [
    {
        "role": "system",
        "content": NOVA_SYSTEM_PROMPT + """

FORMATO OBLIGATORIO:

- Usa saltos de línea reales entre cada punto
- Cada elemento de lista debe ir en su propia línea
- Separa párrafos con líneas en blanco
- No escribas múltiples puntos en una sola línea
- Usa markdown limpio (listas, negritas, títulos)

IMPORTANTE:
Nunca devuelvas texto en bloque continuo.
Siempre estructura la respuesta en líneas separadas.
"""
    },
    *history
]

        # 🔹 4. Llamada a OpenAI
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=messages,
            temperature=DEFAULT_TEMPERATURE,
        )

        reply = response.choices[0].message.content.strip()

        # 🔹 5. Guardar respuesta IA
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

FORMATO OBLIGATORIO:

- Usa saltos de línea reales entre cada punto
- Cada elemento de lista debe ir en su propia línea
- Separa párrafos con líneas en blanco
- No escribas múltiples puntos en una sola línea
- Usa markdown limpio (listas, negritas, títulos)

IMPORTANTE:
Nunca devuelvas texto en bloque continuo.
Siempre estructura la respuesta en líneas separadas.
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
            yield token

    append_message(chat_id, "assistant", reply_full)
