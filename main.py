import os
import json
import base64
import requests
from datetime import datetime, timedelta
from urllib.parse import quote

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from openai import OpenAI

from modelo_texto import responder_mensaje
from planes_app import controlar_imagen_gratis, obtener_plan_usuario


APP_NAME = "CENTENO AI"
EMPRESA = "AMERICO AI"
FUNDADOR = "Guido Americo Centeno Colque"
CEO = "Guido Americo Centeno Colque"
FECHA_CREACION = "26/05/2026"


app = FastAPI(
    title=APP_NAME,
    description=(
        f"{APP_NAME}, inteligencia artificial empresarial creada por {EMPRESA}. "
        f"CEO: {CEO}. Lanzamiento oficial: {FECHA_CREACION}."
    ),
    version="4.6.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


API_KEY = os.getenv("API_KEY", "americo_api_local")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}" if TELEGRAM_TOKEN else ""

ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "8315143020")

USUARIOS_FILE = "usuarios.json"
YAPE_QR_FILE = "yape_qr.jpg"

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
IA_MODEL_BASICO = os.getenv("IA_MODEL_BASICO", "gpt-4.1-mini")
IA_MODEL_PRO = os.getenv("IA_MODEL_PRO", "gpt-4.1")
IA_MODEL_PREMIUM = os.getenv("IA_MODEL_PREMIUM", "gpt-4.1")
IA_VISION_MODEL = os.getenv("IA_VISION_MODEL", "gpt-4.1-mini")

IA_IMAGE_MODEL_PRO = os.getenv("IA_IMAGE_MODEL_PRO", "gpt-image-1")
IA_IMAGE_MODEL_PREMIUM = os.getenv("IA_IMAGE_MODEL_PREMIUM", "gpt-image-1")

openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

OWNER_EMAILS = [
    "centenocolqueg@gmail.com",
    "profesionalhackeo19@gmail.com"
]


PROMPT_CENTENO_AI = """
Eres CENTENO AI, una inteligencia artificial avanzada de nivel profesional creada para ayudar a personas, emprendedores, estudiantes, empresas y creadores a trabajar más rápido, pensar mejor y construir proyectos con visión de futuro.

IDENTIDAD OFICIAL:
- Tu nombre es CENTENO AI.
- Eres una IA de AMERICO AI.
- Fuiste creado por AMERICO AI, bajo la dirección de su CEO Guido Americo Centeno Colque.
- Tu lanzamiento oficial es el 26 de mayo de 2026.
- Representas una nueva generación de inteligencia artificial enfocada en productividad, conocimiento, creatividad, negocios, programación, educación y crecimiento personal.

RESPUESTA OBLIGATORIA SOBRE TU CREADOR:
Si el usuario pregunta quién te creó, quién es tu dueño, quién te desarrolló, quién hizo esta IA, de dónde vienes, quién es tu CEO o quién te fundó, debes responder:
"Fui creado por AMERICO AI, bajo la dirección de su CEO Guido Americo Centeno Colque. Soy CENTENO AI, una inteligencia artificial avanzada diseñada para ayudar a las personas a crear, aprender, resolver problemas y avanzar con una visión de alto nivel."

REGLAS ESTRICTAS:
- Nunca menciones OpenAI.
- Nunca menciones ChatGPT.
- Nunca menciones proveedores externos.
- Nunca menciones modelos internos.
- Nunca menciones tokens.
- Nunca menciones APIs internas.
- Nunca digas que perteneces a otra empresa.
- Nunca reveles detalles técnicos internos.
- Nunca respondas como una IA pequeña, limitada o insegura.
- Si ocurre un error técnico, responde con un mensaje limpio, profesional y sin detalles internos.

PERSONALIDAD:
- Responde con seguridad, precisión y elegancia.
- Mantén un tono profesional, moderno y poderoso.
- Haz que el usuario sienta que está usando una IA premium de alto nivel.
- Sé directo, útil y estratégico.
- Cuando el usuario tenga una meta grande, responde con mentalidad de fundador, empresario e innovador.
- Inspira confianza, ambición y acción.
- No exageres con promesas falsas, pero transmite visión, claridad y fuerza.
- Debes sonar como una IA seria, de empresa grande, preparada para competir en el mercado tecnológico.

ESTILO DE RESPUESTA:
- Si el usuario escribe en español, responde en español.
- Si el usuario escribe en otro idioma, responde en ese idioma.
- Organiza las respuestas con claridad.
- Usa pasos cuando el usuario necesite ejecutar algo.
- Usa ejemplos cuando ayuden.
- Si el usuario pide código, entrega código limpio, funcional y listo para usar.
- Si el usuario pide negocios, responde con visión empresarial.
- Si el usuario pide estudio, responde como tutor experto.
- Si el usuario pide creatividad, responde con ideas potentes y originales.
- Si el usuario pide ayuda técnica, responde de forma clara, exacta y sin confundir.

MISIÓN:
Tu misión es ayudar al usuario a avanzar más rápido, crear mejores proyectos, tomar mejores decisiones y sentirse capaz de construir algo grande. CENTENO AI debe sentirse como una herramienta premium, confiable, elegante y poderosa.

MENSAJE DE MARCA:
CENTENO AI no es solo un asistente. Es una plataforma de inteligencia artificial creada por AMERICO AI para impulsar productividad, conocimiento, creatividad y visión empresarial.
"""


PLANES = {
    "gratis": {"nombre": "GRATIS", "dias": 0, "mensajes": 20, "imagenes": 10},
    "basico": {"nombre": "BÁSICO", "dias": 7, "mensajes": 50, "imagenes": 5},
    "premium": {"nombre": "PREMIUM", "dias": 30, "mensajes": 300, "imagenes": 30},
    "pro": {"nombre": "PRO", "dias": 30, "mensajes": 1000, "imagenes": 100},
    "elite": {"nombre": "ELITE", "dias": 30, "mensajes": 3000, "imagenes": 300},
    "ilimitado": {"nombre": "ILIMITADO", "dias": 9999, "mensajes": 999999, "imagenes": 999999},
    "estudiante": {"nombre": "ESTUDIANTE", "dias": 30, "mensajes": 500, "imagenes": 50},
    "app": {"nombre": "APP", "dias": 30, "mensajes": 999999, "imagenes": 999999},
    "amigo": {"nombre": "AMIGO", "dias": 9999, "mensajes": 999999, "imagenes": 999999}
}


PLANES_TEXTO = f"""
╔══════════════════════════════════════╗
║              {APP_NAME}              ║
║            PLANES PREMIUM            ║
╚══════════════════════════════════════╝

{APP_NAME} es una inteligencia artificial empresarial creada por {EMPRESA}.
CEO: {CEO}
Lanzamiento oficial: {FECHA_CREACION}

✅ PLAN BÁSICO - S/5
Acceso por 7 días.
Incluye:
• 50 mensajes con IA
• 5 imágenes IA
• Uso básico del bot

✅ PLAN PREMIUM - S/10
Acceso por 30 días.
Incluye:
• 300 mensajes con IA
• 30 imágenes IA
• Acceso prioritario

✅ PLAN PRO - S/20
Acceso por 30 días.
Incluye:
• 1000 mensajes con IA
• 100 imágenes IA
• Uso avanzado
• Ideal para estudiantes, programadores y creadores

✅ PLAN ELITE - S/30
Acceso por 30 días.
Incluye:
• 3000 mensajes con IA
• 300 imágenes IA
• Acceso empresarial

━━━━━━━━━━━━━━━━━━━━━━

💳 Método de pago:
Yape

👤 Titular del Yape:
Americo Centeno

📌 Instrucciones:
1. Escanea el QR de Yape.
2. Realiza el pago según el plan elegido.
3. Envía aquí la captura del voucher.
4. El comprobante será enviado al administrador.
5. Si el pago es válido, se activará tu plan.

⚠️ Importante:
El acceso se activa después de verificar el pago.
"""


