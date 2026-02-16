# nova_portero/validaciones_portero.py

from typing import Any, Dict, Tuple


def _is_blank(s: Any) -> bool:
    return s is None or (isinstance(s, str) and not s.strip())


def validar_payload(payload: Any, cfg: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Valida de forma segura:
    - Si el body no es JSON dict => OK (no bloqueamos endpoints que no sean JSON)
    - Si hay campos conocidos, los validamos
    """
    if not isinstance(payload, dict):
        return True, "OK (no-dict payload)"

    limits = cfg.get("limits", {})
    known = cfg.get("known_fields", set())

    # Valida solo si el campo viene en el payload (no obligamos)
    if "titulo" in payload and "titulo" in known:
        titulo = payload.get("titulo")
        if _is_blank(titulo):
            return False, "El campo 'titulo' está vacío."
        if not (limits["titulo_min"] <= len(str(titulo).strip()) <= limits["titulo_max"]):
            return False, "El campo 'titulo' tiene longitud inválida."

    if "contenido" in payload and "contenido" in known:
        contenido = payload.get("contenido")
        if _is_blank(contenido):
            return False, "El campo 'contenido' está vacío."
        if not (limits["contenido_min"] <= len(str(contenido).strip()) <= limits["contenido_max"]):
            return False, "El campo 'contenido' tiene longitud inválida."

    if "num_diapositivas" in payload and "num_diapositivas" in known:
        n = payload.get("num_diapositivas")
        try:
            n_int = int(n)
        except Exception:
            return False, "El campo 'num_diapositivas' debe ser un número."
        if not (limits["num_diapositivas_min"] <= n_int <= limits["num_diapositivas_max"]):
            return False, "El campo 'num_diapositivas' está fuera de rango."

    return True, "OK"
