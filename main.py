import os
import uuid
from datetime import datetime

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from PIL import Image, ImageDraw, ImageFont

from modelo_texto import responder_mensaje


app = FastAPI(
    title="APIs propias de Americo",
    description="API de texto y API de imagen propias en Python.",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


API_KEY = os.getenv("API_KEY", "americo_api_local")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

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


def cortar_texto(texto: str, max_caracteres: int = 28):
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

    return lineas[:8]


def crear_degradado(ancho: int, alto: int):
    imagen = Image.new("RGB", (ancho, alto))

    for y in range(alto):
        r = int(10 + (y / alto) * 18)
        g = int(18 + (y / alto) * 22)
        b = int(45 + (y / alto) * 85)

        for x in range(ancho):
            imagen.putpixel((x, y), (r, g, b))

    return imagen


def dibujar_detalles_fondo(draw, ancho, alto):
    color = (50, 120, 220)

    for x in range(50, ancho, 120):
        draw.line([(x, 0), (x + 50, 80)], fill=color, width=1)

    for y in range(80, alto, 120):
        draw.line([(0, y), (100, y + 40)], fill=color, width=1)

    for x in range(80, ancho, 160):
        draw.ellipse((x, 90, x + 8, 98), fill=(120, 200, 255))

    for y in range(140, alto, 170):
        draw.ellipse((60, y, 68, y + 8), fill=(120, 200, 255))


def dibujar_robot(draw, ancho, alto):
    centro_x = ancho // 2

    cabeza_w = 170
    cabeza_h = 130
    cabeza_x1 = centro_x - cabeza_w // 2
    cabeza_y1 = 140
    cabeza_x2 = cabeza_x1 + cabeza_w
    cabeza_y2 = cabeza_y1 + cabeza_h

    draw.line((centro_x, cabeza_y1 - 35, centro_x, cabeza_y1), fill=(180, 230, 255), width=6)
    draw.ellipse((centro_x - 12, cabeza_y1 - 52, centro_x + 12, cabeza_y1 - 28), fill=(255, 80, 80))

    draw.rounded_rectangle(
        (cabeza_x1, cabeza_y1, cabeza_x2, cabeza_y2),
        radius=25,
        fill=(185, 195, 210),
        outline=(240, 245, 255),
        width=4
    )

    draw.ellipse((cabeza_x1 + 35, cabeza_y1 + 38, cabeza_x1 + 70, cabeza_y1 + 73), fill=(0, 255, 255))
    draw.ellipse((cabeza_x2 - 70, cabeza_y1 + 38, cabeza_x2 - 35, cabeza_y1 + 73), fill=(0, 255, 255))

    draw.rounded_rectangle(
        (cabeza_x1 + 40, cabeza_y2 - 42, cabeza_x2 - 40, cabeza_y2 - 18),
        radius=8,
        fill=(60, 80, 100)
    )

    for x in range(cabeza_x1 + 48, cabeza_x2 - 40, 18):
        draw.line((x, cabeza_y2 - 40, x, cabeza_y2 - 20), fill=(190, 230, 255), width=2)

    draw.rectangle((centro_x - 18, cabeza_y2, centro_x + 18, cabeza_y2 + 26), fill=(160, 170, 185))

    cuerpo_x1 = centro_x - 115
    cuerpo_y1 = cabeza_y2 + 28
    cuerpo_x2 = centro_x + 115
    cuerpo_y2 = cuerpo_y1 + 170

    draw.rounded_rectangle(
        (cuerpo_x1, cuerpo_y1, cuerpo_x2, cuerpo_y2),
        radius=30,
        fill=(120, 135, 155),
        outline=(230, 240, 255),
        width=4
    )

    draw.rounded_rectangle(
        (centro_x - 55, cuerpo_y1 + 28, centro_x + 55, cuerpo_y1 + 88),
        radius=15,
        fill=(25, 45, 80),
        outline=(120, 220, 255),
        width=3
    )

    draw.text(
        (centro_x - 42, cuerpo_y1 + 45),
        "PY API",
        fill=(140, 255, 255),
        font=cargar_fuente(22, bold=True)
    )

    for i, color in enumerate([(255, 90, 90), (255, 210, 70), (80, 255, 120)]):
        x = centro_x - 28 + i * 28
        draw.ellipse((x, cuerpo_y1 + 110, x + 16, cuerpo_y1 + 126), fill=color)

    brazo_y = cuerpo_y1 + 55

    draw.line((cuerpo_x1, brazo_y, cuerpo_x1 - 95, brazo_y + 20), fill=(170, 180, 195), width=18)
    draw.line((cuerpo_x2, brazo_y, cuerpo_x2 + 95, brazo_y + 20), fill=(170, 180, 195), width=18)

    draw.ellipse((cuerpo_x1 - 112, brazo_y + 5, cuerpo_x1 - 82, brazo_y + 35), fill=(210, 220, 235))
    draw.ellipse((cuerpo_x2 + 82, brazo_y + 5, cuerpo_x2 + 112, brazo_y + 35), fill=(210, 220, 235))

    pierna_y1 = cuerpo_y2

    draw.line((centro_x - 45, pierna_y1, centro_x - 55, pierna_y1 + 95), fill=(170, 180, 195), width=18)
    draw.line((centro_x + 45, pierna_y1, centro_x + 55, pierna_y1 + 95), fill=(170, 180, 195), width=18)

    draw.rounded_rectangle((centro_x - 95, pierna_y1 + 88, centro_x - 25, pierna_y1 + 115), radius=10, fill=(210, 220, 235))
    draw.rounded_rectangle((centro_x + 25, pierna_y1 + 88, centro_x + 95, pierna_y1 + 115), radius=10, fill=(210, 220, 235))


def crear_imagen_robot(prompt: str, ancho: int, alto: int):
    imagen = crear_degradado(ancho, alto)
    draw = ImageDraw.Draw(imagen)

    fuente_titulo = cargar_fuente(32, bold=True)
    fuente_texto = cargar_fuente(24)
    fuente_marca = cargar_fuente(18)

    dibujar_detalles_fondo(draw, ancho, alto)

    draw.rounded_rectangle(
        (25, 25, ancho - 25, alto - 25),
        radius=28,
        outline=(80, 190, 255),
        width=4
    )

    draw.rounded_rectangle(
        (30, 30, ancho - 30, 100),
        radius=20,
        fill=(245, 248, 255)
    )

    draw.text(
        (50, 48),
        "Robot programador generado",
        fill=(20, 30, 50),
        font=fuente_titulo
    )

    dibujar_robot(draw, ancho, alto)

    lineas = cortar_texto(prompt, max_caracteres=30)

    caja_x1 = 70
    caja_y1 = alto - 170
    caja_x2 = ancho - 70
    caja_y2 = alto - 75

    draw.rounded_rectangle(
        (caja_x1, caja_y1, caja_x2, caja_y2),
        radius=18,
        fill=(20, 28, 55),
        outline=(100, 180, 255),
        width=3
    )

    y = caja_y1 + 18
    for linea in lineas:
        draw.text((caja_x1 + 20, y), linea, fill=(210, 235, 255), font=fuente_texto)
        y += 30

    draw.text(
        (40, alto - 45),
        "Creado por Americo Centeno Colque",
        fill=(220, 230, 245),
        font=fuente_marca
    )

    return imagen


def crear_imagen_texto(prompt: str, ancho: int, alto: int):
    imagen = crear_degradado(ancho, alto)
    draw = ImageDraw.Draw(imagen)

    fuente_titulo = cargar_fuente(40, bold=True)
    fuente_texto = cargar_fuente(28)
    fuente_marca = cargar_fuente(18)

    margen = 35

    draw.rounded_rectangle(
        [(margen, margen), (ancho - margen, alto - margen)],
        radius=28,
        outline=(110, 180, 255),
        width=4
    )

    draw.rounded_rectangle(
        [(65, 65), (ancho - 65, 145)],
        radius=20,
        fill=(255, 255, 255)
    )

    draw.text(
        (90, 82),
        "Imagen generada",
        fill=(20, 25, 40),
        font=fuente_titulo
    )

    lineas = cortar_texto(prompt, 30)

    y = 200
    for linea in lineas:
        draw.text(
            (75, y),
            linea,
            fill=(230, 240, 255),
            font=fuente_texto
        )
        y += 42

    draw.text(
        (75, alto - 85),
        "Creado por Americo Centeno Colque",
        fill=(200, 210, 230),
        font=fuente_marca
    )

    return imagen


@app.get("/")
def home():
    return {
        "status": "online",
        "mensaje": "APIs propias funcionando",
        "creador": "Americo Centeno Colque",
        "endpoints": [
            "/api/texto",
            "/api/imagen"
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

    prompt = data.prompt.lower().strip()
    ancho = data.ancho
    alto = data.alto

    palabras_robot = [
        "robot",
        "android",
        "bot",
        "python",
        "api",
        "programando",
        "programador"
    ]

    if any(palabra in prompt for palabra in palabras_robot):
        imagen = crear_imagen_robot(data.prompt, ancho, alto)
    else:
        imagen = crear_imagen_texto(data.prompt, ancho, alto)

    nombre_archivo = f"{uuid.uuid4().hex}.png"
    ruta = os.path.join(CARPETA_IMAGENES, nombre_archivo)

    imagen.save(ruta, format="PNG", optimize=True)

    return {
        "api": "imagen",
        "creador": "Americo Centeno Colque",
        "prompt": data.prompt,
        "archivo": nombre_archivo,
        "url": f"{BASE_URL}/imagen/{nombre_archivo}"
    }


@app.get("/imagen/{nombre_archivo}")
def obtener_imagen(nombre_archivo: str):
    ruta = os.path.join(CARPETA_IMAGENES, nombre_archivo)

    if not os.path.exists(ruta):
        raise HTTPException(status_code=404, detail="Imagen no encontrada")

    return FileResponse(ruta, media_type="image/png")