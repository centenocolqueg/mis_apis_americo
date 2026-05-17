import os
import requests
from datetime import datetime
from urllib.parse import quote

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from modelo_texto import responder_mensaje


app = FastAPI(
    title="APIs propias de Americo",
    description="API de texto, imagen IA gratis y bot de Telegram.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


API_KEY = os.getenv("API_KEY", "americo_api_local")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}" if TELEGRAM_TOKEN else ""


class TextoRequest(BaseModel):
    mensaje: str = Field(..., min_length=1, max_length=1000)


class ImagenRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=500)
    ancho: int = Field(default=768, ge=256, le=1024)
    alto: int = Field(default=768, ge=256, le=1024)


def verificar_api_key(x_api_key: str | None):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API key incorrecta")


def crear_url_pollinations(prompt: str, ancho: int = 768, alto: int = 768):
    prompt_mejorado = (
        f"{prompt}, imagen realista, alta calidad, ultra detallada, "
        f"iluminación cinematográfica, estilo profesional, 4k"
    )

    prompt_codificado = quote(prompt_mejorado)

    return (
        f"https://image.pollinations.ai/prompt/{prompt_codificado}"
        f"?width={ancho}&height={alto}&nologo=true&enhance=true"
    )


def telegram_enviar_mensaje(chat_id, texto):
    if not TELEGRAM_API:
        return False

    try:
        response = requests.post(
            f"{TELEGRAM_API}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": texto
            },
            timeout=30
        )

        return response.json().get("ok", False)

    except Exception:
        return False


def telegram_enviar_imagen_url(chat_id, url_imagen, caption="Imagen generada por IA"):
    if not TELEGRAM_API:
        return False

    try:
        response = requests.post(
            f"{TELEGRAM_API}/sendPhoto",
            json={
                "chat_id": chat_id,
                "photo": url_imagen,
                "caption": caption
            },
            timeout=90
        )

        return response.json().get("ok", False)

    except Exception:
        return False


@app.get("/")
def home():
    return {
        "status": "online",
        "mensaje": "APIs propias funcionando",
        "creador": "Americo Centeno Colque",
        "modo_texto": "Groq IA",
        "modo_imagen": "Pollinations AI gratis",
        "endpoints": [
            "/api/texto",
            "/api/imagen",
            "/telegram/webhook",
            "/telegram/set-webhook"
        ]
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "time": datetime.utcnow().isoformat()
    }


@app.post("/api/texto")
def api_texto(
    data: TextoRequest,
    x_api_key: str | None = Header(default=None)
):
    verificar_api_key(x_api_key)

    resultado = responder_mensaje(data.mensaje)

    return {
        "api": "texto",
        "creador": "Americo Centeno Colque",
        "entrada": data.mensaje,
        "intencion": resultado["intencion"],
        "confianza": resultado["confianza"],
        "respuesta": resultado["respuesta"]
    }


@app.post("/api/imagen")
def api_imagen(
    data: ImagenRequest,
    x_api_key: str | None = Header(default=None)
):
    verificar_api_key(x_api_key)

    url_imagen = crear_url_pollinations(
        data.prompt,
        data.ancho,
        data.alto
    )

    return {
        "api": "imagen",
        "creador": "Americo Centeno Colque",
        "prompt": data.prompt,
        "url": url_imagen
    }


@app.post("/telegram/webhook")
async def telegram_webhook(update: dict):
    mensaje = update.get("message", {})

    chat = mensaje.get("chat", {})
    chat_id = chat.get("id")

    texto = mensaje.get("text", "")

    if not chat_id:
        return {"ok": True}

    if not texto:
        telegram_enviar_mensaje(
            chat_id,
            "Solo puedo responder mensajes de texto por ahora."
        )
        return {"ok": True}

    texto = texto.strip()

    if texto == "/start":
        telegram_enviar_mensaje(
            chat_id,
            "Hola, soy el bot conectado a la API de Americo Centeno Colque.\n\n"
            "Puedes escribirme una pregunta normal o usar:\n"
            "/imagen robot realista programando una api en python"
        )
        return {"ok": True}

    if texto.startswith("/imagen"):
        prompt = texto.replace("/imagen", "").strip()

        if not prompt:
            telegram_enviar_mensaje(
                chat_id,
                "Escribe un prompt. Ejemplo:\n/imagen robot realista programando una api en python"
            )
            return {"ok": True}

        telegram_enviar_mensaje(
            chat_id,
            "Generando imagen con IA, espera un momento..."
        )

        url_imagen = crear_url_pollinations(prompt, 768, 768)

        enviado = telegram_enviar_imagen_url(
            chat_id,
            url_imagen,
            "Imagen generada por IA para Americo"
        )

        if not enviado:
            telegram_enviar_mensaje(
                chat_id,
                "No pude enviar la imagen. Intenta otra vez con otro prompt."
            )

        return {"ok": True}

    resultado = responder_mensaje(texto)

    telegram_enviar_mensaje(
        chat_id,
        resultado["respuesta"]
    )

    return {"ok": True}


@app.get("/telegram/set-webhook")
def telegram_set_webhook(x_api_key: str | None = Header(default=None)):
    verificar_api_key(x_api_key)

    if not TELEGRAM_API:
        raise HTTPException(status_code=500, detail="TELEGRAM_TOKEN no configurado")

    webhook_url = f"{BASE_URL}/telegram/webhook"

    response = requests.get(
        f"{TELEGRAM_API}/setWebhook",
        params={
            "url": webhook_url
        },
        timeout=30
    )

    return response.json()


@app.get("/telegram/delete-webhook")
def telegram_delete_webhook(x_api_key: str | None = Header(default=None)):
    verificar_api_key(x_api_key)

    if not TELEGRAM_API:
        raise HTTPException(status_code=500, detail="TELEGRAM_TOKEN no configurado")

    response = requests.get(
        f"{TELEGRAM_API}/deleteWebhook",
        timeout=30
    )

    return response.json()