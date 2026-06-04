# backend/schemas_novap.py

from typing import Optional, Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    chat_id: str = Field(..., min_length=1, description="Identificador único del chat")
    message: str = Field(..., min_length=1, description="Mensaje enviado por el usuario")


class ChatResponse(BaseModel):
    reply: str = Field(..., description="Respuesta generada por NOVA")
    error: Optional[str] = Field(None, description="Mensaje de error si ocurre algún problema")
    image_url: Optional[str] = Field(None, description="URL de imagen generada si aplica")
    audio_url: Optional[str] = Field(None, description="URL de audio generado si aplica")
    chart_url: Optional[str] = Field(None, description="URL de gráfico generado si aplica")

# >>> NOVA&PABLO CHATNOVAP PREMIUM TOTAL OVERRIDE

class ChatResponse(BaseModel):
    reply: str = ""
    error: str | None = None
    image_url: str | None = None
    audio_url: str | None = None
    chart_url: str | None = None
    visual: str | None = None
    autor: str | None = None
    tecnologia: str | None = None
    video_job_id: str | None = None
    video_status_url: str | None = None
    videoJobId: str | None = None
    videoStatusUrl: str | None = None
    resource_urls: list[str] | None = None
    resourceUrls: list[str] | None = None
    download_url: str | None = None
    zip_url: str | None = None
    video_url: str | None = None
    resources: list[dict[str, Any]] | None = None
    table: dict[str, Any] | None = None
    raw: dict | None = None

# <<< NOVA&PABLO CHATNOVAP PREMIUM TOTAL OVERRIDE
