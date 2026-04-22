from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from backend.schemas_novap import ChatResponse
from backend.services_novap import generate_reply_stream, generate_reply

router = APIRouter()


@router.get("/reply")
def stream_reply(chat_id: str, message: str):
    """
    Mantiene el streaming actual de texto plano.
    NO se toca para no romper lo que ya funciona en chatNOVAP.
    """
    clean_chat_id = (chat_id or "").strip()
    clean_message = (message or "").strip()

    if not clean_chat_id or not clean_message:
        raise HTTPException(
            status_code=400,
            detail="chat_id y message son obligatorios"
        )

    return StreamingResponse(
        generate_reply_stream(clean_chat_id, clean_message),
        media_type="text/plain"
    )


def normalize_reply_result(result):
    """
    Normaliza la respuesta enriquecida para mantener una salida
    estable y compatible con el frontend actual.
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


@router.post("/rich-reply", response_model=ChatResponse)
def rich_reply(chat_id: str, message: str):
    """
    Ruta enriquecida para soporte completo:
    - reply
    - image_url
    - audio_url
    - chart_url

    Se añade sin romper el streaming actual.
    """
    try:
        clean_chat_id = (chat_id or "").strip()
        clean_message = (message or "").strip()

        if not clean_chat_id or not clean_message:
            raise HTTPException(
                status_code=400,
                detail="chat_id y message son obligatorios"
            )

        result = generate_reply(clean_chat_id, clean_message)
        return normalize_reply_result(result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno en stream chatNOVAP: {str(e)}"
        )
