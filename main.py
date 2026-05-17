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
    version="2.0.0"
)


API_KEY = os.getenv("API_KEY", "americo_api_local")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

CARPETA_IMAGENES = "imagenes"
os.makedirs(CARPETA_IMAGENES, exist_ok=True)


class TextoRequest(BaseModel):
    mensaje: str = Field(..., min_length=1, max_length=500)


class ImagenRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=300)
    ancho: int = Field(default=768, ge=512, le=1024)
    alto: int = Field(default=768, ge=512, le=1024)


def verificar_api_key(x_api_key: str | None):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API key incorrecta")


def cargar_fuente(tamano: int, bold: bool = False):
    fuentes = [
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "arial.ttf"
    ]

    for fuente in fuentes:
        try:
            return ImageFont.truetype(fuente, tamano)
        except Exception:
            pass

    return ImageFont.load_default()


def cortar_texto(texto: str, max_caracteres: int = 34):
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


def crear_fondo_tecnologico(ancho: int, alto: int):
    imagen = Image.new("RGB", (ancho, alto), (8, 12, 28))
    draw = ImageDraw.Draw(imagen)

    for y in range(alto):
        r = int(8 + (y / alto) * 22)
        g = int(12 + (y / alto) * 35)
        b = int(28 + (y / alto) * 70)

        draw.line([(0, y), (ancho, y)], fill=(r, g, b))

    for x in range(0, ancho, 64):
        draw.line([(x, 0), (x, alto)], fill=(20, 60, 110), width=1)

    for y in range(0, alto, 64):
        draw.line([(0, y), (ancho, y)], fill=(20, 60, 110), width=1)

    return imagen


def dibujar_robot(draw: ImageDraw.ImageDraw, cx: int, cy: int):
    metal = (185, 200, 215)
    metal_oscuro = (95, 110, 130)
    sombra = (35, 45, 65)
    azul = (0, 190, 255)
    blanco = (245, 250, 255)
    negro = (10, 15, 25)

    # sombra
    draw.ellipse((cx - 170, cy + 250, cx + 170, cy + 290), fill=(5, 8, 18))

    # antena
    draw.line((cx, cy - 250, cx, cy - 205), fill=metal, width=8)
    draw.ellipse((cx - 20, cy - 285, cx + 20, cy - 245), fill=azul)

    # cabeza
    draw.rounded_rectangle(
        (cx - 130, cy - 210, cx + 130, cy - 20),
        radius=35,
        fill=metal,
        outline=azul,
        width=5
    )

    # brillo cabeza
    draw.rounded_rectangle(
        (cx - 105, cy - 190, cx + 105, cy - 150),
        radius=18,
        fill=(220, 230, 240)
    )

    # ojos
    draw.ellipse((cx - 80, cy - 125, cx - 35, cy - 80), fill=azul)
    draw.ellipse((cx + 35, cy - 125, cx + 80, cy - 80), fill=azul)
    draw.ellipse((cx - 65, cy - 112, cx - 50, cy - 97), fill=blanco)
    draw.ellipse((cx + 50, cy - 112, cx + 65, cy - 97), fill=blanco)

    # boca
    draw.rounded_rectangle(
        (cx - 60, cy - 58, cx + 60, cy - 38),
        radius=8,
        fill=negro
    )

    for i in range(5):
        x = cx - 45 + i * 22
        draw.rectangle((x, cy - 56, x + 8, cy - 40), fill=azul)

    # cuello
    draw.rounded_rectangle(
        (cx - 45, cy - 20, cx + 45, cy + 20),
        radius=10,
        fill=metal_oscuro
    )

    # cuerpo
    draw.rounded_rectangle(
        (cx - 150, cy + 15, cx + 150, cy + 230),
        radius=40,
        fill=metal,
        outline=azul,
        width=5
    )

    # panel pecho
    draw.rounded_rectangle(
        (cx - 95, cy + 55, cx + 95, cy + 150),
        radius=20,
        fill=sombra,
        outline=(120, 210, 255),
        width=3
    )

    draw.text(
        (cx - 58, cy + 85),
        "PY API",
        fill=azul,
        font=cargar_fuente(28, bold=True)
    )

    # luces pecho
    draw.ellipse((cx - 70, cy + 170, cx - 45, cy + 195), fill=(0, 255, 120))
    draw.ellipse((cx - 15, cy + 170, cx + 15, cy + 200), fill=(255, 220, 0))
    draw.ellipse((cx + 45, cy + 170, cx + 70, cy + 195), fill=(255, 70, 70))

    # brazos
    draw.line((cx - 150, cy + 70, cx - 240, cy + 150), fill=metal_oscuro, width=28)
    draw.line((cx + 150, cy + 70, cx + 240, cy + 150), fill=metal_oscuro, width=28)

    draw.ellipse((cx - 270, cy + 130, cx - 215, cy + 185), fill=metal)
    draw.ellipse((cx + 215, cy + 130, cx + 270, cy + 185), fill=metal)

    # laptop
    draw.rounded_rectangle(
        (cx - 190, cy + 245, cx + 190, cy + 360),
        radius=12,
        fill=(18, 24, 38),
        outline=azul,
        width=4
    )

    draw.rectangle((cx - 170, cy + 265, cx + 170, cy + 335), fill=(5, 10, 20))

    codigo = [
        "def api():",
        "  return 'online'",
        "FastAPI + Python"
    ]

    fuente_codigo = cargar_fuente(18, bold=False)
    y = cy + 275
    for linea in codigo:
        draw.text((cx - 150, y), linea, fill=(0, 255, 180), font=fuente_codigo)
        y += 22

    draw.rounded_rectangle(
        (cx - 220, cy + 360, cx + 220, cy + 385),
        radius=8,
        fill=(110, 125, 145)
    )


def crear_imagen_robot(prompt: str, ancho: int, alto: int):
    imagen = crear_fondo_tecnologico(ancho, alto)
    draw = ImageDraw.Draw(imagen)

    fuente_titulo = cargar_fuente(42, bold=True)
    fuente_texto = cargar_fuente(24)
    fuente_marca = cargar_fuente(18)

    # título
    draw.rounded_rectangle(
        (40, 35, ancho - 40, 105),
        radius=22,
        fill=(235, 245, 255),
        outline=(0, 190, 255),
        width=3
    )

    draw.text(
        (70, 52),
        "Robot programador generado",
        fill=(15, 25, 45),
        font=fuente_titulo
    )

    # robot central
    dibujar_robot(draw, ancho // 2, 330)

    # caja prompt
    draw.rounded_rectangle(
        (55, alto - 180, ancho - 55, alto - 75),
        radius=20,
        fill=(10, 18, 35),
        outline=(0, 190, 255),
        width=3
    )

    lineas = cortar_texto(prompt, max_caracteres=42)

    y = alto - 165
    for linea in lineas:
        draw.text(
            (80, y),
            linea,
            fill=(230, 245, 255),
            font=fuente_texto
        )
        y += 30

    draw.text(
        (70, alto - 45),
        "Creado por Americo Centeno Colque",
        fill=(210, 225, 240),
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

    imagen = crear_imagen_robot(
        prompt=data.prompt,
        ancho=data.ancho,
        alto=data.alto
    )

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