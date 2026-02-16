# nova_portero/middleware_portero.py

import json
from typing import Any, Dict, Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from .validaciones_portero import validar_payload


class PorteroMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, config: Optional[Dict[str, Any]] = None):
        super().__init__(app)
        self.cfg = config or {}
        self.bypass = set(self.cfg.get("bypass_paths", set()))
        self.max_body = int(self.cfg.get("max_body_bytes", 250_000))

    async def dispatch(self, request: Request, call_next) -> Response:
        # 1) Bypass rutas seguras
        path = request.url.path
        internal_header = self.cfg.get("internal_access_header")
        internal_key = self.cfg.get("internal_access_key")

        if internal_header and internal_key:
            if request.headers.get(internal_header) == internal_key:
                return await call_next(request)
                
        # --- NUEVO: control de acceso público ---
        public_header = self.cfg.get("public_access_header")
        public_key = self.cfg.get("public_access_key")
        protected_prefix = self.cfg.get("protected_paths_prefix", [])

        # si la ruta empieza por alguno de los prefijos protegidos
        if any(path.startswith(p) for p in protected_prefix):
            if public_header and public_key:
                if request.headers.get(public_header) != public_key:
                    return JSONResponse(
                        status_code=401,
                        content={
                            "ok": False,
                            "error": "Acceso no autorizado. Falta clave pública.",
                            "portero": "bloqueado"
                        },
                    )
        
        if path in self.bypass:
            return await call_next(request)

        # 2) Solo revisamos métodos con body potencial
        if request.method.upper() not in {"POST", "PUT", "PATCH"}:
            return await call_next(request)

        # 3) Control de tamaño del body (anti-abuso)
        body = await request.body()
        if len(body) > self.max_body:
            return JSONResponse(
                status_code=413,
                content={"ok": False, "error": "Body demasiado grande. Petición rechazada por PORTERO."},
            )

        # 4) Intento de parseo JSON (si no es JSON, no bloqueamos)
        payload = None
        if body:
            try:
                payload = json.loads(body.decode("utf-8"))
            except Exception:
                payload = None

        # 5) Validación suave (valida campos si vienen)
        ok, msg = validar_payload(payload, self.cfg)
        if not ok:
            return JSONResponse(
                status_code=422,
                content={"ok": False, "error": msg, "portero": "bloqueado"},
            )

        # 6) Reinyectar el body para que FastAPI lo pueda leer después
        async def receive():
            return {"type": "http.request", "body": body, "more_body": False}

        request._receive = receive  # starlette internal but common pattern

        return await call_next(request)
