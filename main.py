import os
import uuid
import requests
from datetime import datetime

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from PIL import Image, ImageDraw, ImageFont

from modelo_texto import responder_mensaje


app = FastAPI(
    title="APIs propias de Americo",
    description="API de texto, API de imagen y bot de Telegram en Python.",
    version="1.5.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


API_KEY = os.getenv("API_KEY", "americo_api_local")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}" if TELEGRAM_TOKEN else ""

CARPETA_IMAGENES = "imagenes"
os.makedirs(CARPETA_IMAGENES, exist_ok=True)


class TextoRequest(BaseModel):
    mensaje: str = Field(..., min_length=1, max_length=500)


class ImagenRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=300)
    ancho: int = Field(default=768, ge=256, le=1024)
    alto: int = Field(default=768, ge=256, le=1024)


def verificar_api_key(x_api_key: str | None):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API key incorrecta")


def cargar_fuente(tamano: int, bold: bool = False):
    posibles = [
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "arial.ttf"
    ]

    for fuente in posibles:
        try:
            return ImageFont.truetype(fuente, tamano)
        except Exception:
            pass

    return ImageFont.load_default()


def cortar_texto(texto: str, max_caracteres: int = 26):
    palabras = texto.split()
    lineas = []
    linea_actual = ""

    for palabra in palabras:
        prueba = f"{linea_actual} {palabra}".strip()

        if len(prueba) <= max_caracteres:
            linea_actual = prueba
        else:
            if linea_actual:
                lineas.append(linea_actual)
            linea_actual = palabra

    if linea_actual:
        lineas.append(linea_actual)

    return lineas[:6]


def crear_fondo(ancho: int, alto: int):
    imagen = Image.new("RGB", (ancho, alto), (10, 25, 60))
    draw = ImageDraw.Draw(imagen)

    for y in range(0, alto, 40):
        draw.line((0, y, ancho, y), fill=(20, 60, 120), width=1)

    for x in range(0, ancho, 40):
        draw.line((x, 0, x, alto), fill=(20, 60, 120), width=1)

    for x in range(20, ancho, 90):
        draw.ellipse((x, 30, x + 5, 35), fill=(0, 220, 255))

    for y in range(80, alto, 100):
        draw.ellipse((30, y, 36, y + 6), fill=(0, 220, 255))

    return imagen


