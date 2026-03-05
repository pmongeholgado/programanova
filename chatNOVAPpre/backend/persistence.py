# backend/persistence.py

import json
from pathlib import Path
from typing import Dict, Any

BASE_DIR = Path(__file__).resolve().parent
FILE_PATH = BASE_DIR / "conversations.json"


def load_conversations() -> Dict[str, Any]:
    """
    Carga las conversaciones desde el archivo JSON.
    Si no existe o está corrupto, devuelve diccionario vacío.
    """
    if not FILE_PATH.exists():
        # Crear archivo vacío inicial
        FILE_PATH.write_text("{}", encoding="utf-8")
        return {}

    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
            return {}
    except json.JSONDecodeError:
        # Si el JSON está corrupto, lo reseteamos de forma segura
        FILE_PATH.write_text("{}", encoding="utf-8")
        return {}
    except Exception:
        return {}


def save_conversations(conversations: Dict[str, Any]) -> None:
    """
    Guarda las conversaciones de forma segura en el archivo JSON.
    """
    try:
        temp_path = FILE_PATH.with_suffix(".tmp")

        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(conversations, f, ensure_ascii=False, indent=2)

        temp_path.replace(FILE_PATH)

    except Exception as e:
        print(f"[ERROR] No se pudo guardar conversations.json: {e}")