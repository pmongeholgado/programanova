from openai import OpenAI
import requests
import re
import unicodedata

from backend.nova_identity import NOVA_SYSTEM_PROMPT
from backend.config_novap import (
    OPENAI_API_KEY,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    GENESIOS_URL,
)
from backend.memory_store import get_history, append_message


client = OpenAI(api_key=OPENAI_API_KEY)

MAX_HISTORY_MESSAGES = 20


def is_special_genesios_request(message: str) -> bool:
    return (
        wants_image(message)
        or wants_audio(message)
        or wants_chart(message)
        or wants_premium_resource(message)
    )


def wants_image(message: str) -> bool:
    m = (message or "").lower()
    image_words = [
        "imagen", "imágenes", "image", "images",
        "dibuja", "dibujar", "crea una imagen", "genera una imagen",
        "render", "foto", "picture", "illustration"
    ]
    return any(word in m for word in image_words)


def wants_audio(message: str) -> bool:
    m = (message or "").lower()
    audio_words = [
        "voz", "audio", "habla", "leer", "léelo", "leelo",
        "pronuncia", "reproduce", "escuchar", "escúchalo", "escuchalo"
    ]
    return any(word in m for word in audio_words)


def wants_chart(message: str) -> bool:
    m = (message or "").lower()

    # NOVA&PABLO FIX MINIMO REAL:
    # Evita falso positivo: "grafica" dentro de "cinematografica".
    # Conserva lo correcto: grafico/grafica/lineas con o sin acento.
    m_normalized = "".join(
        c for c in unicodedata.normalize("NFD", m)
        if unicodedata.category(c) != "Mn"
    )

    chart_patterns = [
        r"\bgrafico\b",
        r"\bgrafica\b",
        r"\bchart\b",
        r"\bcharts\b",
        r"\bbarras\b",
        r"\blineas\b",
        r"\bpie\b",
        r"\bcircular\b",
        r"\bcomparativa\b",
        r"\btabla\b",
        r"\btable\b",
    ]

    return any(re.search(pattern, m_normalized) for pattern in chart_patterns)


def wants_premium_resource(message: str) -> bool:
    m = (message or "").lower()
    m_normalized = "".join(
        c for c in unicodedata.normalize("NFD", m)
        if unicodedata.category(c) != "Mn"
    )

    premium_words = [
        "video", "mp4", "zip", "panel", "html", "descargable",
        "recurso", "recursos", "premium", "presentacion",
        "documento", "archivo", "enlace", "enlaces"
    ]

    return any(re.search(r"\b" + re.escape(word) + r"\b", m_normalized) for word in premium_words)


def absolutize_url(base_url: str, maybe_relative: str | None) -> str | None:
    if not maybe_relative:
        return None

    if maybe_relative.startswith("http://") or maybe_relative.startswith("https://"):
        return maybe_relative

    if maybe_relative.startswith("/") and "://" in base_url:
        scheme, rest = base_url.split("://", 1)
        host = rest.split("/", 1)[0]
        return f"{scheme}://{host}{maybe_relative}"

    return maybe_relative


def enforce_structure_soft(text: str) -> str:
    t = (text or "").strip()

    t = re.sub(r"\s-\s", "\n- ", t)
    t = re.sub(r"(#{1,6}\s)", r"\n\n\1", t)
    t = re.sub(r"\n{3,}", "\n\n", t)

    return t.strip()


def build_system_prompt() -> str:
    return NOVA_SYSTEM_PROMPT + """

FORMATO OBLIGATORIO (ESTRICTO):

Responde SIEMPRE en Markdown real.
Responde SIEMPRE en español correcto y natural.
No inventes códigos raros, cadenas extrañas ni texto corrupto.

Reglas obligatorias:
- Usa saltos de línea reales (\\n)
- Usa listas con "-"
- Separa párrafos con línea en blanco
- No escribas toda la respuesta en una sola línea
- No repitas bloques absurdos
- No devuelvas texto técnico interno
"""


