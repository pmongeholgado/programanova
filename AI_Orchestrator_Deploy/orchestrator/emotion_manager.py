# emotion_manager.py
def analyze_emotion(texto: str) -> str:
    texto = texto.lower()

    emociones = {
        "feliz": ["feliz", "contento", "alegre", "genial"],
        "triste": ["triste", "deprimido", "mal", "pena"],
        "enfadado": ["enfadado", "molesto", "furioso", "cabreado"],
        "miedo": ["miedo", "asustado", "nervioso"],
        "neutral": []
    }

    for emocion, palabras in emociones.items():
        for p in palabras:
            if p in texto:
                return emocion

    return "neutral"
