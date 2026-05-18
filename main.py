import os
import json
import requests
from datetime import datetime, timedelta
from urllib.parse import quote

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from modelo_texto import responder_mensaje


app = FastAPI(
    title="AMERICO IA CORPORATION",
    description="API de texto, imagen IA, bot Telegram y sistema premium.",
    version="3.1.3",
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


PLANES = {
    "gratis": {"nombre": "GRATIS", "dias": 0, "mensajes": 20, "imagenes": 10},
    "basico": {"nombre": "BÁSICO", "dias": 7, "mensajes": 50, "imagenes": 5},
    "premium": {"nombre": "PREMIUM", "dias": 30, "mensajes": 300, "imagenes": 30},
    "pro": {"nombre": "PRO", "dias": 30, "mensajes": 1000, "imagenes": 100},
    "amigo": {"nombre": "AMIGO", "dias": 9999, "mensajes": 999999, "imagenes": 999999}
}


PLANES_TEXTO = """
╔══════════════════════════════════════╗
║       💎 AMERICO IA CORPORATION      ║
║            PLANES PREMIUM            ║
╚══════════════════════════════════════╝

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


def verificar_api_key(x_api_key: str | None):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API key incorrecta")


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
                    "Tu plan venció.\n\n"
                    "Para seguir usando AMERICO IA CORPORATION, escribe /premium y renueva tu acceso."
                )
        except Exception:
            pass

    if tipo_uso == "mensaje":
        if usuario.get("mensajes_usados", 0) >= datos_plan["mensajes"]:
            guardar_usuarios(usuarios)
            return False, (
                "Llegaste al límite gratuito de 20 mensajes.\n\n"
                "Para seguir navegando y usando AMERICO IA CORPORATION, compra un plan premium con /premium "
                "o vuelve a intentarlo en 2 horas."
            )
        usuario["mensajes_usados"] = usuario.get("mensajes_usados", 0) + 1

    if tipo_uso == "imagen":
        if usuario.get("imagenes_usadas", 0) >= datos_plan["imagenes"]:
            guardar_usuarios(usuarios)
            return False, (
                "Llegaste al límite gratuito de 10 imágenes.\n\n"
                "Para seguir generando imágenes, compra un plan premium con /premium "
                "o vuelve a intentarlo en 2 horas."
            )
        usuario["imagenes_usadas"] = usuario.get("imagenes_usadas", 0) + 1

    guardar_usuarios(usuarios)
    return True, "ok"


def activar_usuario(user_id, plan):
    plan = plan.lower().strip()

    if plan not in PLANES:
        return False, "Plan inválido. Usa: basico, premium, pro o amigo."

    usuarios = cargar_usuarios()
    user_id = str(user_id)

    datos_plan = PLANES[plan]

    if plan == "amigo":
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
        "Bienvenido a AMERICO IA CORPORATION. "
        "Soy la plataforma inteligente corporativa desarrollada por Americo Centeno Colque. "
        "Mi objetivo es brindarte asistencia técnica y profesional en programación, APIs, bots, automatización, "
        "generación de imágenes y otros temas relacionados con tecnología.\n\n"
        "**ESTADO DEL SISTEMA**\n\n"
        "- Lanzamiento oficial: 17/05/2026\n"
        "- Desarrollador principal: Americo Centeno Colque\n"
        "- Plataforma tecnológica: Basada en Python, APIs inteligentes, servicios cloud, automatización y conexión con plataformas externas\n"
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
                {"text": "🤝 AMIGO", "callback_data": f"activar:{user_id}:amigo"}
            ]
        ]
    }

    aviso_admin = (
        "╔══════════════════════════════╗\n"
        "║       NUEVO VOUCHER YAPE     ║\n"
        "╚══════════════════════════════╝\n\n"
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
        "Tu comprobante fue enviado al administrador para revisión. "
        "Si el pago es válido, tu plan será activado."
    )


@app.get("/")
def home():
    return {
        "status": "online",
        "proyecto": "AMERICO IA CORPORATION",
        "creador": "Americo Centeno Colque",
        "texto": "Groq IA",
        "imagen": "Pollinations AI",
        "premium": "activo",
        "supabase_configurado": bool(SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY),
        "gratis": "20 mensajes y 10 imágenes cada 2 horas",
        "endpoints": [
            "/api/texto",
            "/api/texto-app",
            "/api/imagen",
            "/supabase/test",
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


@app.get("/supabase/test")
def supabase_test():
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise HTTPException(
            status_code=500,
            detail="Supabase no configurado en Render"
        )

    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/usuarios?select=*&limit=1",
        headers=headers,
        timeout=30
    )

    return {
        "ok": response.status_code in [200, 201],
        "status_code": response.status_code,
        "respuesta": response.text
    }


@app.post("/api/texto")
def api_texto(data: TextoRequest, x_api_key: str | None = Header(default=None)):
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


@app.get("/api/texto-app")
def api_texto_app(mensaje: str):
    if not mensaje or not mensaje.strip():
        raise HTTPException(status_code=400, detail="Mensaje vacío")

    resultado = responder_mensaje(mensaje)

    return {
        "api": "texto-app",
        "creador": "Americo Centeno Colque",
        "entrada": mensaje,
        "respuesta": resultado["respuesta"]
    }


@app.post("/api/imagen")
def api_imagen(data: ImagenRequest, x_api_key: str | None = Header(default=None)):
    verificar_api_key(x_api_key)

    url_imagen = crear_url_pollinations(data.prompt, data.ancho, data.alto)

    return {
        "api": "imagen",
        "creador": "Americo Centeno Colque",
        "prompt": data.prompt,
        "url": url_imagen
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
        telegram_enviar_mensaje(chat_id, "Solo puedo responder mensajes de texto o recibir vouchers en imagen.")
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
                    f"Usuario ID: {usuario_id}\n"
                    f"Plan activado: {nombre_plan}\n\n"
                    "El usuario ya fue notificado correctamente."
                )

                telegram_enviar_mensaje(usuario_id, mensaje_sistema_activado(nombre_plan))
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
            "Hola. Soy AMERICO IA CORPORATION.\n\n"
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
            telegram_enviar_mensaje(chat_id, "El QR de Yape todavía no está configurado.")

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
                "Escribe un prompt. Ejemplo:\n/imagen robot realista programando una api en python"
            )
            return {"ok": True}

        telegram_enviar_mensaje(chat_id, "Generando imagen con IA, espera un momento...")

        url_imagen = crear_url_pollinations(prompt, 768, 768)

        enviado = telegram_enviar_imagen_url(
            chat_id,
            url_imagen,
            "Imagen generada por AMERICO IA CORPORATION"
        )

        if not enviado:
            telegram_enviar_mensaje(chat_id, "No pude enviar la imagen. Intenta otra vez con otro prompt.")

        return {"ok": True}

    permitido, mensaje_permiso = verificar_permiso(chat_id, "mensaje")

    if not permitido:
        telegram_enviar_mensaje(chat_id, mensaje_permiso)
        return {"ok": True}

    resultado = responder_mensaje(texto)
    telegram_enviar_mensaje(chat_id, resultado["respuesta"])

    return {"ok": True}


@app.get("/telegram/set-webhook")
def telegram_set_webhook(x_api_key: str | None = Header(default=None)):
    verificar_api_key(x_api_key)

    if not TELEGRAM_API:
        raise HTTPException(status_code=500, detail="TELEGRAM_TOKEN no configurado")

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
        raise HTTPException(status_code=500, detail="TELEGRAM_TOKEN no configurado")

    response = requests.get(f"{TELEGRAM_API}/deleteWebhook", timeout=30)

    return response.json()