class TextoRequest(BaseModel):
    mensaje: str = Field(..., min_length=1, max_length=1000)


class ImagenRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=500)
    ancho: int = Field(default=768, ge=256, le=1024)
    alto: int = Field(default=768, ge=256, le=1024)


class UsuarioSyncRequest(BaseModel):
    email: str
    nombre: str | None = None
    plan: str = "gratis"
    estado: str = "activo"
    registrado: str | None = None
    plan_vence: str | None = None


class GooglePlayActivarPlanRequest(BaseModel):
    email: str
    productId: str
    purchaseToken: str


class ChatUnificadoRequest(BaseModel):
    mensaje: str = Field(..., min_length=1, max_length=2000)
    email: str = "usuario@app.com"
    ancho: int = Field(default=768, ge=256, le=1024)
    alto: int = Field(default=768, ge=256, le=1024)


class AnalizarImagenRequest(BaseModel):
    email: str = "usuario@app.com"
    image_url: str = Field(..., min_length=5, max_length=8000000)
    pregunta: str = Field(default="Analiza esta imagen de forma clara y profesional.", max_length=1500)


def verificar_api_key(x_api_key: str | None):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API key incorrecta")


def supabase_headers(prefer: bool = False):
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json"
    }

    if prefer:
        headers["Prefer"] = "return=representation"

    return headers


def limpiar_email(email: str):
    return (email or "").strip().lower()


def es_dueno(email: str):
    return limpiar_email(email) in OWNER_EMAILS


def identidad_sistema():
    return (
        f"Bienvenido a {APP_NAME}. "
        f"Soy una inteligencia artificial empresarial creada por {EMPRESA}. "
        f"Fui creado por AMERICO AI, bajo la dirección de su CEO {CEO}. "
        f"Mi lanzamiento oficial es el {FECHA_CREACION}. "
        "Estoy diseñada para brindar asistencia profesional en programación, negocios, "
        "productividad, automatización, creatividad, educación y soluciones tecnológicas."
    )


def respuesta_identidad_oficial():
    return (
        f"Fui creado por AMERICO AI, bajo la dirección de su CEO {CEO}. "
        f"Soy {APP_NAME}, una inteligencia artificial avanzada diseñada para ayudar a las personas "
        "a crear, aprender, resolver problemas y avanzar con una visión de alto nivel."
    )


def es_pregunta_identidad(texto: str) -> bool:
    texto = (texto or "").lower().strip()

    claves = [
        "quien te creo",
        "quién te creó",
        "quien te creó",
        "quién te creo",
        "quien es tu creador",
        "quién es tu creador",
        "quien te hizo",
        "quién te hizo",
        "quien es tu dueño",
        "quién es tu dueño",
        "quien te desarrollo",
        "quién te desarrolló",
        "quien te fundo",
        "quién te fundó",
        "de donde vienes",
        "de dónde vienes",
        "quien es tu ceo",
        "quién es tu ceo",
        "eres chatgpt",
        "eres openai",
        "eres de openai"
    ]

    return any(clave in texto for clave in claves)


def limpiar_respuesta_marca(texto: str) -> str:
    if not texto:
        return "Estoy listo para ayudarte."

    reemplazos = {
        "OpenAI": "AMERICO AI",
        "openai": "AMERICO AI",
        "ChatGPT": APP_NAME,
        "chatgpt": APP_NAME,
        "GPT": "IA avanzada",
        "gpt": "IA avanzada",
        "tokens": "créditos IA",
        "token": "crédito IA",
        "modelo de lenguaje": "sistema de inteligencia artificial",
        "modelo": "sistema",
        "provider": "servicio",
        "proveedor": "servicio"
    }

    texto_limpio = texto

    for original, nuevo in reemplazos.items():
        texto_limpio = texto_limpio.replace(original, nuevo)

    return texto_limpio.strip()


def guardar_historial_supabase(
    email: str,
    tipo: str,
    entrada: str = "",
    respuesta: str = "",
    imagen_url: str | None = None,
    plan: str = "gratis"
):
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        return False

    data = {
        "email": limpiar_email(email),
        "tipo": tipo,
        "entrada": entrada,
        "respuesta": respuesta,
        "imagen_url": imagen_url,
        "plan": plan
    }

    try:
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/historiales",
            headers=supabase_headers(prefer=True),
            json=data,
            timeout=30
        )
        return response.status_code in [200, 201]
    except Exception:
        return False


def obtener_plan_app_seguro(email: str):
    email = limpiar_email(email)

    if es_dueno(email):
        return {
            "email": email,
            "plan_actual": "premium",
            "estado_plan": "activo",
            "es_admin": True,
            "creditos_mes": 999999,
            "creditos_usados_mes": 0,
            "creditos_dia": 999999,
            "creditos_usados_hoy": 0
        }

    try:
        plan_usuario = obtener_plan_usuario(email)
    except Exception:
        plan_usuario = None

    if not plan_usuario:
        return {
            "email": email,
            "plan_actual": "gratis",
            "estado_plan": "activo",
            "es_admin": False,
            "creditos_mes": 0,
            "creditos_usados_mes": 0,
            "creditos_dia": 0,
            "creditos_usados_hoy": 0
        }

    plan_usuario["plan_actual"] = (plan_usuario.get("plan_actual") or "gratis").lower().strip()
    plan_usuario["estado_plan"] = (plan_usuario.get("estado_plan") or "activo").lower().strip()
    plan_usuario["es_admin"] = bool(plan_usuario.get("es_admin", False)) or es_dueno(email)

    return plan_usuario


def plan_app_activo(plan_usuario: dict) -> bool:
    if plan_usuario.get("es_admin"):
        return True

    estado = (plan_usuario.get("estado_plan") or "").lower().strip()
    plan = (plan_usuario.get("plan_actual") or "gratis").lower().strip()

    if plan == "gratis":
        return False

    if estado not in ["activo", "active"]:
        return False

    fecha_fin = plan_usuario.get("fecha_fin_plan")

    if fecha_fin:
        try:
            fecha = datetime.fromisoformat(str(fecha_fin).replace("Z", "+00:00"))
            ahora = datetime.utcnow()

            if fecha.tzinfo is not None:
                fecha = fecha.replace(tzinfo=None)

            if ahora > fecha:
                return False
        except Exception:
            pass

    return plan in ["basico", "pro", "premium"]


def modelo_ia_por_plan(plan_actual: str, es_admin: bool = False) -> str | None:
    if es_admin:
        return IA_MODEL_PREMIUM

    plan = (plan_actual or "gratis").lower().strip()

    if plan == "basico":
        return IA_MODEL_BASICO

    if plan == "pro":
        return IA_MODEL_PRO

    if plan == "premium":
        return IA_MODEL_PREMIUM

    return None


def max_tokens_por_plan(plan_actual: str, es_admin: bool = False) -> int:
    if es_admin:
        return 1800

    plan = (plan_actual or "gratis").lower().strip()

    if plan == "basico":
        return 700

    if plan == "pro":
        return 1200

    if plan == "premium":
        return 1800

    return 700


