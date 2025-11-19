# tone_manager.py

def analyze_tone(texto: str) -> str:
    """
    Analiza el texto y devuelve una respuesta preliminar basada en el tono.
    Esto sirve como respuesta rápida del Orquestador antes de usar modelos complejos.
    """

    texto = texto.lower()

    if "hola" in texto or "buenas" in texto:
        return "¡Hola! ¿En qué puedo ayudarte?"

    if "ayuda" in texto:
        return "Claro, estoy aquí para ayudarte. Cuéntame un poco más."

    if "problema" in texto:
        return "Entiendo. Vamos a ver cuál puede ser la mejor solución."

    if "gracias" in texto:
        return "¡De nada! Siempre contigo."

    # Respuesta genérica si no detecta tono concreto
    return "Entendido. ¿Quieres que profundicemos?"
