# backend/memory_store.py

from backend.persistence import load_conversations, save_conversations

# 🔹 Cargar memoria al iniciar
conversations = load_conversations()


def _normalize_role(role: str) -> str:
    role = (role or "").strip().lower()

    if role in {"user", "assistant", "system"}:
        return role

    if role == "bot":
        return "assistant"

    return "user"


def _sanitize_message(message):
    if not isinstance(message, dict):
        return None

    role = _normalize_role(message.get("role", "user"))
    content = message.get("content", "")

    if content is None:
        content = ""

    content = str(content).strip()

    if not content:
        return None

    return {
        "role": role,
        "content": content
    }


def _sanitize_history(history):
    if not isinstance(history, list):
        return []

    clean_history = []

    for message in history:
        sanitized = _sanitize_message(message)
        if sanitized:
            clean_history.append(sanitized)

    return clean_history


def get_history(chat_id: str):
    """
    Devuelve el historial del chat.
    Si no existe, lo crea vacío.
    Si existe, lo sanea antes de devolverlo.
    """
    chat_id = str(chat_id).strip()

    if not chat_id:
        return []

    if chat_id not in conversations:
        conversations[chat_id] = []
        save_conversations(conversations)
        return conversations[chat_id]

    clean_history = _sanitize_history(conversations.get(chat_id, []))

    if clean_history != conversations.get(chat_id, []):
        conversations[chat_id] = clean_history
        save_conversations(conversations)

    return conversations[chat_id]


def append_message(chat_id: str, role: str, content: str):
    """
    Añade un mensaje al historial y guarda persistencia.
    """
    chat_id = str(chat_id).strip()
    if not chat_id:
        return

    message = _sanitize_message({
        "role": role,
        "content": content
    })

    if not message:
        return

    history = get_history(chat_id)
    history.append(message)

    save_conversations(conversations)
