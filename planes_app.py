import os
import requests
from datetime import datetime, timedelta, timezone

APP_NAME = "CENTENO AI"

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

OWNER_EMAILS = [
    "centenocolqueg@gmail.com",
    "profesionalhackeo19@gmail.com"
]

PLANES_APP = {
    "gratis": {
        "modelo": "apis_gratis",
        "creditos_mes": 0,
        "creditos_dia": 0,
        "dias": 0,
        "herramientas": ["chat_gratis", "imagen_basica"]
    },
    "basico": {
        "modelo": "ia_basica",
        "creditos_mes": 3000,
        "creditos_dia": 100,
        "dias": 30,
        "herramientas": [
            "chat_inteligente",
            "redactor",
            "traductor",
            "resumen",
            "corrector"
        ]
    },
    "pro": {
        "modelo": "ia_pro",
        "creditos_mes": 8000,
        "creditos_dia": 300,
        "dias": 30,
        "herramientas": [
            "chat_inteligente",
            "redactor",
            "traductor",
            "resumen",
            "corrector",
            "programacion",
            "respuesta_larga",
            "analizar_imagen",
            "leer_captura",
            "resolver_foto",
            "estudio",
            "negocios"
        ]
    },
    "premium": {
        "modelo": "ia_premium",
        "creditos_mes": 18000,
        "creditos_dia": 700,
        "dias": 30,
        "herramientas": [
            "todo",
            "chat_inteligente",
            "redactor",
            "traductor",
            "resumen",
            "corrector",
            "programacion",
            "respuesta_larga",
            "analizar_imagen",
            "leer_captura",
            "resolver_foto",
            "estudio",
            "negocios",
            "documento",
            "preguntar_documento",
            "voz_a_texto",
            "texto_a_voz",
            "hablar_ia",
            "imagen_premium"
        ]
    }
}

COSTO_HERRAMIENTA = {
    "chat_inteligente": 1,
    "redactor": 2,
    "traductor": 1,
    "resumen": 2,
    "corrector": 1,
    "programacion": 3,
    "respuesta_larga": 3,
    "analizar_imagen": 5,
    "leer_captura": 5,
    "resolver_foto": 6,
    "estudio": 2,
    "negocios": 2,
    "documento": 10,
    "preguntar_documento": 4,
    "imagen_premium": 15,
    "voz_a_texto": 5,
    "texto_a_voz": 5,
    "hablar_ia": 15
}


def limpiar_email(email: str) -> str:
    return (email or "").strip().lower()


def ahora_utc():
    return datetime.now(timezone.utc)


def supabase_headers():
    return {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }


def supabase_disponible() -> bool:
    return bool(SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY)


def es_admin(email: str) -> bool:
    return limpiar_email(email) in OWNER_EMAILS


def respuesta_limite_temporal():
    return {
        "ok": False,
        "codigo": "limite_temporal",
        "mensaje": (
            "Has alcanzado el uso disponible por ahora. "
            "Puedes seguir usando el chat de CENTENO AI normalmente."
        )
    }


def respuesta_plan_superior():
    return {
        "ok": False,
        "codigo": "plan_superior",
        "mensaje": (
            "Esta función está disponible en un plan superior. "
            "Actualiza tu plan para desbloquear IA avanzada."
        )
    }


def respuesta_imagen_gratis_espera():
    return {
        "ok": False,
        "codigo": "espera_imagen",
        "mensaje": (
            "Has alcanzado el límite de generación de imágenes por ahora. "
            "Podrás volver a generar imágenes en 40 minutos. "
            "Mientras tanto, puedes seguir usando el chat de CENTENO AI normalmente."
        )
    }


def crear_usuario_plan_si_no_existe(email: str):
    email = limpiar_email(email)

    if not supabase_disponible() or not email:
        return None

    if es_admin(email):
        data = {
            "email": email,
            "plan_actual": "premium",
            "estado_plan": "activo",
            "modelo_permitido": "ia_premium",
            "creditos_mes": 999999,
            "creditos_dia": 999999,
            "creditos_usados_mes": 0,
            "creditos_usados_hoy": 0,
            "es_admin": True
        }
    else:
        data = {
            "email": email,
            "plan_actual": "gratis",
            "estado_plan": "activo",
            "modelo_permitido": "apis_gratis",
            "creditos_mes": 0,
            "creditos_dia": 0,
            "creditos_usados_mes": 0,
            "creditos_usados_hoy": 0,
            "imagenes_gratis_usadas": 0,
            "es_admin": False
        }

    try:
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/usuarios_planes?on_conflict=email",
            headers={
                **supabase_headers(),
                "Prefer": "resolution=merge-duplicates,return=representation"
            },
            json=data,
            timeout=30
        )

        if response.status_code in [200, 201]:
            rows = response.json()
            return rows[0] if rows else None

        return None

    except Exception:
        return None


