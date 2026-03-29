import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from brain.engine import GenerativeBrain
from memory.vector_db import VectorMemory

class BotDuplicativo:
    def __init__(self, bot_id: str, model_path: str):
        self.bot_id = bot_id
        # Conectamos las piezas maestras
        self.brain = GenerativeBrain(model_path)
        self.memory = VectorMemory()
        print(f"Bot Duplicativo '{self.bot_id}' ensamblado y listo para interactuar.")

    def interact(self, user_input: str) -> str:
        # 1. Recuperar contexto de la memoria (RAG)
        past_context = self.memory.recall_pattern(self.bot_id, user_input)
        
        # 2. Generar respuesta autónoma con IA propia
        response = self.brain.generate_response(past_context, user_input)
        
        # 3. Guardar la nueva interacción para mimetizar en el futuro
        self.memory.store_interaction(self.bot_id, user_input, response)
        
        return response

if __name__ == "__main__":
    print("Módulo de agente (duplicativo_beta.py) guardado con éxito.")