def is_bad_genesios_text(reply: str) -> bool:
    text = (reply or "").strip()
    if not text:
        return True

    lower = text.lower()

    bad_markers = [
        "quer och",
        "undefined",
        "null",
        "[object object]",
        "respuesta recibida desde genesios",
        "no se pudo obtener una respuesta válida",
        "error al conectar con genesios",
    ]
    if any(marker in lower for marker in bad_markers):
        return True

    if text.count("|") >= 2:
        return True

    if len(text) < 6:
        return True

    segments = [seg.strip() for seg in re.split(r"[|\n]+", text) if seg.strip()]
    normalized_segments = [
        re.sub(r"^\d+[\.\)\-:\s]*", "", seg.lower())
        for seg in segments
    ]

    if len(normalized_segments) >= 3 and len(set(normalized_segments)) <= 1:
        return True

    letters = sum(ch.isalpha() for ch in text)
    if letters == 0:
        return True

    letters_ratio = letters / max(len(text), 1)
    if letters_ratio < 0.45:
        return True

    return False


def is_bad_history_message(message: dict) -> bool:
    if not isinstance(message, dict):
        return True

    role = (message.get("role") or "").strip().lower()
    content = (message.get("content") or "").strip()

    if role not in {"user", "assistant", "system"}:
        return True

    if not content:
        return True

    lower = content.lower()

    bad_markers = [
        "quer och",
        "[object object]",
        "undefined",
        "null",
        "error interno en chatnovap",
        "error interno en stream chatnovap",
    ]
    if any(marker in lower for marker in bad_markers):
        return True

    return False


def build_model_history(chat_id: str):
    history = get_history(chat_id)

    clean_history = []
    for item in history:
        if not is_bad_history_message(item):
            clean_history.append({
                "role": item["role"],
                "content": item["content"],
            })

    if len(clean_history) > MAX_HISTORY_MESSAGES:
        clean_history = clean_history[-MAX_HISTORY_MESSAGES:]

    return clean_history


def extract_resource_urls_from_text(text: str, endpoint_url: str) -> list:
    if not text:
        return []

    found = []
    pattern = r"https?://[^\s)\]\"']+|/(?:static|video-status)/[^\s)\]\"']+"

    for raw_url in re.findall(pattern, text):
        clean_url = raw_url.rstrip(".,;")
        abs_url = absolutize_url(endpoint_url, clean_url)
        if abs_url and abs_url not in found:
            found.append(abs_url)

    return found


def call_genesios_once(endpoint_url: str, message: str) -> dict:
    response = requests.post(
        endpoint_url,
        json={"mensaje": message},
        headers={"Content-Type": "application/json"},
        timeout=220,
    )
    response.raise_for_status()
    data = response.json()

    reply = (data.get("respuesta") or data.get("reply") or data.get("message") or "").strip()

    image_url = absolutize_url(endpoint_url, data.get("image_url"))
    audio_url = absolutize_url(endpoint_url, data.get("audio_url"))
    chart_url = absolutize_url(
        endpoint_url,
        data.get("chart_url") or data.get("graph_url") or data.get("grafico_url")
    )
    visual = absolutize_url(endpoint_url, data.get("visual"))

    video_job_id = data.get("video_job_id") or data.get("videoJobId")
    video_status_url = absolutize_url(
        endpoint_url,
        data.get("video_status_url") or data.get("videoStatusUrl")
    )

    resource_urls = extract_resource_urls_from_text(reply, endpoint_url)

    direct_resource_keys = [
        "panel_url", "html_url", "zip_url", "download_url", "file_url",
        "video_url", "mp4_url", "document_url", "table_url", "csv_url",
        "pdf_url", "markdown_url", "md_url", "json_url"
    ]

    for key in direct_resource_keys:
        value = data.get(key)
        if value:
            abs_value = absolutize_url(endpoint_url, value)
            if abs_value and abs_value not in resource_urls:
                resource_urls.append(abs_value)

    if video_status_url and video_status_url not in resource_urls:
        resource_urls.append(video_status_url)

    result = {
        "reply": reply,
        "image_url": image_url,
        "audio_url": audio_url,
        "chart_url": chart_url,
        "visual": visual,
        "video_job_id": video_job_id,
        "videoJobId": video_job_id,
        "video_status_url": video_status_url,
        "videoStatusUrl": video_status_url,
        "resource_urls": resource_urls,
        "resourceUrls": resource_urls,
        "bot_id": data.get("bot_id"),
        "autor": data.get("autor"),
        "tecnologia": data.get("tecnologia"),
        "error": None,
    }

    for key, value in data.items():
        if key not in result:
            if isinstance(value, str) and (key.endswith("_url") or value.startswith("/static/") or value.startswith("/video-status/")):
                result[key] = absolutize_url(endpoint_url, value)
            else:
                result[key] = value

    has_content = any([
        result.get("reply"),
        result.get("image_url"),
        result.get("audio_url"),
        result.get("chart_url"),
        result.get("visual"),
        result.get("video_job_id"),
        result.get("video_status_url"),
        result.get("resource_urls"),
    ])

    if has_content:
        return result

    return {
        "reply": "",
        "image_url": None,
        "audio_url": None,
        "chart_url": None,
        "visual": None,
        "video_job_id": None,
        "videoJobId": None,
        "video_status_url": None,
        "videoStatusUrl": None,
        "resource_urls": [],
        "resourceUrls": [],
        "error": "No se pudo obtener una respuesta valida del motor premium.",
    }