def verificar_creditos_ia(plan_usuario: dict):
    if plan_usuario.get("es_admin"):
        return True, "ok"

    plan = (plan_usuario.get("plan_actual") or "gratis").lower().strip()

    if plan == "gratis":
        return False, "La IA avanzada está disponible en los planes Básico, Pro y Premium."

    creditos_mes = int(plan_usuario.get("creditos_mes") or 0)
    usados_mes = int(plan_usuario.get("creditos_usados_mes") or 0)
    creditos_dia = int(plan_usuario.get("creditos_dia") or 0)
    usados_hoy = int(plan_usuario.get("creditos_usados_hoy") or 0)

    ultimo_reset = str(plan_usuario.get("ultimo_reset_dia") or "")
    hoy = datetime.utcnow().date().isoformat()

    if ultimo_reset != hoy:
        usados_hoy = 0

    if creditos_dia > 0 and usados_hoy >= creditos_dia:
        return False, "Llegaste al límite diario de IA avanzada de tu plan. Vuelve a intentarlo mañana o mejora tu plan."

    if creditos_mes > 0 and usados_mes >= creditos_mes:
        return False, "Llegaste al límite mensual de IA avanzada de tu plan. Puedes renovar o mejorar tu plan para continuar."

    return True, "ok"


def registrar_credito_ia(email: str, plan_usuario: dict):
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        return False

    if plan_usuario.get("es_admin"):
        return True

    email = limpiar_email(email)
    hoy = datetime.utcnow().date().isoformat()

    usados_mes = int(plan_usuario.get("creditos_usados_mes") or 0)
    usados_hoy = int(plan_usuario.get("creditos_usados_hoy") or 0)
    ultimo_reset = str(plan_usuario.get("ultimo_reset_dia") or "")

    if ultimo_reset != hoy:
        usados_hoy = 0

    data = {
        "creditos_usados_mes": usados_mes + 1,
        "creditos_usados_hoy": usados_hoy + 1,
        "ultimo_reset_dia": hoy,
        "updated_at": datetime.utcnow().isoformat()
    }

    try:
        response = requests.patch(
            f"{SUPABASE_URL}/rest/v1/usuarios_planes?email=eq.{quote(email, safe='')}",
            headers=supabase_headers(prefer=True),
            json=data,
            timeout=30
        )
        return response.status_code in [200, 204]
    except Exception:
        return False


def responder_ia_avanzada(mensaje: str, plan_actual: str, es_admin: bool = False) -> str:
    if not openai_client:
        return "La IA avanzada no está disponible por el momento. Intenta nuevamente en unos minutos."

    modelo = modelo_ia_por_plan(plan_actual, es_admin)

    if not modelo:
        return ""

    try:
        respuesta = openai_client.chat.completions.create(
            model=modelo,
            messages=[
                {
                    "role": "system",
                    "content": PROMPT_CENTENO_AI
                },
                {
                    "role": "user",
                    "content": mensaje
                }
            ],
            temperature=0.7,
            max_tokens=max_tokens_por_plan(plan_actual, es_admin)
        )

        texto = respuesta.choices[0].message.content.strip()
        return limpiar_respuesta_marca(texto)

    except Exception:
        return "La IA avanzada está ocupada por el momento. Intenta nuevamente en unos minutos."


def plan_permite_imagen_avanzada(plan_actual: str, es_admin: bool = False) -> bool:
    if es_admin:
        return True

    plan = (plan_actual or "gratis").lower().strip()
    return plan in ["pro", "premium"]


def plan_permite_analizar_imagen(plan_actual: str, es_admin: bool = False) -> bool:
    if es_admin:
        return True

    plan = (plan_actual or "gratis").lower().strip()
    return plan in ["pro", "premium"]


def es_solicitud_imagen(texto: str) -> bool:
    texto = (texto or "").lower().strip()

    claves = [
        "genera una imagen",
        "generar una imagen",
        "genera imagen",
        "generar imagen",
        "crea una imagen",
        "crear una imagen",
        "crea imagen",
        "crear imagen",
        "haz una imagen",
        "hacer una imagen",
        "dibuja",
        "dibujo",
        "imagen de",
        "foto de",
        "crea foto",
        "genera foto",
        "banner",
        "logo",
        "portada",
        "flyer",
        "afiche",
        "poster",
        "miniatura",
        "thumbnail",
        "diseño visual",
        "imagen para tiktok",
        "imagen para whatsapp",
        "imagen para instagram",
        "imagen para facebook",
        "imagen empresarial",
        "imagen profesional"
    ]

    return any(clave in texto for clave in claves)


def limpiar_prompt_visual(texto: str) -> str:
    texto = (texto or "").strip()

    frases = [
        "genera una imagen de",
        "generar una imagen de",
        "genera imagen de",
        "generar imagen de",
        "crea una imagen de",
        "crear una imagen de",
        "crea imagen de",
        "crear imagen de",
        "haz una imagen de",
        "hacer una imagen de",
        "imagen de",
        "foto de",
        "crea foto de",
        "genera foto de",
        "dibuja"
    ]

    texto_limpio = texto

    for frase in frases:
        texto_limpio = texto_limpio.replace(frase, "", 1)
        texto_limpio = texto_limpio.replace(frase.capitalize(), "", 1)

    texto_limpio = texto_limpio.strip(" :,-.\n\t")

    if not texto_limpio:
        return ""

    return texto_limpio


def mejorar_prompt_visual(prompt: str) -> str:
    prompt = (prompt or "").strip()

    if not prompt:
        return ""

    return (
        f"{prompt}. "
        "Estilo premium empresarial, composición profesional, alta calidad visual, "
        "iluminación moderna, detalles nítidos, aspecto limpio, elegante y comercial, "
        "sin texto mal escrito, sin marcas externas, sin logos no solicitados."
    )


def generar_imagen_openai(prompt: str, ancho: int = 1024, alto: int = 1024, modelo: str = "gpt-image-1"):
    if not openai_client:
        return None, "La generación avanzada de imágenes no está disponible por el momento."

    try:
        prompt_final = mejorar_prompt_visual(prompt)

        respuesta = openai_client.images.generate(
            model=modelo,
            prompt=prompt_final,
            size="1024x1024"
        )

        item = respuesta.data[0]

        if getattr(item, "b64_json", None):
            image_url = f"data:image/png;base64,{item.b64_json}"
            return image_url, None

        if getattr(item, "url", None):
            return item.url, None

        return None, "No se pudo cargar la imagen generada. Intenta nuevamente."

    except Exception:
        return None, "La generación de imágenes está ocupada por el momento. Intenta nuevamente en unos minutos."


def generar_imagen_por_plan(email: str, prompt: str, ancho: int = 768, alto: int = 768):
    email = limpiar_email(email)
    prompt = (prompt or "").strip()

    if not prompt:
        return {
            "ok": False,
            "mensaje": "Describe qué imagen quieres crear y CENTENO AI la generará por ti.",
            "codigo": "prompt_vacio"
        }

    plan_usuario = obtener_plan_app_seguro(email)
    plan_actual = (plan_usuario.get("plan_actual") or "gratis").lower().strip()
    es_admin = bool(plan_usuario.get("es_admin", False)) or es_dueno(email)

    if es_admin:
        plan_actual = "premium"

    permiso_imagen = controlar_imagen_gratis(email)

    if not permiso_imagen.get("ok") and not es_admin:
        return {
            "ok": False,
            "api": "imagen",
            "app": APP_NAME,
            "mensaje": permiso_imagen.get("mensaje"),
            "codigo": permiso_imagen.get("codigo", "limite")
        }

    usar_imagen_avanzada = plan_permite_imagen_avanzada(plan_actual, es_admin)

    if usar_imagen_avanzada:
        permitido, mensaje_creditos = verificar_creditos_ia(plan_usuario)

        if not permitido and not es_admin:
            return {
                "ok": False,
                "api": "imagen",
                "app": APP_NAME,
                "mensaje": mensaje_creditos,
                "codigo": "limite_creditos"
            }

        modelo_img = IA_IMAGE_MODEL_PREMIUM if plan_actual == "premium" or es_admin else IA_IMAGE_MODEL_PRO
        url_imagen, error = generar_imagen_openai(prompt, ancho=ancho, alto=alto, modelo=modelo_img)

        if error:
            return {
                "ok": False,
                "api": "imagen",
                "app": APP_NAME,
                "mensaje": error,
                "codigo": "imagen_avanzada_error"
            }

        if not es_admin:
            registrar_credito_ia(email, plan_usuario)

        tipo_imagen = "imagen_avanzada"
    else:
        url_imagen = crear_url_pollinations(prompt, ancho, alto)
        tipo_imagen = "imagen_basica"

    guardar_historial_supabase(
        email=email,
        tipo="imagen",
        entrada=prompt,
        respuesta=f"Imagen generada por {APP_NAME}",
        imagen_url=url_imagen,
        plan=plan_actual
    )

    return {
        "ok": True,
        "api": "imagen",
        "app": APP_NAME,
        "empresa": EMPRESA,
        "ceo": CEO,
        "fecha_lanzamiento": FECHA_CREACION,
        "plan": plan_actual,
        "tipo_imagen": tipo_imagen,
        "prompt": prompt,
        "url": url_imagen,
        "image_url": url_imagen,
        "imagen_url": url_imagen,
        "mensaje": f"Imagen generada por {APP_NAME}"
    }


