from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse

from backend.schemas_novap import ChatResponse
from backend.services_novap import generate_reply_stream, generate_reply
import requests

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
    Normaliza sin perder campos premium.
    Antes se devolvia ChatResponse y se filtraban claves extra.
    Ahora chatNOVAP backend entrega todo lo recibido:
    video_job_id, video_status_url, resourceUrls, ZIP, HTML, MP4, etc.
    """
    if isinstance(result, dict):
        result.setdefault("reply", "")
        result.setdefault("error", None)
        result.setdefault("image_url", None)
        result.setdefault("audio_url", None)
        result.setdefault("chart_url", None)

        if "resourceUrls" not in result and "resource_urls" in result:
            result["resourceUrls"] = result.get("resource_urls") or []

        if "resource_urls" not in result and "resourceUrls" in result:
            result["resource_urls"] = result.get("resourceUrls") or []

        return result

    return {
        "reply": str(result) if result is not None else "",
        "error": None,
        "image_url": None,
        "audio_url": None,
        "chart_url": None,
    }


@router.post("/rich-reply")
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

# >>> NOVA&PABLO CHATNOVAP PREMIUM TOTAL OVERRIDE

def normalize_reply_result(result):
    if isinstance(result, dict):
        resource_urls = result.get("resource_urls") or result.get("resourceUrls") or []
        video_job_id = result.get("video_job_id") or result.get("videoJobId")
        video_status_url = result.get("video_status_url") or result.get("videoStatusUrl")

        return ChatResponse(
            reply=result.get("reply", "") or "",
            error=result.get("error"),
            image_url=result.get("image_url"),
            audio_url=result.get("audio_url"),
            chart_url=result.get("chart_url"),
            visual=result.get("visual"),
            autor=result.get("autor"),
            tecnologia=result.get("tecnologia"),
            video_job_id=video_job_id,
            video_status_url=video_status_url,
            videoJobId=video_job_id,
            videoStatusUrl=video_status_url,
            resource_urls=resource_urls,
            resourceUrls=resource_urls,
            raw=result.get("raw") or result,
        )

    return ChatResponse(reply=str(result) if result is not None else "")

# <<< NOVA&PABLO CHATNOVAP PREMIUM TOTAL OVERRIDE


@router.get("/genesios-premium-bridge")
def genesios_premium_bridge(url: str = Query(...)):
    """
    NOVA&PABLO · PUENTE PREMIUM TOTAL GENESIOS.

    Objetivo:
    que chatNOVAP pueda traer desde backend respuestas premium finales
    de GENESIOS sin bloqueo CORS del navegador.

    No es solo vídeo:
    admite estados premium y recursos JSON/texto de GENESIOS cuando estén
    bajo rutas permitidas de genesios.online.
    """
    allowed_prefixes = (
        "https://genesios.online/video-status/",
        "https://genesios.online/static/",
        "https://genesios.online/download/",
    )

    if not url.startswith(allowed_prefixes):
        return {
            "status": "error_url_no_permitida",
            "error": "Solo se permiten URLs premium controladas de genesios.online.",
            "url": url,
            "allowed_prefixes": allowed_prefixes,
        }

    try:
        response = requests.get(
            url,
            headers={"Accept": "application/json, text/plain, */*"},
            timeout=45,
        )

        content_type = response.headers.get("content-type", "")
        text = response.text

        if "application/json" in content_type:
            data = response.json()
        else:
            try:
                import json
                data = json.loads(text)
            except Exception:
                data = {
                    "status": "raw_text",
                    "respuesta": text,
                    "content_type": content_type,
                }

        if isinstance(data, dict):
            data.setdefault("proxied_by", "programanova-chatnovap")
            data.setdefault("source_url", url)
            data.setdefault("premium_bridge", "NOVA&PABLO · PUENTE PREMIUM TOTAL GENESIOS")

        return data

    except Exception as exc:
        return {
            "status": "error_proxy_genesios_premium",
            "url": url,
            "error": str(exc),
            "premium_bridge": "NOVA&PABLO · PUENTE PREMIUM TOTAL GENESIOS",
        }


@router.get("/genesios-video-status")
def genesios_video_status_proxy(url: str = Query(...)):
    """
    Compatibilidad: ruta antigua de estado de vídeo.
    Internamente usa el puente premium total.
    """
    return genesios_premium_bridge(url)

