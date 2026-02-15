# nova_portero/config_portero.py

PORTERO_CONFIG = {
    # Rutas que NO deben ser interceptadas (docs, health, openapi...)
    "bypass_paths": {
        "/", "/health", "/docs", "/redoc", "/openapi.json"
    },

    # Límite de tamaño del body (evita peticiones gigantes)
    "max_body_bytes": 250_000,  # 250 KB

    "internal_access_header": "X-NOVA-ADMIN",
    "internal_access_key": "nova_pablo_full_access",
    
    # Límite de caracteres para campos típicos
    "limits": {
        "titulo_min": 3,
        "titulo_max": 120,
        "contenido_min": 20,
        "contenido_max": 20_000,
        "num_diapositivas_min": 1,
        "num_diapositivas_max": 30,
    },

    # Campos esperados (si existen en tu payload real, lo valida)
    # Si tu payload no trae alguno, NO falla; solo valida lo que venga.
    "known_fields": {"titulo", "contenido", "num_diapositivas"},
}