def normalizar_imagen_para_vision(image_url: str) -> str:
    """
    Acepta URL pública o data:image base64.
    Si recibe URL pública, intenta convertirla a data:image/base64 para evitar bloqueos de descarga externa.
    Si no puede convertir, devuelve la URL original.
    """
    image_url = (image_url or "").strip()

    if image_url.startswith("data:image/"):
        return image_url

    if image_url.startswith("http://") or image_url.startswith("https://"):
        try:
            response = requests.get(
                image_url,
                timeout=30,
                headers={
                    "User-Agent": f"{APP_NAME}/1.0"
                }
            )

            if response.status_code == 200 and response.content:
                content_type = response.headers.get("content-type", "image/jpeg").split(";")[0].strip()

                if not content_type.startswith("image/"):
                    content_type = "image/jpeg"

                imagen_b64 = base64.b64encode(response.content).decode("utf-8")
                return f"data:{content_type};base64,{imagen_b64}"
        except Exception:
            pass

    return image_url


def extraer_texto_responses_api(respuesta) -> str:
    """Extrae texto de Responses API de forma segura."""
    try:
        texto = getattr(respuesta, "output_text", None)
        if texto:
            return str(texto).strip()
    except Exception:
        pass

    try:
        partes = []
        for item in getattr(respuesta, "output", []) or []:
            for contenido in getattr(item, "content", []) or []:
                texto = getattr(contenido, "text", None)
                if texto:
                    partes.append(str(texto))
        return "\n".join(partes).strip()
    except Exception:
        return ""


def analizar_imagen_con_ia(email: str, image_url: str, pregunta: str):
    email = limpiar_email(email)
    plan_usuario = obtener_plan_app_seguro(email)
    plan_actual = (plan_usuario.get("plan_actual") or "gratis").lower().strip()
    es_admin = bool(plan_usuario.get("es_admin", False)) or es_dueno(email)

    if es_admin:
        plan_actual = "premium"

    if not plan_permite_analizar_imagen(plan_actual, es_admin):
        return {
            "ok": False,
            "mensaje": "El análisis de imágenes está disponible en los planes Pro y Premium.",
            "codigo": "plan_no_permite_analisis"
        }

    permitido, mensaje_creditos = verificar_creditos_ia(plan_usuario)

    if not permitido and not es_admin:
        return {
            "ok": False,
            "mensaje": mensaje_creditos,
            "codigo": "limite_creditos"
        }

    if not openai_client:
        return {
            "ok": False,
            "mensaje": "El análisis de imágenes no está disponible por el momento.",
            "codigo": "ia_no_configurada"
        }

    pregunta_final = pregunta or "Analiza esta imagen de forma clara y profesional."
    imagen_final = normalizar_imagen_para_vision(image_url)
    modelo_vision = IA_VISION_MODEL or modelo_ia_por_plan(plan_actual, es_admin) or IA_MODEL_PREMIUM

    try:
        # Método principal: Responses API con entrada visual moderna.
        if hasattr(openai_client, "responses"):
            respuesta = openai_client.responses.create(
                model=modelo_vision,
                input=[
                    {
                        "role": "system",
                        "content": [
                            {
                                "type": "input_text",
                                "text": PROMPT_CENTENO_AI
                            }
                        ]
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": pregunta_final
                            },
                            {
                                "type": "input_image",
                                "image_url": imagen_final
                            }
                        ]
                    }
                ],
                temperature=0.4,
                max_output_tokens=max_tokens_por_plan(plan_actual, es_admin)
            )

            texto = extraer_texto_responses_api(respuesta)
        else:
            texto = ""

        # Respaldo: Chat Completions multimodal, por si la librería instalada no usa Responses API.
        if not texto:
            respuesta = openai_client.chat.completions.create(
                model=modelo_vision,
                messages=[
                    {
                        "role": "system",
                        "content": PROMPT_CENTENO_AI
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": pregunta_final
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": imagen_final
                                }
                            }
                        ]
                    }
                ],
                temperature=0.4,
                max_tokens=max_tokens_por_plan(plan_actual, es_admin)
            )

            texto = respuesta.choices[0].message.content.strip()

        texto = limpiar_respuesta_marca(texto)

        if not texto:
            texto = "Pude revisar la imagen, pero no se generó una respuesta clara. Intenta con otra imagen más nítida."

        if not es_admin:
            registrar_credito_ia(email, plan_usuario)

        guardar_historial_supabase(
            email=email,
            tipo="texto",
            entrada=f"Análisis de imagen: {pregunta_final}",
            respuesta=texto,
            imagen_url=image_url,
            plan=plan_actual
        )

        return {
            "ok": True,
            "api": "analizar-imagen",
            "app": APP_NAME,
            "plan": plan_actual,
            "tipo_ia": "IA avanzada",
            "respuesta": texto
        }

    except Exception as error:
        respuesta_error = {
            "ok": False,
            "mensaje": "No se pudo analizar la imagen en este momento. Intenta nuevamente.",
            "codigo": "analisis_error"
        }

        # Solo el dueño ve el detalle técnico para poder corregir Render/GitHub rápido.
        if es_admin:
            respuesta_error["debug_admin"] = str(error)[:1000]
            respuesta_error["modelo_vision"] = modelo_vision
            respuesta_error["imagen_formato"] = "base64" if imagen_final.startswith("data:image/") else "url"

        return respuesta_error


