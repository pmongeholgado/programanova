# backend/schemas_novap.py

from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    chat_id: str = Field(..., min_length=1, description="Identificador único del chat")
    message: str = Field(..., min_length=1, description="Mensaje enviado por el usuario")


class ChatResponse(BaseModel):
    reply: str = Field(..., description="Respuesta generada por NOVA")
    error: Optional[str] = Field(None, description="Mensaje de error si ocurre algún problema")
    image_url: Optional[str] = Field(None, description="URL de imagen generada si aplica")
    audio_url: Optional[str] = Field(None, description="URL de audio generado si aplica")
