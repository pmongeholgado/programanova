# backend/routes_novap.py

from fastapi import APIRouter, HTTPException
from backend.schemas_novap import ChatRequest, ChatResponse
from backend.services_novap import generate_reply

router = APIRouter()


@router.get("/health")
def health():
    return {
        "ok": True,
        "module": "novap",
        "status": "running"
    }


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(data: ChatRequest):
    """
    Endpoint principal del chat.
    Recibe chat_id y mensaje.
    Devuelve respuesta generada por NOVA.
    """
    try:
        if not data.chat_id or not data.message:
            raise HTTPException(
                status_code=400,
                detail="chat_id y message son obligatorios"
            )

        result = generate_reply(data.chat_id, data.message)

        if isinstance(result, dict):
            return ChatResponse(
                reply=result.get("reply", ""),
                error=result.get("error"),
                image_url=result.get("image_url"),
                audio_url=result.get("audio_url")
            )

        return ChatResponse(reply=result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno en chatNOVAP: {str(e)}"
        )