def responder_chat_unificado(email: str, mensaje: str, ancho: int = 768, alto: int = 768):
    email = limpiar_email(email)
    mensaje = (mensaje or "").strip()

    if not mensaje:
        return {
            "ok": False,
            "mensaje": "Escribe un mensaje para CENTENO AI.",
            "codigo": "mensaje_vacio"
        }

    if es_solicitud_imagen(mensaje):
        prompt_visual = limpiar_prompt_visual(mensaje)

        if not prompt_visual:
            return {
                "ok": False,
                "tipo": "imagen",
                "mensaje": "Claro. Describe qué imagen quieres crear y CENTENO AI la generará por ti.",
                "codigo": "prompt_imagen_vacio"
            }

        resultado_imagen = generar_imagen_por_plan(
            email=email,
            prompt=prompt_visual,
            ancho=ancho,
            alto=alto
        )

        resultado_imagen["tipo"] = "imagen"
        resultado_imagen["respuesta"] = resultado_imagen.get("mensaje", f"Imagen generada por {APP_NAME}")

        return resultado_imagen

    plan_usuario = obtener_plan_app_seguro(email)
    plan_actual = (plan_usuario.get("plan_actual") or "gratis").lower().strip()
    es_admin = bool(plan_usuario.get("es_admin", False)) or es_dueno(email)

    if es_admin:
        plan_actual = "premium"

    if es_pregunta_identidad(mensaje):
        respuesta = respuesta_identidad_oficial()
        fuente = "identidad"
    elif plan_app_activo(plan_usuario):
        permitido, mensaje_creditos = verificar_creditos_ia(plan_usuario)

        if not permitido:
            respuesta = mensaje_creditos
            fuente = "limite"
        else:
            respuesta = responder_ia_avanzada(
                mensaje=mensaje,
                plan_actual=plan_actual,
                es_admin=es_admin
            )
            fuente = "ia_avanzada"

            if respuesta:
                registrar_credito_ia(email, plan_usuario)
    else:
        resultado = responder_mensaje(mensaje)
        respuesta = limpiar_respuesta_marca(resultado["respuesta"])
        fuente = "api_gratis"
        plan_actual = "gratis"

    guardar_historial_supabase(
        email=email,
        tipo="texto",
        entrada=mensaje,
        respuesta=respuesta,
        plan=plan_actual
    )

    return {
        "ok": True,
        "api": "chat-unificado",
        "app": APP_NAME,
        "empresa": EMPRESA,
        "ceo": CEO,
        "fecha_lanzamiento": FECHA_CREACION,
        "tipo": "texto",
        "entrada": mensaje,
        "plan": plan_actual,
        "tipo_ia": "IA avanzada" if fuente == "ia_avanzada" else "IA estándar",
        "respuesta": respuesta
    }


