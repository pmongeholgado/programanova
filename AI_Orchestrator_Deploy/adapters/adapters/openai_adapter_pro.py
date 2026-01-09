import os
from openai import OpenAI
from .adapter_base import AIAdapter

# ======================================================
# 🔒 OPENAI ADAPTER PRO
# Uso exclusivo para backend PRO
# ======================================================

IS_PRO_ADAPTER = True

print("✅ OpenAI Adapter PRO cargado")

def assert_pro_context():
    """
    Garantiza que este adapter solo se use en contexto PRO
    """
    if not IS_PRO_ADAPTER:
        raise RuntimeError("❌ OpenAI Adapter PRO usado fuera de contexto PRO")

class OpenAIAdapter(AIAdapter):
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("No se encontró la clave OPENAI_API_KEY en .env")
        self.client = OpenAI(api_key=api_key)

    def generate_response(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message["content"]










