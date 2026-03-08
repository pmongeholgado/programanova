# backend/memory_store.py

from backend.persistence import load_conversations, save_conversations

# 🔹 Cargar memoria al iniciar
conversations = load_conversations()

def get_history(chat_id: str):
    """
    Devuelve el historial del chat.
    Si no existe, lo crea vacío.
    """
    if chat_id not in conversations:
        conversations[chat_id] = []
        save_conversations(conversations)
    return conversations[chat_id]

def append_message(chat_id: str, role: str, content: str):
    """
    Añade un mensaje al historial y guarda persistencia.
    """
    history = get_history(chat_id)
    history.append({
        "role": role,
        "content": content
    })
    save_conversations(conversations)