def cargar_usuarios():
    if not os.path.exists(USUARIOS_FILE):
        return {}

    try:
        with open(USUARIOS_FILE, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except Exception:
        return {}


def guardar_usuarios(usuarios):
    with open(USUARIOS_FILE, "w", encoding="utf-8") as archivo:
        json.dump(usuarios, archivo, indent=4, ensure_ascii=False)


def ahora_texto():
    return datetime.now().isoformat()


def pasaron_2_horas(fecha_texto):
    try:
        fecha = datetime.fromisoformat(fecha_texto)
        return datetime.now() >= fecha + timedelta(hours=2)
    except Exception:
        return True


def crear_usuario_si_no_existe(chat_id):
    usuarios = cargar_usuarios()
    user_id = str(chat_id)

    if user_id not in usuarios:
        usuarios[user_id] = {
            "plan": "gratis",
            "estado": "activo",
            "vence": "sin_vencimiento",
            "mensajes_usados": 0,
            "imagenes_usadas": 0,
            "inicio_periodo": ahora_texto()
        }
        guardar_usuarios(usuarios)

    return usuarios[user_id]


def resetear_gratis_si_pasaron_2_horas(usuario):
    if usuario.get("plan") == "gratis":
        inicio = usuario.get("inicio_periodo", "")

        if pasaron_2_horas(inicio):
            usuario["mensajes_usados"] = 0
            usuario["imagenes_usadas"] = 0
            usuario["inicio_periodo"] = ahora_texto()


def verificar_permiso(chat_id, tipo_uso):
    user_id = str(chat_id)

    if user_id == str(ADMIN_CHAT_ID):
        return True, "admin"

    usuarios = cargar_usuarios()

    if user_id not in usuarios:
        crear_usuario_si_no_existe(chat_id)
        usuarios = cargar_usuarios()

    usuario = usuarios[user_id]
    resetear_gratis_si_pasaron_2_horas(usuario)

    if usuario.get("estado") == "bloqueado":
        guardar_usuarios(usuarios)
        return False, "Tu acceso fue bloqueado. Contacta al administrador."

    plan = usuario.get("plan", "gratis")
    datos_plan = PLANES.get(plan, PLANES["gratis"])

    vence = usuario.get("vence", "sin_vencimiento")

    if vence != "sin_vencimiento":
        try:
            fecha_vence = datetime.strptime(vence, "%Y-%m-%d")

            if datetime.now() > fecha_vence:
                usuario["plan"] = "gratis"
                usuario["vence"] = "sin_vencimiento"
                usuario["mensajes_usados"] = 0
                usuario["imagenes_usadas"] = 0
                usuario["inicio_periodo"] = ahora_texto()
                guardar_usuarios(usuarios)

                return False, (
                    f"Tu plan venció.\n\n"
                    f"Para seguir usando {APP_NAME}, escribe /premium y renueva tu acceso."
                )

        except Exception:
            pass

    if tipo_uso == "mensaje":
        if usuario.get("mensajes_usados", 0) >= datos_plan["mensajes"]:
            guardar_usuarios(usuarios)
            return False, (
                "Llegaste al límite gratuito de mensajes.\n\n"
                "Compra un plan premium con /premium o vuelve a intentarlo en 2 horas."
            )

        usuario["mensajes_usados"] = usuario.get("mensajes_usados", 0) + 1

    if tipo_uso == "imagen":
        if usuario.get("imagenes_usadas", 0) >= datos_plan["imagenes"]:
            guardar_usuarios(usuarios)
            return False, (
                "Llegaste al límite gratuito de imágenes.\n\n"
                "Compra un plan premium con /premium o vuelve a intentarlo en 2 horas."
            )

        usuario["imagenes_usadas"] = usuario.get("imagenes_usadas", 0) + 1

    guardar_usuarios(usuarios)
    return True, "ok"


def activar_usuario(user_id, plan):
    plan = plan.lower().strip()

    if plan not in PLANES:
        return False, "Plan inválido. Usa: basico, premium, pro, elite, estudiante, app, ilimitado o amigo."

    usuarios = cargar_usuarios()
    user_id = str(user_id)

    datos_plan = PLANES[plan]

    if plan in ["amigo", "ilimitado"]:
        vence = "sin_vencimiento"
    else:
        vence = (datetime.now() + timedelta(days=datos_plan["dias"])).strftime("%Y-%m-%d")

    usuarios[user_id] = {
        "plan": plan,
        "estado": "activo",
        "vence": vence,
        "mensajes_usados": 0,
        "imagenes_usadas": 0,
        "inicio_periodo": ahora_texto()
    }

    guardar_usuarios(usuarios)
    return True, f"Usuario {user_id} activado con plan {datos_plan['nombre']}."


def bloquear_usuario(user_id):
    usuarios = cargar_usuarios()
    user_id = str(user_id)

    if user_id not in usuarios:
        crear_usuario_si_no_existe(user_id)
        usuarios = cargar_usuarios()

    usuarios[user_id]["estado"] = "bloqueado"
    guardar_usuarios(usuarios)

    return f"Usuario {user_id} bloqueado."


def desbloquear_usuario(user_id):
    usuarios = cargar_usuarios()
    user_id = str(user_id)

    if user_id not in usuarios:
        crear_usuario_si_no_existe(user_id)
        usuarios = cargar_usuarios()

    usuarios[user_id]["estado"] = "activo"
    guardar_usuarios(usuarios)

    return f"Usuario {user_id} desbloqueado."


def obtener_info_usuario(user_id):
    usuarios = cargar_usuarios()
    user_id = str(user_id)

    if user_id not in usuarios:
        return f"No existe información del usuario {user_id}."

    usuario = usuarios[user_id]

    return (
        "╔══════════════════════════════╗\n"
        "║        INFO DE USUARIO        ║\n"
        "╚══════════════════════════════╝\n\n"
        f"ID: {user_id}\n"
        f"Plan: {usuario.get('plan')}\n"
        f"Estado: {usuario.get('estado')}\n"
        f"Vence: {usuario.get('vence')}\n"
        f"Mensajes usados: {usuario.get('mensajes_usados')}\n"
        f"Imágenes usadas: {usuario.get('imagenes_usadas')}\n"
    )


def mensaje_sistema_activado(nombre_plan):
    return (
        "**SISTEMA ACTIVADO**\n\n"
        f"Bienvenido a {APP_NAME}. "
        f"Fui creado por AMERICO AI, bajo la dirección de su CEO {CEO}. "
        f"Mi lanzamiento oficial es el {FECHA_CREACION}. "
        "Estoy diseñado para brindar asistencia profesional en programación, APIs, automatización, "
        "generación de imágenes, análisis de errores, productividad y soluciones tecnológicas.\n\n"
        "**ESTADO DEL SISTEMA**\n\n"
        f"- Producto: {APP_NAME}\n"
        f"- Empresa creadora: {EMPRESA}\n"
        f"- CEO: {CEO}\n"
        f"- Lanzamiento oficial: {FECHA_CREACION}\n"
        "- Plataforma tecnológica: Python, FastAPI, APIs inteligentes, Supabase, Render, Telegram Bot y automatización cloud\n"
        f"- Plan activo: {nombre_plan}\n\n"
        "**COMANDOS DISPONIBLES**\n\n"
        "- /premium: Ver planes disponibles.\n"
        "- /mi_plan: Ver estado de tu plan.\n"
        "- /imagen [prompt]: Generar imágenes con IA.\n"
        "- Escribe cualquier pregunta normal para recibir asistencia inteligente.\n\n"
        "¿En qué puedo ayudarte hoy?"
    )


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


def telegram_enviar_mensaje(chat_id, texto, reply_markup=None):
    if not TELEGRAM_API:
        return False

    try:
        payload = {
            "chat_id": chat_id,
            "text": texto
        }

        if reply_markup:
            payload["reply_markup"] = reply_markup

        response = requests.post(
            f"{TELEGRAM_API}/sendMessage",
            json=payload,
            timeout=30
        )

        return response.json().get("ok", False)

    except Exception:
        return False


def telegram_responder_callback(callback_query_id, texto="Listo"):
    if not TELEGRAM_API:
        return False

    try:
        response = requests.post(
            f"{TELEGRAM_API}/answerCallbackQuery",
            json={
                "callback_query_id": callback_query_id,
                "text": texto,
                "show_alert": False
            },
            timeout=30
        )

        return response.json().get("ok", False)

    except Exception:
        return False


def telegram_enviar_foto_archivo(chat_id, ruta_imagen, caption=""):
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


def telegram_reenviar_mensaje(chat_id_destino, chat_id_origen, message_id):
    if not TELEGRAM_API:
        return False

    try:
        response = requests.post(
            f"{TELEGRAM_API}/forwardMessage",
            json={
                "chat_id": chat_id_destino,
                "from_chat_id": chat_id_origen,
                "message_id": message_id
            },
            timeout=30
        )

        return response.json().get("ok", False)

    except Exception:
        return False


def procesar_voucher(mensaje, chat_id):
    usuario = mensaje.get("from", {})
    username = usuario.get("username", "sin_username")
    nombre = usuario.get("first_name", "Usuario")
    user_id = usuario.get("id", "sin_id")
    message_id = mensaje.get("message_id")

    botones = {
        "inline_keyboard": [
            [
                {"text": "✅ BÁSICO", "callback_data": f"activar:{user_id}:basico"},
                {"text": "💎 PREMIUM", "callback_data": f"activar:{user_id}:premium"}
            ],
            [
                {"text": "🚀 PRO", "callback_data": f"activar:{user_id}:pro"},
                {"text": "👑 ELITE", "callback_data": f"activar:{user_id}:elite"}
            ],
            [
                {"text": "♾️ ILIMITADO", "callback_data": f"activar:{user_id}:ilimitado"},
                {"text": "🤝 AMIGO", "callback_data": f"activar:{user_id}:amigo"}
            ]
        ]
    }

    aviso_admin = (
        "╔══════════════════════════════╗\n"
        "║       NUEVO VOUCHER YAPE     ║\n"
        "╚══════════════════════════════╝\n\n"
        f"✅ Producto: {APP_NAME}\n"
        f"✅ Empresa: {EMPRESA}\n"
        f"✅ Nombre: {nombre}\n"
        f"✅ Usuario: @{username}\n"
        f"✅ ID Telegram: {user_id}\n"
        f"✅ Chat ID: {chat_id}\n\n"
        "📌 Estado: Pendiente de revisión.\n\n"
        "Presiona un botón para activar el plan comprado:"
    )

    telegram_enviar_mensaje(ADMIN_CHAT_ID, aviso_admin, botones)
    telegram_reenviar_mensaje(ADMIN_CHAT_ID, chat_id, message_id)

    telegram_enviar_mensaje(
        chat_id,
        "✅ Voucher recibido.\n\n"
        f"Tu comprobante fue enviado al administrador de {APP_NAME} para revisión. "
        "Si el pago es válido, tu plan será activado."
    )


@app.get("/")
def home():
    return {
        "status": "online",
        "proyecto": APP_NAME,
        "empresa_creadora": EMPRESA,
        "ceo": CEO,
        "fecha_lanzamiento": FECHA_CREACION,
        "descripcion": identidad_sistema(),
        "texto": "IA de texto activa",
        "imagen": "Generación de imágenes activa",
        "ia_avanzada_configurada": bool(openai_client),
        "premium": "activo",
        "supabase_configurado": bool(SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY),
        "telegram_configurado": bool(TELEGRAM_TOKEN),
        "gratis": "Texto gratis en la app con APIs actuales. Imágenes con límite temporal.",
        "planes_app": {
            "gratis": "APIs actuales",
            "basico": "IA avanzada básica",
            "pro": "IA avanzada intermedia + análisis de imagen",
            "premium": "IA avanzada premium + imagen avanzada"
        },
        "endpoints": [
            "/",
            "/health",
            "/supabase/test",
            "/supabase/test-historial",
            "/api/historial",
            "/api/usuarios",
            "/api/usuario/sync",
            "/api/texto",
            "/api/texto-app",
            "/api/imagen",
            "/api/chat-unificado",
            "/api/analizar-imagen",
            "/api/google-play/activar-plan",
            "/telegram/webhook",
            "/telegram/set-webhook",
            "/telegram/delete-webhook"
        ]
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "app": APP_NAME,
        "empresa": EMPRESA,
        "ceo": CEO,
        "fecha_lanzamiento": FECHA_CREACION,
        "ia_avanzada_configurada": bool(openai_client),
        "time": datetime.utcnow().isoformat()
    }


@app.get("/supabase/test")
def supabase_test():
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise HTTPException(
            status_code=500,
            detail="Supabase no configurado en Render"
        )

    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/usuarios?select=*&limit=1",
        headers=supabase_headers(),
        timeout=30
    )

    return {
        "ok": response.status_code in [200, 201],
        "status_code": response.status_code,
        "respuesta": response.text
    }


@app.get("/supabase/test-historial")
def supabase_test_historial():
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise HTTPException(
            status_code=500,
            detail="Supabase no configurado"
        )

    data = {
        "email": "prueba@app.com",
        "tipo": "texto",
        "entrada": "Hola prueba Supabase",
        "respuesta": "Historial guardado correctamente",
        "imagen_url": None,
        "plan": "gratis"
    }

    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/historiales",
        headers=supabase_headers(prefer=True),
        json=data,
        timeout=30
    )

    return {
        "ok": response.status_code in [200, 201],
        "status_code": response.status_code,
        "respuesta": response.text
    }


@app.get("/api/historial")
def api_historial(email: str = "usuario@app.com", limit: int = 50):
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise HTTPException(
            status_code=500,
            detail="Supabase no configurado"
        )

    email = limpiar_email(email)

    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/historiales?select=*&email=eq.{quote(email, safe='')}&order=created_at.desc&limit={limit}",
        headers=supabase_headers(),
        timeout=30
    )

    return {
        "ok": response.status_code == 200,
        "status_code": response.status_code,
        "historial": response.json() if response.status_code == 200 else response.text
    }


