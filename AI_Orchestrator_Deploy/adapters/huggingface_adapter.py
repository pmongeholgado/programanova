


# adapters/huggingface_adapter.py
from adapters.adapter_base import AIAdapter
from huggingface_hub import InferenceClient

class HuggingFaceAdapter(AIAdapter):
    """Adaptador para usar modelos abiertos y gratuitos de Hugging Face"""

    def __init__(self):
        # Sin necesidad de token
        self.client = InferenceClient(model="google/gemma-2b-it")


    def process(self, prompt: str) -> str:
        """Procesa un mensaje con un modelo gratuito de Hugging Face"""
        try:
            response = self.client.text_generation(
                prompt,
                max_new_tokens=200,
                temperature=0.7
            )
            return response
        except Exception as e:
            return f"⚠️ Error al procesar la solicitud con Hugging Face: {e}"
