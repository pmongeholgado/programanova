# adapters/auto_adapter.py
from adapters.adapter_base import AIAdapter
import os

class AutoAdapter(AIAdapter):
    """Adaptador automático que elige cómo responder localmente."""

    def __init__(self):
        self.memory = []  # Memoria interna simple para contexto

    def send_message(self, prompt):
        """Procesa el mensaje simulando una respuesta básica."""
        try:
            # Ejemplo de respuesta automatizada
            if "hola" in prompt.lower():
                respuesta = "¡Hola! Soy tu asistente local. ¿Cómo estás?"
            elif "inteligencia artificial" in prompt.lower():
                respuesta = "La inteligencia artificial permite a las máquinas aprender de los datos y tomar decisiones."
            elif "adiós" in prompt.lower() or "salir" in prompt.lower():
                respuesta = "Hasta pronto 👋"
            else:
                respuesta = "Interesante... puedo aprender más si sigues conversando conmigo."

            # Guarda el intercambio en memoria
            self.memory.append({"usuario": prompt, "ia": respuesta})
            return respuesta

        except Exception as e:
            return f"Error al procesar la solicitud contextual: {e}"

    def process(self, prompt):
        """Cumple con el método abstracto requerido por AIAdapter"""
        return self.send_message(prompt)