def generate_reply_with_genesios(message: str) -> dict:
    try:
        result = call_genesios_once(GENESIOS_URL, message)

        if result.get("error"):
            return result

        return result

    except Exception as e:
        return {
            "reply": "",
            "image_url": None,
            "audio_url": None,
            "chart_url": None,
            "visual": None,
            "video_job_id": None,
            "videoJobId": None,
            "video_status_url": None,
            "videoStatusUrl": None,
            "resource_urls": [],
            "resourceUrls": [],
            "error": f"{GENESIOS_URL} -> {str(e)}",
        }


def generate_text_with_openai(chat_id: str) -> str:
    history = build_model_history(chat_id)

    messages = [
        {
            "role": "system",
            "content": build_system_prompt(),
        },
        *history,
    ]

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=messages,
        temperature=DEFAULT_TEMPERATURE,
    )

    reply = (response.choices[0].message.content or "").strip()
    reply = enforce_structure_soft(reply)

    return reply


def build_special_reply(message: str, genesios_result: dict) -> str:
    genesios_reply = enforce_structure_soft(genesios_result.get("reply", ""))

    if wants_image(message):
        if genesios_result.get("image_url"):
            if genesios_reply and not is_bad_genesios_text(genesios_reply):
                return genesios_reply
            return "Aquí tienes la imagen generada correctamente."
        return "No se pudo generar la imagen correctamente."

    if wants_audio(message):
        if genesios_result.get("audio_url"):
            if genesios_reply and not is_bad_genesios_text(genesios_reply):
                return genesios_reply
            return "Aquí tienes el audio generado correctamente."
        return "No se pudo generar el audio correctamente."

    if wants_chart(message):
        if genesios_result.get("chart_url"):
            if genesios_reply and not is_bad_genesios_text(genesios_reply):
                return genesios_reply
            return "Aquí tienes el gráfico generado correctamente."
        return "No se pudo generar el gráfico correctamente."

    if genesios_reply and not is_bad_genesios_text(genesios_reply):
        return genesios_reply

    return "Solicitud completada correctamente."


def build_special_success_result(chat_id: str, message: str, genesios_result: dict) -> dict:
    final_reply = build_special_reply(message, genesios_result)

    result = dict(genesios_result)
    result["reply"] = final_reply
    result["error"] = None

    if "resourceUrls" not in result and "resource_urls" in result:
        result["resourceUrls"] = result.get("resource_urls") or []

    if "resource_urls" not in result and "resourceUrls" in result:
        result["resource_urls"] = result.get("resourceUrls") or []

    if result["reply"]:
        append_message(chat_id, "assistant", result["reply"])

    return result


def build_text_success_result(chat_id: str, genesios_result: dict) -> dict:
    genesios_reply = enforce_structure_soft(genesios_result.get("reply", ""))

    if not is_bad_genesios_text(genesios_reply):
        result = {
            "reply": genesios_reply,
            "image_url": None,
            "audio_url": None,
            "chart_url": None,
            "error": None,
        }
        append_message(chat_id, "assistant", result["reply"])
        return result

    reply = generate_text_with_openai(chat_id)

    result = {
        "reply": reply,
        "image_url": None,
        "audio_url": None,
        "chart_url": None,
        "error": None,
    }

    append_message(chat_id, "assistant", result["reply"])
    return result


