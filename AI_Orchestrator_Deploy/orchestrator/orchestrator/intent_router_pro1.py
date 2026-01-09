# Pipeline PRO FINAL confirmado y sellado

# -*- coding: utf-8 -*-

"""
Detector sencillo de intención para el Orquestador IA.
Devuelve una intención en texto según patrones básicos.
"""

# ======================================================
# 🔒 ROUTER PRO FINAL
# Conectado a Summary Generator PRO
# ======================================================

IS_PRO_ROUTER_FINAL = True

print("✅ Intent Router PRO FINAL cargado")

from orchestrator.summary_generator_pro import generate_summary_pro

def route_intent(texto: str) -> str:
    texto_l = texto.lower()

    # Intenciones relacionadas con sentimientos o estado personal
    if any(p in texto_l for p in ["triste", "mal", "deprimido", "solo"]):
        return "estado_emocional_negativo"

    if any(p in texto_l for p in ["feliz", "contento", "alegre", "motivado"]):
        return "estado_emocional_positivo"

    # Intenciones relacionadas con preguntas
    if texto_l.startswith("¿") or texto_l.endswith("?") or "que es" in texto_l:
        return "pregunta"

    # Intenciones relacionadas con acciones
    if any(p in texto_l for p in ["ayuda", "explica", "enséñame", "muestrame"]):
        return "solicitud_ayuda"

    if any(p in texto_l for p in ["crea", "genera", "haz", "escribe"]):
        return "solicitud_creativa"

    # Conversación general
    if any(p in texto_l for p in ["hola", "buenas", "hey"]):
        return "saludo"

    # Fallback
    return "desconocida"

def route_intent_pro(texto: str) -> dict:
    """
    Orquesta intención + generación de respuesta IA (modo PRO)
    """
    intent = route_intent(texto)
    summary = generate_summary_pro(texto)

    return {
        "mode": "PRO",
        "intent": intent,
        "resultado": summary
    }
