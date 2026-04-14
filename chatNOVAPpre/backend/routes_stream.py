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
    return StreamingResponse(
        generate_reply_stream(chat_id, message),
        media_type="text/plain"
    )


@router.post("/rich-reply", response_model=ChatResponse)
def rich_reply(chat_id: str, message: str):
    """
    Nueva ruta enriquecida para soporte completo:
    - reply
    - image_url
    - audio_url

    Se añade sin romper el streaming actual.
    """
    try:
        result = generate_reply(chat_id, message)

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
            detail=f"Error interno en stream chatNOVAP: {str(e)}"
        )
