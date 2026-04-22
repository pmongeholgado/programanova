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


def normalize_reply_result(result):
    """
    Normaliza la respuesta del servicio para que siempre salga
    con una estructura coherente hacia el frontend.
    """
    if isinstance(result, dict):
        return ChatResponse(
            reply=result.get("reply", "") or "",
            error=result.get("error"),
            image_url=result.get("image_url"),
            audio_url=result.get("audio_url"),
            chart_url=result.get("chart_url")
        )

    return ChatResponse(
        reply=str(result) if result is not None else "",
        error=None,
        image_url=None,
        audio_url=None,
        chart_url=None
    )


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(data: ChatRequest):
    """
    Endpoint principal del chat.
    Recibe chat_id y message.
    Devuelve respuesta generada por NOVA.
    """
    try:
        chat_id = (data.chat_id or "").strip()
        message = (data.message or "").strip()

        if not chat_id or not message:
            raise HTTPException(
                status_code=400,
                detail="chat_id y message son obligatorios"
            )

        result = generate_reply(chat_id, message)

        return normalize_reply_result(result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno en chatNOVAP: {str(e)}"
        )