def obtener_plan_usuario(email: str):
    email = limpiar_email(email)

    if not supabase_disponible() or not email:
        return {
            "email": email,
            "plan_actual": "gratis",
            "modelo_permitido": "apis_gratis",
            "es_admin": False
        }

    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/usuarios_planes?select=*&email=eq.{email}&limit=1",
            headers=supabase_headers(),
            timeout=30
        )

        if response.status_code == 200:
            rows = response.json()
            if rows:
                usuario = rows[0]

                if es_admin(email):
                    usuario["plan_actual"] = "premium"
                    usuario["modelo_permitido"] = "ia_premium"
                    usuario["es_admin"] = True

                return usuario

        return crear_usuario_plan_si_no_existe(email)

    except Exception:
        return {
            "email": email,
            "plan_actual": "gratis",
            "modelo_permitido": "apis_gratis",
            "es_admin": False
        }


def resetear_creditos_diarios_si_corresponde(usuario: dict):
    if not usuario or not supabase_disponible():
        return usuario

    email = limpiar_email(usuario.get("email", ""))
    ultimo_reset = usuario.get("ultimo_reset_dia")
    hoy = ahora_utc().date().isoformat()

    if ultimo_reset == hoy:
        return usuario

    data = {
        "creditos_usados_hoy": 0,
        "ultimo_reset_dia": hoy,
        "updated_at": ahora_utc().isoformat()
    }

    try:
        requests.patch(
            f"{SUPABASE_URL}/rest/v1/usuarios_planes?email=eq.{email}",
            headers=supabase_headers(),
            json=data,
            timeout=30
        )

        usuario["creditos_usados_hoy"] = 0
        usuario["ultimo_reset_dia"] = hoy

    except Exception:
        pass

    return usuario


def plan_vencido(usuario: dict) -> bool:
    if not usuario:
        return False

    if usuario.get("es_admin"):
        return False

    plan = (usuario.get("plan_actual") or "gratis").lower()

    if plan == "gratis":
        return False

    fecha_fin = usuario.get("fecha_fin_plan")

    if not fecha_fin:
        return True

    try:
        fecha_fin_dt = datetime.fromisoformat(fecha_fin.replace("Z", "+00:00"))
        return ahora_utc() > fecha_fin_dt
    except Exception:
        return True


def volver_a_gratis(email: str):
    email = limpiar_email(email)

    if not supabase_disponible() or not email:
        return False

    data = {
        "plan_actual": "gratis",
        "estado_plan": "activo",
        "modelo_permitido": "apis_gratis",
        "creditos_mes": 0,
        "creditos_dia": 0,
        "creditos_usados_mes": 0,
        "creditos_usados_hoy": 0,
        "updated_at": ahora_utc().isoformat()
    }

    try:
        response = requests.patch(
            f"{SUPABASE_URL}/rest/v1/usuarios_planes?email=eq.{email}",
            headers=supabase_headers(),
            json=data,
            timeout=30
        )
        return response.status_code in [200, 204]
    except Exception:
        return False


def herramienta_permitida(usuario: dict, herramienta: str) -> bool:
    if not usuario:
        return False

    if usuario.get("es_admin"):
        return True

    plan = (usuario.get("plan_actual") or "gratis").lower()

    if plan not in PLANES_APP:
        plan = "gratis"

    herramientas = PLANES_APP[plan]["herramientas"]

    return "todo" in herramientas or herramienta in herramientas


def descontar_creditos(email: str, costo: int):
    email = limpiar_email(email)

    if not supabase_disponible() or not email:
        return False

    usuario = obtener_plan_usuario(email)

    if not usuario:
        return False

    if usuario.get("es_admin"):
        return True

    creditos_usados_mes = int(usuario.get("creditos_usados_mes") or 0) + costo
    creditos_usados_hoy = int(usuario.get("creditos_usados_hoy") or 0) + costo

    data = {
        "creditos_usados_mes": creditos_usados_mes,
        "creditos_usados_hoy": creditos_usados_hoy,
        "updated_at": ahora_utc().isoformat()
    }

    try:
        response = requests.patch(
            f"{SUPABASE_URL}/rest/v1/usuarios_planes?email=eq.{email}",
            headers=supabase_headers(),
            json=data,
            timeout=30
        )
        return response.status_code in [200, 204]
    except Exception:
        return False


