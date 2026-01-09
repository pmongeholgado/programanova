# summary_generator.py
# ======================================================
# 🔒 SUMMARY GENERATOR PRO
# Uso exclusivo para backend PRO
# ======================================================

IS_PRO_SUMMARY = True

print("✅ Summary Generator PRO cargado")

from adapters.openai_adapter_pro import OpenAIAdapter, assert_pro_context as assert_adapter_pro

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

def generate_summary_pro(texto: str) -> dict:
    """
    Genera un resumen usando IA real (modo PRO)
    """
    # Garantizamos contexto PRO del adapter
    assert_adapter_pro()

    adapter = OpenAIAdapter()
    resumen = adapter.generate_response(
        f"Resume el siguiente texto de forma clara y concisa:\n\n{texto}"
    )

    return {
        "mode": "PRO",
        "resumen": resumen
    }
