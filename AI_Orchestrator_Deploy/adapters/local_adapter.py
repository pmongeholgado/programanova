# adapters/local_adapter.py
from adapters.adapter_base import AIAdapter
from adapters.adapter_base import SimpleMemory

class LocalAdapter(AIAdapter):
    """Adaptador local que simula respuestas y guarda memoria de la conversación"""

    def __init__(self):
        # Inicializa una memoria temporal por sesión
        self.memory = SimpleMemory()

    def process(self, prompt):
        """Procesa la entrada del usuario simulando una IA local"""
        try:
            # Guarda el mensaje del usuario
            self.memory.add_message("usuario", prompt)

            # Genera una respuesta simulada con algo de contexto
            contexto = self.memory.get_contexto()
            respuesta = self.generar_respuesta(prompt, contexto)

            # Guarda la respuesta de la IA
            self.memory.add_message("IA", respuesta)
            return respuesta

        except Exception as e:
            return f"⚠️ Error al procesar el mensaje local: {e}"

    def generar_respuesta(self, prompt, contexto):
        """Genera una respuesta básica usando el contexto reciente"""
        if not contexto:
            return f"Hola 👋, parece que es nuestra primera charla. Dijiste: '{prompt}'."

        ultimo_usuario = next((m['contenido'] for m in reversed(contexto) if m['rol'] == 'usuario'), None)
        if ultimo_usuario:
            return f"Recuerdo que antes mencionaste: '{ultimo_usuario}'. Sobre lo que acabas de decir, '{prompt}', creo que suena interesante 🤔."
        else:
            return f"Entiendo. Sobre '{prompt}', me parece una buena idea 💡."


