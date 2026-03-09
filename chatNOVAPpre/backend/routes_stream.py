from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from backend.services_novap import generate_reply_stream

router = APIRouter()


@router.get("/reply")
def stream_reply(chat_id: str, message: str):

    return StreamingResponse(
        generate_reply_stream(chat_id, message),
        media_type="text/plain"

    )
