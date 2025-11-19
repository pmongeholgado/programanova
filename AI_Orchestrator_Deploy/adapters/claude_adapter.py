from typing import List, Optional, Dict, Any
from .adapter_base import BaseAdapter


class ClaudeAdapter(BaseAdapter):
    """
    Adaptador de ejemplo para Claude (Claude Sonnet).
    De momento devuelve una respuesta simulada para que la app funcione
    aunque no tengamos aún la API real conectada.
    """

    def __init__(self) -> None:
        # Aquí podríamos cargar claves de API o configuración en el futuro
        pass

    async def process(
        self,
        prompt: str,
        history: Optional[List[Dict[str, str]]] = None,
        **kwargs: Any,
    ) -> str:
        """
        Método obligatorio que pide BaseAdapter.
        De momento es un stub (respuesta simulada) para no romper la app.
        """
        if history is None:
            history = []

        # Construimos un pequeño resumen del historial (solo para depuración)
        resumen_historial = ""
        if history:
            resumen_historial = "\n\nHistorial reciente:\n"
            for msg in history[-3:]:
                rol = msg.get("role", "user")
                contenido = msg.get("content", "")
                resumen_historial += f"- {rol}: {contenido[:80]}...\n"

        respuesta = (
            "⚠️ ClaudeAdapter aún no está conectado a una API real.\n"
            "Esta es una respuesta simulada para que el orquestador funcione correctamente.\n\n"
            f"Prompt recibido:\n{prompt}"
            f"{resumen_historial}"
        )

        return respuesta
