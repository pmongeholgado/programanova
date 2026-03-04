# backend/config_novap.py

import os
from dotenv import load_dotenv
from pathlib import Path

# 🔹 Cargar .env desde backend
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# 🔹 Variables globales del proyecto
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 🔹 Configuración modelo IA
DEFAULT_MODEL = "gpt-4.1-mini"
DEFAULT_TEMPERATURE = 0.7