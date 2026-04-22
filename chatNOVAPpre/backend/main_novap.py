# backend/main_novap.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.rutas_novap import router as novap_router
from backend.routes_auth import router as auth_router
from backend.rutas_chats import router as chats_router
from backend.rutas_usuarios import router as users_router
from backend.routes_messages import router as messages_router
from backend.rutas_stream import router as stream_router

from backend.db import engine, Base


# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="chatNOVAP",
    version="2.0",
)

# CORS correcto para local + Netlify + dominio final
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://gentle-puffpuff-4753cf.netlify.app",
        "https://chatnovap.online",
        "https://www.chatnovap.online",
    ],
    allow_origin_regex=r"https://.*\.netlify\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas del módulo NOVAP
app.include_router(novap_router, prefix="/novap")

# Rutas del sistema
app.include_router(auth_router, prefix="/auth")
app.include_router(chats_router, prefix="/chats")
app.include_router(messages_router, prefix="/messages")
app.include_router(users_router, prefix="/users")
app.include_router(stream_router, prefix="/stream")


# Ruta raíz de prueba
@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "chatNOVAP",
        "version": "v2",
        "mode": "railway",
    }


# Healthcheck simple
@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "chatNOVAP",
    }