def generate_reply(chat_id: str, message: str):
    try:
        append_message(chat_id, "user", message)

        special_request = is_special_genesios_request(message)

        # NOVA&PABLO FIX MINIMO REAL:
        # Texto normal va directo a OpenAI.
        # Peticiones especiales van a GENESIOS.
        # No se toca generate_reply_stream ni /stream/reply.
        if special_request:
            genesios_result = generate_reply_with_genesios(message)

            if genesios_result.get("error"):
                return {
                    "reply": "No se pudo completar correctamente la peticion especial en GENESIOS.",
                    "image_url": None,
                    "audio_url": None,
                    "chart_url": None,
                    "error": genesios_result.get("error") or "Error al conectar con GENESIOS.",
                }

            return build_special_success_result(chat_id, message, genesios_result)

        reply = generate_text_with_openai(chat_id)

        result = {
            "reply": reply,
            "image_url": None,
            "audio_url": None,
            "chart_url": None,
            "error": None,
        }

        append_message(chat_id, "assistant", result["reply"])
        return result

    except Exception as e:
        return {
            "reply": "",
            "image_url": None,
            "audio_url": None,
            "chart_url": None,
            "error": f"Error IA: {str(e)}",
        }


def generate_reply_stream(chat_id: str, message: str):
    append_message(chat_id, "user", message)

    history = build_model_history(chat_id)

    messages = [
        {
            "role": "system",
            "content": build_system_prompt(),
        },
        *history,
    ]

    stream = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=messages,
        temperature=DEFAULT_TEMPERATURE,
        stream=True,
    )

    reply_full = ""

    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            token = chunk.choices[0].delta.content
            reply_full += token
            yield token

    reply_full = enforce_structure_soft(reply_full)

    if reply_full:
        append_message(chat_id, "assistant", reply_full)

# >>> NOVA&PABLO CHATNOVAP PREMIUM TOTAL OVERRIDE

def wants_premium_total(message: str) -> bool:
    m = (message or "").lower()
    premium_words = [
        "premium", "video", "vídeo", "videos", "vídeos",
        "mp4", "zip", "panel", "html", "markdown", "json",
        "descargable", "descargar", "recurso", "recursos",
        "paquete", "documento", "tabla", "grafico", "gráfico",
        "audio", "imagen", "imagenes", "imágenes"
    ]
    return any(word in m for word in premium_words)


def is_special_genesios_request(message: str) -> bool:
    return wants_premium_total(message) or wants_image(message) or wants_audio(message) or wants_chart(message)


def _np_abs_url(endpoint_url: str, url):
    if not url:
        return None

    if not isinstance(url, str):
        return None

    clean = url.strip()
    if not clean:
        return None

    if clean.startswith("http://") or clean.startswith("https://"):
        return clean

    from urllib.parse import urljoin
    return urljoin(endpoint_url, clean)


def extract_resource_urls_from_text(text: str) -> list[str]:
    import re

    raw = text or ""
    found = set()

    patterns = [
        r"https?://[^\s)\]}'\"<>|]+",
        r"/static/[^\s)\]}'\"<>|]+",
        r"/video-status/[^\s)\]}'\"<>|]+",
        r"/download/[^\s)\]}'\"<>|]+",
    ]

    for pattern in patterns:
        for item in re.findall(pattern, raw):
            clean = item.strip().rstrip(".,;`")
            if clean.endswith("/") and not clean.startswith("/video-status/"):
                continue
            if clean:
                found.add(clean)

    return list(found)


def _np_collect_urls_from_value(endpoint_url: str, value, bucket: set):
    if not value:
        return

    if isinstance(value, str):
        full = _np_abs_url(endpoint_url, value)
        if full:
            bucket.add(full)
        return

    if isinstance(value, list):
        for item in value:
            _np_collect_urls_from_value(endpoint_url, item, bucket)
        return

    if isinstance(value, dict):
        for item in value.values():
            _np_collect_urls_from_value(endpoint_url, item, bucket)