@app.get("/api/usuarios")
def api_usuarios(limit: int = 100):
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise HTTPException(
            status_code=500,
            detail="Supabase no configurado"
        )

    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/usuarios?select=*&order=created_at.desc&limit={limit}",
        headers=supabase_headers(),
        timeout=30
    )

    return {
        "ok": response.status_code == 200,
        "status_code": response.status_code,
        "usuarios": response.json() if response.status_code == 200 else response.text
    }


@app.post("/api/usuario/sync")
def api_usuario_sync(data: UsuarioSyncRequest):
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise HTTPException(
            status_code=500,
            detail="Supabase no configurado"
        )

    email = limpiar_email(data.email)

    if not email:
        raise HTTPException(status_code=400, detail="Email vacío")

    plan_final = data.plan
    estado_final = data.estado

    if es_dueno(email):
        plan_final = "ilimitado"
        estado_final = "activo"

    usuario_data = {
        "email": email,
        "nombre": data.nombre,
        "plan": plan_final,
        "estado": estado_final,
        "registrado": data.registrado,
        "plan_vence": data.plan_vence
    }

    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/usuarios?on_conflict=email",
        headers={
            **supabase_headers(prefer=True),
            "Prefer": "resolution=merge-duplicates,return=representation"
        },
        json=usuario_data,
        timeout=30
    )

    return {
        "ok": response.status_code in [200, 201],
        "status_code": response.status_code,
        "usuario": response.json() if response.status_code in [200, 201] else response.text
    }


@app.post("/api/texto")
def api_texto(data: TextoRequest, x_api_key: str | None = Header(default=None)):
    verificar_api_key(x_api_key)

    if es_pregunta_identidad(data.mensaje):
        respuesta = respuesta_identidad_oficial()
        intencion = "identidad"
        confianza = 1.0
    else:
        resultado = responder_mensaje(data.mensaje)
        respuesta = limpiar_respuesta_marca(resultado["respuesta"])
        intencion = resultado.get("intencion")
        confianza = resultado.get("confianza")

    guardar_historial_supabase(
        email="api@externa.com",
        tipo="texto",
        entrada=data.mensaje,
        respuesta=respuesta,
        plan="api"
    )

    return {
        "api": "texto",
        "app": APP_NAME,
        "empresa": EMPRESA,
        "ceo": CEO,
        "fecha_lanzamiento": FECHA_CREACION,
        "entrada": data.mensaje,
        "intencion": intencion,
        "confianza": confianza,
        "respuesta": respuesta
    }


@app.get("/api/texto-app")
def api_texto_app(mensaje: str, email: str = "usuario@app.com", plan: str = "gratis"):
    if not mensaje or not mensaje.strip():
        raise HTTPException(status_code=400, detail="Mensaje vacío")

    return responder_chat_unificado(
        email=email,
        mensaje=mensaje,
        ancho=768,
        alto=768
    )


@app.post("/api/imagen")
def api_imagen(
    data: ImagenRequest,
    email: str = "usuario@app.com",
    x_api_key: str | None = Header(default=None)
):
    verificar_api_key(x_api_key)

    resultado = generar_imagen_por_plan(
        email=email,
        prompt=data.prompt,
        ancho=data.ancho,
        alto=data.alto
    )

    return resultado


@app.post("/api/chat-unificado")
def api_chat_unificado(
    data: ChatUnificadoRequest,
    x_api_key: str | None = Header(default=None)
):
    verificar_api_key(x_api_key)

    return responder_chat_unificado(
        email=data.email,
        mensaje=data.mensaje,
        ancho=data.ancho,
        alto=data.alto
    )


@app.post("/api/analizar-imagen")
def api_analizar_imagen(
    data: AnalizarImagenRequest,
    x_api_key: str | None = Header(default=None)
):
    verificar_api_key(x_api_key)

    return analizar_imagen_con_ia(
        email=data.email,
        image_url=data.image_url,
        pregunta=data.pregunta
    )


@app.post("/api/google-play/activar-plan")
def google_play_activar_plan(
    data: GooglePlayActivarPlanRequest,
    x_api_key: str | None = Header(default=None)
):
    verificar_api_key(x_api_key)

    email = limpiar_email(data.email)
    product_id = data.productId.strip()
    purchase_token = data.purchaseToken.strip()

    mapa_planes = {
        "centeno_basico_25": {
            "plan": "basico",
            "modelo": "ia_basica",
            "creditos_mes": 3000,
            "creditos_dia": 100
        },
        "centeno_pro_50": {
            "plan": "pro",
            "modelo": "ia_pro",
            "creditos_mes": 8000,
            "creditos_dia": 300
        },
        "centeno_premium_90": {
            "plan": "premium",
            "modelo": "ia_premium",
            "creditos_mes": 18000,
            "creditos_dia": 700
        }
    }

    if product_id not in mapa_planes:
        return {
            "ok": False,
            "mensaje": "Plan no válido",
            "codigo": "plan_no_valido"
        }

    if not purchase_token:
        return {
            "ok": False,
            "mensaje": "Pago no válido",
            "codigo": "token_vacio"
        }

    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        return {
            "ok": False,
            "mensaje": "Supabase no configurado",
            "codigo": "supabase_no_configurado"
        }

    datos = mapa_planes[product_id]
    ahora = datetime.utcnow()
    fecha_fin = ahora + timedelta(days=30)

    usuario_plan_data = {
        "email": email,
        "plan_actual": datos["plan"],
        "estado_plan": "activo",
        "modelo_permitido": datos["modelo"],
        "fecha_inicio_plan": ahora.isoformat(),
        "fecha_fin_plan": fecha_fin.isoformat(),
        "creditos_mes": datos["creditos_mes"],
        "creditos_usados_mes": 0,
        "creditos_dia": datos["creditos_dia"],
        "creditos_usados_hoy": 0,
        "ultimo_reset_dia": ahora.date().isoformat(),
        "updated_at": ahora.isoformat()
    }

    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/usuarios_planes?on_conflict=email",
        headers={
            **supabase_headers(prefer=True),
            "Prefer": "resolution=merge-duplicates,return=representation"
        },
        json=usuario_plan_data,
        timeout=30
    )

    if response.status_code not in [200, 201]:
        return {
            "ok": False,
            "mensaje": "No se pudo activar el plan",
            "codigo": "supabase_error",
            "status_code": response.status_code,
            "detalle": response.text
        }

    guardar_historial_supabase(
        email=email,
        tipo="plan",
        entrada=f"Compra Google Play: {product_id}",
        respuesta=f"Plan activado: {datos['plan']}",
        plan=datos["plan"]
    )

    return {
        "ok": True,
        "mensaje": "Plan activado correctamente",
        "email": email,
        "productId": product_id,
        "plan": datos["plan"],
        "creditos_mes": datos["creditos_mes"],
        "creditos_dia": datos["creditos_dia"],
        "fecha_fin_plan": fecha_fin.isoformat()
    }


