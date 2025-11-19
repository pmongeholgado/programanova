# summary_generator.py

def generate_summary(texto: str) -> dict:
    """
    Genera un resumen básico del mensaje.
    Si quieres, más adelante lo reemplazamos por un resumen real con IA.
    """

    texto = texto.strip()

    # Si el texto es muy corto, devolvemos un "resumen" directo
    if len(texto) < 40:
        return {
            "resumen": texto
        }

    # Resumen básico tomando las primeras frases
    resumen_corto = texto[:200].rsplit(" ", 1)[0]

    return {
        "resumen": resumen_corto + "..."
    }
