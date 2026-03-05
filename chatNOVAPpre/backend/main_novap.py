# backend/main_novap.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes_novap import router as novap_router

app = FastAPI(
    title="chatNOVAP",
    version="1.0",
)

# 🔹 CORS correcto para desarrollo local
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 Rutas del módulo NOVAP
app.include_router(novap_router, prefix="/novap")

# 🔹 Ruta raíz de prueba
@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "chatNOVAP",
        "mode": "local"
    }