def call_genesios_once(endpoint_url: str, message: str) -> dict:
    import requests

    response = requests.post(
        endpoint_url,
        json={"mensaje": message},
        headers={"Content-Type": "application/json"},
        timeout=260,
    )
    response.raise_for_status()

    data = response.json()
    reply = (data.get("respuesta") or data.get("reply") or data.get("text") or "").strip()

    image_url = _np_abs_url(endpoint_url, data.get("image_url") or data.get("visual"))
    audio_url = _np_abs_url(endpoint_url, data.get("audio_url"))
    chart_url = _np_abs_url(endpoint_url, data.get("chart_url") or data.get("graph_url") or data.get("grafico_url"))
    visual = _np_abs_url(endpoint_url, data.get("visual"))

    video_job_id = data.get("video_job_id") or data.get("videoJobId") or data.get("job_id")
    video_status_url = _np_abs_url(endpoint_url, data.get("video_status_url") or data.get("videoStatusUrl"))

    resource_urls = set()

    for url in extract_resource_urls_from_text(reply):
        full = _np_abs_url(endpoint_url, url) or url
        if full:
            resource_urls.add(full)

    for key in [
        "resource_urls", "resourceUrls", "resources", "recursos",
        "download_url", "download_urls", "downloadUrl", "downloadUrls",
        "zip_url", "zipUrl", "html_url", "htmlUrl", "panel_url", "panelUrl",
        "video_url", "videoUrl", "mp4_url", "mp4Url"
    ]:
        _np_collect_urls_from_value(endpoint_url, data.get(key), resource_urls)

    for url in [image_url, audio_url, chart_url, visual, video_status_url]:
        if url:
            resource_urls.add(url)

    resource_urls = list(resource_urls)

    return {
        "reply": reply or "",
        "image_url": image_url,
        "audio_url": audio_url,
        "chart_url": chart_url,
        "visual": visual,
        "download_url": _np_abs_url(endpoint_url, data.get("download_url") or data.get("downloadUrl") or data.get("panel_url") or data.get("panelUrl") or data.get("html_url") or data.get("htmlUrl")),
        "zip_url": _np_abs_url(endpoint_url, data.get("zip_url") or data.get("zipUrl")),
        "video_url": _np_abs_url(endpoint_url, data.get("video_url") or data.get("videoUrl") or data.get("mp4_url") or data.get("mp4Url")),
        "resources": data.get("resources") or data.get("recursos") or [],
        "table": data.get("table") or data.get("tabla"),
        "autor": data.get("autor"),
        "tecnologia": data.get("tecnologia"),
        "video_job_id": video_job_id,
        "video_status_url": video_status_url,
        "videoJobId": video_job_id,
        "videoStatusUrl": video_status_url,
        "resource_urls": resource_urls,
        "resourceUrls": resource_urls,
        "raw": data,
        "error": None,
    }


def generate_reply_with_genesios(message: str) -> dict:
    try:
        return call_genesios_once(GENESIOS_URL, message)
    except Exception as e:
        return {
            "reply": "",
            "image_url": None,
            "audio_url": None,
            "chart_url": None,
            "visual": None,
            "autor": None,
            "tecnologia": None,
            "video_job_id": None,
            "video_status_url": None,
            "videoJobId": None,
            "videoStatusUrl": None,
            "resource_urls": [],
            "resourceUrls": [],
            "raw": None,
            "error": f"{GENESIOS_URL} -> {str(e)}",
        }


def build_special_success_result(chat_id: str, message: str, genesios_result: dict) -> dict:
    resource_urls = genesios_result.get("resource_urls") or genesios_result.get("resourceUrls") or []
    video_job_id = genesios_result.get("video_job_id") or genesios_result.get("videoJobId")
    video_status_url = genesios_result.get("video_status_url") or genesios_result.get("videoStatusUrl")

    final_reply = genesios_result.get("reply") or build_special_reply(message, genesios_result)

    result = {
        "reply": final_reply,
        "image_url": genesios_result.get("image_url"),
        "audio_url": genesios_result.get("audio_url"),
        "chart_url": genesios_result.get("chart_url"),
        "visual": genesios_result.get("visual"),
        "download_url": genesios_result.get("download_url"),
        "zip_url": genesios_result.get("zip_url"),
        "video_url": genesios_result.get("video_url"),
        "resources": genesios_result.get("resources") or [],
        "table": genesios_result.get("table"),
        "autor": genesios_result.get("autor"),
        "tecnologia": genesios_result.get("tecnologia"),
        "video_job_id": video_job_id,
        "video_status_url": video_status_url,
        "videoJobId": video_job_id,
        "videoStatusUrl": video_status_url,
        "resource_urls": resource_urls,
        "resourceUrls": resource_urls,
        "raw": genesios_result.get("raw"),
        "error": None,
    }

    if result["reply"]:
        append_message(chat_id, "assistant", result["reply"])

    return result

# <<< NOVA&PABLO CHATNOVAP PREMIUM TOTAL OVERRIDE