def validar_uso_ia(email: str, herramienta: str):
    email = limpiar_email(email)
    herramienta = (herramienta or "chat_inteligente").strip().lower()

    usuario = obtener_plan_usuario(email)

    if not usuario:
        return respuesta_plan_superior()

    usuario = resetear_creditos_diarios_si_corresponde(usuario)

    if plan_vencido(usuario):
        volver_a_gratis(email)
        return respuesta_plan_superior()

    if usuario.get("es_admin"):
        return {
            "ok": True,
            "plan": "premium",
            "modelo": "ia_premium",
            "herramienta": herramienta,
            "costo": 0,
            "admin": True
        }

    plan = (usuario.get("plan_actual") or "gratis").lower()

    if plan == "gratis":
        return respuesta_plan_superior()

    if not herramienta_permitida(usuario, herramienta):
        return respuesta_plan_superior()

    costo = COSTO_HERRAMIENTA.get(herramienta, 1)

    creditos_mes = int(usuario.get("creditos_mes") or 0)
    creditos_dia = int(usuario.get("creditos_dia") or 0)
    usados_mes = int(usuario.get("creditos_usados_mes") or 0)
    usados_hoy = int(usuario.get("creditos_usados_hoy") or 0)

    if usados_hoy + costo > creditos_dia:
        return respuesta_limite_temporal()

    if usados_mes + costo > creditos_mes:
        return respuesta_limite_temporal()

    return {
        "ok": True,
        "plan": plan,
        "modelo": usuario.get("modelo_permitido", PLANES_APP[plan]["modelo"]),
        "herramienta": herramienta,
        "costo": costo,
        "admin": False
    }


def activar_plan_app(email: str, plan: str):
    email = limpiar_email(email)
    plan = (plan or "gratis").strip().lower()

    if plan not in PLANES_APP:
        return False, "Plan inválido"

    datos = PLANES_APP[plan]
    fecha_inicio = ahora_utc()

    if plan == "gratis":
        fecha_fin = None
    else:
        fecha_fin = fecha_inicio + timedelta(days=30)

    data = {
        "email": email,
        "plan_actual": plan,
        "estado_plan": "activo",
        "modelo_permitido": datos["modelo"],
        "fecha_inicio_plan": fecha_inicio.isoformat(),
        "fecha_fin_plan": fecha_fin.isoformat() if fecha_fin else None,
        "creditos_mes": datos["creditos_mes"],
        "creditos_usados_mes": 0,
        "creditos_dia": datos["creditos_dia"],
        "creditos_usados_hoy": 0,
        "ultimo_reset_dia": fecha_inicio.date().isoformat(),
        "updated_at": fecha_inicio.isoformat(),
        "es_admin": es_admin(email)
    }

    if es_admin(email):
        data["plan_actual"] = "premium"
        data["modelo_permitido"] = "ia_premium"
        data["creditos_mes"] = 999999
        data["creditos_dia"] = 999999
        data["es_admin"] = True

    try:
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/usuarios_planes?on_conflict=email",
            headers={
                **supabase_headers(),
                "Prefer": "resolution=merge-duplicates,return=representation"
            },
            json=data,
            timeout=30
        )

        return response.status_code in [200, 201], response.text

    except Exception as e:
        return False, str(e)


def controlar_imagen_gratis(email: str):
    email = limpiar_email(email)
    usuario = obtener_plan_usuario(email)

    if not usuario:
        usuario = crear_usuario_plan_si_no_existe(email)

    if not usuario:
        return {
            "ok": True,
            "mensaje": "Imagen permitida"
        }

    if usuario.get("es_admin"):
        return {
            "ok": True,
            "mensaje": "Admin permitido"
        }

    plan = (usuario.get("plan_actual") or "gratis").lower()

    if plan != "gratis":
        return {
            "ok": True,
            "mensaje": "Plan pagado permitido"
        }

    proxima = usuario.get("proxima_imagen_gratis_at")

    if proxima:
        try:
            proxima_dt = datetime.fromisoformat(proxima.replace("Z", "+00:00"))
            if ahora_utc() < proxima_dt:
                return respuesta_imagen_gratis_espera()
        except Exception:
            pass

    usadas = int(usuario.get("imagenes_gratis_usadas") or 0)

    if usadas >= 10:
        nueva_fecha = ahora_utc() + timedelta(minutes=40)

        data = {
            "imagenes_gratis_usadas": 0,
            "proxima_imagen_gratis_at": nueva_fecha.isoformat(),
            "updated_at": ahora_utc().isoformat()
        }

        try:
            requests.patch(
                f"{SUPABASE_URL}/rest/v1/usuarios_planes?email=eq.{email}",
                headers=supabase_headers(),
                json=data,
                timeout=30
            )
        except Exception:
            pass

        return respuesta_imagen_gratis_espera()

    data = {
        "imagenes_gratis_usadas": usadas + 1,
        "updated_at": ahora_utc().isoformat()
    }

    try:
        requests.patch(
            f"{SUPABASE_URL}/rest/v1/usuarios_planes?email=eq.{email}",
            headers=supabase_headers(),
            json=data,
            timeout=30
        )
    except Exception:
        pass

    return {
        "ok": True,
        "mensaje": "Imagen permitida"
    }
