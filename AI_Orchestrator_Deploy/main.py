from orchestrator.intent_router import route_intent
from orchestrator.emotion_manager import analyze_emotion
from orchestrator.tone_manager import analyze_tone
from orchestrator.summary_generator import generate_summary

def procesar_mensaje(texto: str):
    """
    Función principal que procesa un mensaje
    usando los módulos del Orquestador.
    Devuelve: emoción, intención, respuesta, resumen
    """

    # 1. Detectar intención
    intencion = route_intent(texto)

    # 2. Detectar emoción
    emocion = analyze_emotion(texto)

    # 3. Analizar el tono (respuesta preliminar)
    respuesta = analyze_tone(texto)

    # 4. Generar resumen del contenido
    resumen = generate_summary(texto)

    return emocion, intencion, respuesta, resumen
