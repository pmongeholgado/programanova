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