def crear_imagen_robot(prompt: str, ancho: int, alto: int):
    imagen = crear_fondo(ancho, alto)
    draw = ImageDraw.Draw(imagen)

    fuente_titulo = cargar_fuente(max(24, ancho // 24), bold=True)
    fuente_texto = cargar_fuente(max(18, ancho // 32), bold=False)
    fuente_marca = cargar_fuente(max(13, ancho // 45), bold=True)
    fuente_api = cargar_fuente(max(16, ancho // 35), bold=True)

    cx = ancho // 2

    draw.rounded_rectangle(
        (20, 20, ancho - 20, alto - 20),
        radius=25,
        outline=(0, 210, 255),
        width=4
    )

    draw.rounded_rectangle(
        (40, 35, ancho - 40, 90),
        radius=18,
        fill=(245, 250, 255)
    )

    draw.text(
        (60, 48),
        "Robot programador",
        fill=(20, 30, 50),
        font=fuente_titulo
    )

    cabeza_w = ancho // 4
    cabeza_h = alto // 6
    cabeza_x1 = cx - cabeza_w // 2
    cabeza_y1 = alto // 5
    cabeza_x2 = cabeza_x1 + cabeza_w
    cabeza_y2 = cabeza_y1 + cabeza_h

    draw.line((cx, cabeza_y1 - 25, cx, cabeza_y1), fill=(180, 230, 255), width=4)
    draw.ellipse((cx - 8, cabeza_y1 - 38, cx + 8, cabeza_y1 - 22), fill=(255, 80, 80))

    draw.rounded_rectangle(
        (cabeza_x1, cabeza_y1, cabeza_x2, cabeza_y2),
        radius=20,
        fill=(190, 200, 215),
        outline=(240, 250, 255),
        width=3
    )

    ojo = max(14, ancho // 40)

    draw.ellipse(
        (cabeza_x1 + 25, cabeza_y1 + 35, cabeza_x1 + 25 + ojo, cabeza_y1 + 35 + ojo),
        fill=(0, 255, 255)
    )

    draw.ellipse(
        (cabeza_x2 - 25 - ojo, cabeza_y1 + 35, cabeza_x2 - 25, cabeza_y1 + 35 + ojo),
        fill=(0, 255, 255)
    )

    draw.rounded_rectangle(
        (cabeza_x1 + 35, cabeza_y2 - 35, cabeza_x2 - 35, cabeza_y2 - 15),
        radius=6,
        fill=(40, 60, 80)
    )

    cuerpo_w = ancho // 3
    cuerpo_h = alto // 4
    cuerpo_x1 = cx - cuerpo_w // 2
    cuerpo_y1 = cabeza_y2 + 20
    cuerpo_x2 = cuerpo_x1 + cuerpo_w
    cuerpo_y2 = cuerpo_y1 + cuerpo_h

    draw.rounded_rectangle(
        (cuerpo_x1, cuerpo_y1, cuerpo_x2, cuerpo_y2),
        radius=25,
        fill=(120, 140, 165),
        outline=(230, 245, 255),
        width=4
    )

    draw.rounded_rectangle(
        (cx - 55, cuerpo_y1 + 25, cx + 55, cuerpo_y1 + 75),
        radius=12,
        fill=(20, 40, 75),
        outline=(0, 220, 255),
        width=3
    )

    draw.text(
        (cx - 42, cuerpo_y1 + 40),
        "PY API",
        fill=(140, 255, 255),
        font=fuente_api
    )

    for i, color in enumerate([(255, 80, 80), (255, 220, 60), (80, 255, 120)]):
        x = cx - 30 + i * 30
        draw.ellipse((x, cuerpo_y1 + 95, x + 16, cuerpo_y1 + 111), fill=color)

    brazo_y = cuerpo_y1 + 55

    draw.line(
        (cuerpo_x1, brazo_y, cuerpo_x1 - 65, brazo_y + 25),
        fill=(180, 190, 205),
        width=14
    )

    draw.line(
        (cuerpo_x2, brazo_y, cuerpo_x2 + 65, brazo_y + 25),
        fill=(180, 190, 205),
        width=14
    )

    draw.ellipse(
        (cuerpo_x1 - 82, brazo_y + 15, cuerpo_x1 - 52, brazo_y + 45),
        fill=(220, 230, 240)
    )

    draw.ellipse(
        (cuerpo_x2 + 52, brazo_y + 15, cuerpo_x2 + 82, brazo_y + 45),
        fill=(220, 230, 240)
    )

    caja_x1 = 45
    caja_y1 = alto - 135
    caja_x2 = ancho - 45
    caja_y2 = alto - 55

    draw.rounded_rectangle(
        (caja_x1, caja_y1, caja_x2, caja_y2),
        radius=16,
        fill=(15, 25, 50),
        outline=(0, 220, 255),
        width=3
    )

    y = caja_y1 + 15

    for linea in cortar_texto(prompt, 30):
        draw.text(
            (caja_x1 + 18, y),
            linea,
            fill=(230, 245, 255),
            font=fuente_texto
        )
        y += 26

    draw.text(
        (45, alto - 38),
        "Creado por Americo Centeno Colque",
        fill=(220, 230, 245),
        font=fuente_marca
    )

    return imagen


def crear_imagen_texto(prompt: str, ancho: int, alto: int):
    imagen = crear_fondo(ancho, alto)
    draw = ImageDraw.Draw(imagen)

    fuente_titulo = cargar_fuente(max(28, ancho // 22), bold=True)
    fuente_texto = cargar_fuente(max(22, ancho // 30))
    fuente_marca = cargar_fuente(max(14, ancho // 45), bold=True)

    draw.rounded_rectangle(
        (25, 25, ancho - 25, alto - 25),
        radius=25,
        outline=(0, 210, 255),
        width=4
    )

    draw.rounded_rectangle(
        (50, 45, ancho - 50, 110),
        radius=18,
        fill=(245, 250, 255)
    )

    draw.text(
        (70, 62),
        "Imagen generada",
        fill=(20, 30, 50),
        font=fuente_titulo
    )

    y = 160

    for linea in cortar_texto(prompt, 28):
        draw.text(
            (60, y),
            linea,
            fill=(230, 245, 255),
            font=fuente_texto
        )
        y += 35

    draw.text(
        (60, alto - 55),
        "Creado por Americo Centeno Colque",
        fill=(220, 230, 245),
        font=fuente_marca
    )

    return imagen


def generar_imagen_archivo(prompt: str, ancho: int = 768, alto: int = 768):
    prompt_limpio = prompt.lower().strip()

    palabras_robot = [
        "robot",
        "android",
        "bot",
        "python",
        "api",
        "programando",
        "programador"
    ]

    if any(palabra in prompt_limpio for palabra in palabras_robot):
        imagen = crear_imagen_robot(prompt, ancho, alto)
    else:
        imagen = crear_imagen_texto(prompt, ancho, alto)

    nombre_archivo = f"{uuid.uuid4().hex}.png"
    ruta = os.path.join(CARPETA_IMAGENES, nombre_archivo)

    imagen.save(ruta, format="PNG", optimize=True)

    return nombre_archivo, ruta, f"{BASE_URL}/imagen/{nombre_archivo}"


def telegram_enviar_mensaje(chat_id, texto):
    if not TELEGRAM_API:
        return

    try:
        requests.post(
            f"{TELEGRAM_API}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": texto
            },
            timeout=30
        )
    except Exception:
        pass


def telegram_enviar_imagen_archivo(chat_id, ruta_imagen, caption="Imagen generada por la API de Americo"):
    if not TELEGRAM_API:
        return False

    try:
        with open(ruta_imagen, "rb") as foto:
            response = requests.post(
                f"{TELEGRAM_API}/sendPhoto",
                data={
                    "chat_id": chat_id,
                    "caption": caption
                },
                files={
                    "photo": foto
                },
                timeout=60
            )

        data = response.json()
        return data.get("ok", False)

    except Exception:
        return False


@app.get("/")
def home():
    return {
        "status": "online",
        "mensaje": "APIs propias funcionando",
        "creador": "Americo Centeno Colque",
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

    nombre_archivo, ruta_imagen, url_imagen = generar_imagen_archivo(
        data.prompt,
        data.ancho,
        data.alto
    )

    return {
        "api": "imagen",
        "creador": "Americo Centeno Colque",
        "prompt": data.prompt,
        "archivo": nombre_archivo,
        "url": url_imagen
    }


@app.get("/imagen/{nombre_archivo}")
def obtener_imagen(nombre_archivo: str):
    ruta = os.path.join(CARPETA_IMAGENES, nombre_archivo)

    if not os.path.exists(ruta):
        raise HTTPException(status_code=404, detail="Imagen no encontrada")

    return FileResponse(ruta, media_type="image/png")


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
            "/imagen robot programando una api en python"
        )
        return {"ok": True}

    if texto.startswith("/imagen"):
        prompt = texto.replace("/imagen", "").strip()

        if not prompt:
            telegram_enviar_mensaje(
                chat_id,
                "Escribe un prompt. Ejemplo:\n/imagen robot programando una api en python"
            )
            return {"ok": True}

        telegram_enviar_mensaje(
            chat_id,
            "Generando imagen, espera un momento..."
        )

        nombre_archivo, ruta_imagen, url_imagen = generar_imagen_archivo(
            prompt,
            512,
            512
        )

        enviado = telegram_enviar_imagen_archivo(
            chat_id,
            ruta_imagen,
            "Imagen generada por la API de Americo"
        )

        if not enviado:
            telegram_enviar_mensaje(
                chat_id,
                "No pude enviar la imagen. Intenta otra vez."
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