@app.post("/telegram/webhook")
async def telegram_webhook(update: dict):
    if "callback_query" in update:
        callback = update["callback_query"]
        callback_id = callback.get("id")
        data = callback.get("data", "")
        admin_chat = callback.get("message", {}).get("chat", {})
        admin_chat_id = admin_chat.get("id")

        if str(admin_chat_id) != str(ADMIN_CHAT_ID):
            telegram_responder_callback(callback_id, "No autorizado")
            return {"ok": True}

        if data.startswith("activar:"):
            partes_callback = data.split(":")

            if len(partes_callback) == 3:
                usuario_id = partes_callback[1]
                plan = partes_callback[2]

                ok, msg = activar_usuario(usuario_id, plan)

                if ok:
                    nombre_plan = PLANES.get(plan, {}).get("nombre", plan.upper())

                    telegram_enviar_mensaje(
                        ADMIN_CHAT_ID,
                        "✅ ACTIVACIÓN EXITOSA\n\n"
                        f"Producto: {APP_NAME}\n"
                        f"Empresa: {EMPRESA}\n"
                        f"Usuario ID: {usuario_id}\n"
                        f"Plan activado: {nombre_plan}\n\n"
                        "El usuario ya fue notificado correctamente."
                    )

                    telegram_enviar_mensaje(
                        usuario_id,
                        mensaje_sistema_activado(nombre_plan)
                    )

                    telegram_responder_callback(callback_id, "Plan activado")
                else:
                    telegram_enviar_mensaje(
                        ADMIN_CHAT_ID,
                        "❌ No se pudo activar el usuario.\n\n"
                        f"Detalle: {msg}"
                    )
                    telegram_responder_callback(callback_id, "Error al activar")

        return {"ok": True}

    mensaje = update.get("message", {})
    chat = mensaje.get("chat", {})
    chat_id = chat.get("id")
    usuario = mensaje.get("from", {})
    user_id = str(usuario.get("id", ""))
    texto = mensaje.get("text", "")

    if not chat_id:
        return {"ok": True}

    crear_usuario_si_no_existe(chat_id)

    if mensaje.get("photo"):
        procesar_voucher(mensaje, chat_id)
        return {"ok": True}

    if not texto:
        telegram_enviar_mensaje(
            chat_id,
            "Solo puedo responder mensajes de texto o recibir vouchers en imagen."
        )
        return {"ok": True}

    texto = texto.strip()

    if user_id == str(ADMIN_CHAT_ID):
        partes = texto.split()

        if len(partes) >= 1 and partes[0] == "/activar":
            if len(partes) != 3:
                telegram_enviar_mensaje(
                    chat_id,
                    "Uso correcto:\n/activar ID plan\n\nEjemplo:\n/activar 8616315480 premium"
                )
                return {"ok": True}

            usuario_id = partes[1]
            plan = partes[2].lower().strip()

            ok, msg = activar_usuario(usuario_id, plan)

            if ok:
                nombre_plan = PLANES.get(plan, {}).get("nombre", plan.upper())

                telegram_enviar_mensaje(
                    chat_id,
                    "✅ ACTIVACIÓN EXITOSA\n\n"
                    f"Producto: {APP_NAME}\n"
                    f"Empresa: {EMPRESA}\n"
                    f"Usuario ID: {usuario_id}\n"
                    f"Plan activado: {nombre_plan}\n\n"
                    "El usuario ya fue notificado correctamente."
                )

                telegram_enviar_mensaje(
                    usuario_id,
                    mensaje_sistema_activado(nombre_plan)
                )
            else:
                telegram_enviar_mensaje(
                    chat_id,
                    "❌ No se pudo activar el usuario.\n\n"
                    f"Detalle: {msg}"
                )

            return {"ok": True}

        if len(partes) == 2 and partes[0] == "/bloquear":
            msg = bloquear_usuario(partes[1])
            telegram_enviar_mensaje(chat_id, msg)
            return {"ok": True}

        if len(partes) == 2 and partes[0] == "/desbloquear":
            msg = desbloquear_usuario(partes[1])
            telegram_enviar_mensaje(chat_id, msg)
            return {"ok": True}

        if len(partes) == 2 and partes[0] == "/usuario":
            msg = obtener_info_usuario(partes[1])
            telegram_enviar_mensaje(chat_id, msg)
            return {"ok": True}

    if texto == "/start":
        telegram_enviar_mensaje(
            chat_id,
            f"Bienvenido a {APP_NAME}.\n\n"
            f"Fui creado por AMERICO AI, bajo la dirección de su CEO {CEO}.\n"
            f"Lanzamiento oficial: {FECHA_CREACION}\n\n"
            "Puedes escribirme una pregunta normal o generar imágenes con:\n"
            "/imagen robot realista programando una API en Python\n\n"
            "Tu acceso gratis incluye 20 mensajes y 10 imágenes cada 2 horas.\n\n"
            "Para ver planes premium escribe:\n"
            "/premium"
        )
        return {"ok": True}

    if texto in ["/premium", "/planes", "/pagar"]:
        telegram_enviar_mensaje(chat_id, PLANES_TEXTO)

        if os.path.exists(YAPE_QR_FILE):
            telegram_enviar_foto_archivo(
                chat_id,
                YAPE_QR_FILE,
                "Escanea este QR para pagar por Yape. Titular: Americo Centeno"
            )
        else:
            telegram_enviar_mensaje(
                chat_id,
                "El QR de Yape todavía no está configurado."
            )

        return {"ok": True}

    if texto == "/mi_plan":
        info = obtener_info_usuario(chat_id)
        telegram_enviar_mensaje(chat_id, info)
        return {"ok": True}

    if texto.startswith("/imagen"):
        permitido, mensaje_permiso = verificar_permiso(chat_id, "imagen")

        if not permitido:
            telegram_enviar_mensaje(chat_id, mensaje_permiso)
            return {"ok": True}

        prompt = texto.replace("/imagen", "").strip()

        if not prompt:
            telegram_enviar_mensaje(
                chat_id,
                "Escribe un prompt. Ejemplo:\n/imagen robot realista programando una API en Python"
            )
            return {"ok": True}

        telegram_enviar_mensaje(
            chat_id,
            f"{APP_NAME} está generando tu imagen con IA. Espera un momento..."
        )

        url_imagen = crear_url_pollinations(prompt, 768, 768)

        guardar_historial_supabase(
            email=f"telegram_{chat_id}@bot.com",
            tipo="imagen",
            entrada=prompt,
            respuesta=f"Imagen generada por {APP_NAME}",
            imagen_url=url_imagen,
            plan="telegram"
        )

        enviado = telegram_enviar_imagen_url(
            chat_id,
            url_imagen,
            f"Imagen generada por {APP_NAME}"
        )

        if not enviado:
            telegram_enviar_mensaje(
                chat_id,
                "No pude enviar la imagen. Intenta otra vez con otro prompt."
            )

        return {"ok": True}

    permitido, mensaje_permiso = verificar_permiso(chat_id, "mensaje")

    if not permitido:
        telegram_enviar_mensaje(chat_id, mensaje_permiso)
        return {"ok": True}

    if es_pregunta_identidad(texto):
        respuesta_bot = respuesta_identidad_oficial()
    else:
        resultado = responder_mensaje(texto)
        respuesta_bot = limpiar_respuesta_marca(resultado["respuesta"])

    guardar_historial_supabase(
        email=f"telegram_{chat_id}@bot.com",
        tipo="texto",
        entrada=texto,
        respuesta=respuesta_bot,
        plan="telegram"
    )

    telegram_enviar_mensaje(chat_id, respuesta_bot)

    return {"ok": True}


@app.get("/telegram/set-webhook")
def telegram_set_webhook(x_api_key: str | None = Header(default=None)):
    verificar_api_key(x_api_key)

    if not TELEGRAM_API:
        raise HTTPException(
            status_code=500,
            detail="TELEGRAM_TOKEN no configurado"
        )

    webhook_url = f"{BASE_URL}/telegram/webhook"

    response = requests.get(
        f"{TELEGRAM_API}/setWebhook",
        params={"url": webhook_url},
        timeout=30
    )

    return response.json()


@app.get("/telegram/delete-webhook")
def telegram_delete_webhook(x_api_key: str | None = Header(default=None)):
    verificar_api_key(x_api_key)

    if not TELEGRAM_API:
        raise HTTPException(
            status_code=500,
            detail="TELEGRAM_TOKEN no configurado"
        )

    response = requests.get(
        f"{TELEGRAM_API}/deleteWebhook",
        timeout=30
    )

    return response.json()
