# nova_portero/economia_portero.py
import os
import json
import time
import hmac
import base64
import hashlib
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

# =========================
#   MODELO ECONÓMICO V1
#   (Listo como si cobrara,
#    pero activable por switch)
# =========================

@dataclass(frozen=True)
class Plan:
    name: str
    price_eur: float
    chat_uses: int
    can_generate: bool
    can_download: bool
    languages: Tuple[str, ...]  # ("es","en","ja")

PLANS: Dict[str, Plan] = {
    "VISITOR": Plan("VISITOR", 0.00, 0, False, False, ("es",)),
    "A":       Plan("A",       0.50, 5, False, False, ("es","en","ja")),
    "B":       Plan("B",       0.90, 0, True,  False, ("es","en","ja")),
    "BPLUS":   Plan("BPLUS",   1.25, 0, True,  True,  ("es","en","ja")),
}
ACTIONS_PRICING = {
    "VIEW_ONLY": 0.00,          # solo ver
    "UNLOCK_LANGS_AND_CHAT": 0.50,  # opción A
    "GENERATE_NO_DOWNLOAD": 0.90,   # opción B
    "DOWNLOAD_PPT": 1.25,           # upgrade/acción
}

# Header económico (token del usuario)
ECON_HEADER = os.getenv("NOVA_ECON_TOKEN_HEADER", "X-NOVA-TIER-TOKEN")
# Secreto para firmar tokens (IMPORTANTE en Railway)
TOKEN_SECRET = os.getenv("NOVA_TOKEN_SECRET", "")

# Switch económico: OFF por defecto (no cambia nada)
ECON_MODE = os.getenv("NOVA_ECONOMY_MODE", "off").lower()  # off|on

# Store simple (v1): usos de chat por token (cuando ECON_MODE=on)
# En producción real se reemplaza por Redis/DB sin cambiar lógica.
_USAGE: Dict[str, int] = {}

def _b64e(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode("utf-8").rstrip("=")

def _b64d(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode((s + pad).encode("utf-8"))

def sign_token(payload: dict) -> str:
    """
    Crea token firmado. Se usa cuando haya pagos reales.
    Hoy lo dejamos listo.
    """
    if not TOKEN_SECRET:
        raise RuntimeError("NOVA_TOKEN_SECRET no está definido")
    raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    sig = hmac.new(TOKEN_SECRET.encode("utf-8"), raw, hashlib.sha256).digest()
    return f"{_b64e(raw)}.{_b64e(sig)}"

def verify_token(token: str) -> Optional[dict]:
    """
    Verifica token firmado y devuelve payload si es válido.
    """
    if not token or "." not in token:
        return None
    if not TOKEN_SECRET:
        return None
    part_raw, part_sig = token.split(".", 1)
    raw = _b64d(part_raw)
    sig = _b64d(part_sig)
    expected = hmac.new(TOKEN_SECRET.encode("utf-8"), raw, hashlib.sha256).digest()
    if not hmac.compare_digest(sig, expected):
        return None
    try:
        payload = json.loads(raw.decode("utf-8"))
    except Exception:
        return None
    # expiración opcional
    exp = payload.get("exp")
    if exp and time.time() > float(exp):
        return None
    return payload

def get_plan_from_request_headers(headers: dict) -> Tuple[Plan, Optional[str]]:
    """
    Devuelve (plan, token). Si ECON_MODE=off => VISITOR sin bloquear nada.
    """
    if ECON_MODE != "on":
        return PLANS["VISITOR"], None

    token = headers.get(ECON_HEADER)
    payload = verify_token(token) if token else None
    if not payload:
        return PLANS["VISITOR"], None

    tier = (payload.get("tier") or "VISITOR").upper()
    plan = PLANS.get(tier, PLANS["VISITOR"])
    return plan, token

def enforce_economy(plan: Plan, token: Optional[str], path: str) -> Tuple[bool, dict]:
    """
    Decide si se permite o no según plan y ruta.
    NO bloquea nada si ECON_MODE=off (porque get_plan ya devuelve VISITOR y token None).
    """
    # VISITOR no puede ejecutar /chat ni /generar cuando esté activado
    if plan.name == "VISITOR":
        if path.startswith("/chat") or path.startswith("/generar") or path.startswith("/api/chat") or path.startswith("/api/generar"):
            return False, {
                "ok": False,
                "error": "Acceso VISITOR: solo ver. Necesitas activar un plan.",
                "economia": {
                  "plan": plan.name,
                  "accion_requerida": "UNLOCK_LANGS_AND_CHAT",
                  "precio_eur": ACTIONS_PRICING["UNLOCK_LANGS_AND_CHAT"],
                },
            }
        return True, {"ok": True}

    # Plan A: solo chat limitado
    if plan.name == "A":
        if path.startswith("/generar") or path.startswith("/api/generar"):
            return False, {
                "ok": False,
                "error": "Plan A: no incluye generación. Sube a Plan B/B+.",
                "economia": {
                  "plan": plan.name,
                  "accion_requerida": "GENERATE_NO_DOWNLOAD",
                  "precio_eur": ACTIONS_PRICING["GENERATE_NO_DOWNLOAD"],
                },
            }
        if path.startswith("/chat") or path.startswith("/api/chat"):
            # Contador v1 por token
            if not token:
                return False, {
                    "ok": False,
                    "error": "Falta token de Plan A. Necesitas activar acceso.",
                    "economia": {
                      "plan": plan.name,
                      "accion_requerida": "UNLOCK_LANGS_AND_CHAT",
                      "precio_eur": ACTIONS_PRICING["UNLOCK_LANGS_AND_CHAT"],
                    },
                }

            remaining = _USAGE.get(token)
            if remaining is None:
                _USAGE[token] = plan.chat_uses - 1
                remaining = plan.chat_uses - 1
            else:
                if remaining <= 0:
                    return False, {
                        "ok": False,
                        "error": "Plan A: sin usos de chat disponibles.",
                        "economia": {"plan": plan.name, "usos_restantes": 0},
                    }
                _USAGE[token] = remaining - 1
                remaining = remaining - 1
            return True, {"ok": True, "economia": {"plan": plan.name, "usos_restantes": remaining}}
        return True, {"ok": True}

    # Plan B: generar permitido, descarga NO (se aplicará en endpoint/flujo de descarga)
    if plan.name == "B":
        if path.startswith("/generar") or path.startswith("/api/generar"):
            return True, {"ok": True, "economia": {"plan": plan.name, "descarga": False}}
        if path.startswith("/chat") or path.startswith("/api/chat"):
            return True, {"ok": True, "economia": {"plan": plan.name}}
        return True, {"ok": True}

    # Plan BPLUS: todo permitido
    if plan.name == "BPLUS":
        return True, {"ok": True, "economia": {"plan": plan.name, "descarga": True}}

    return True, {"ok": True}
