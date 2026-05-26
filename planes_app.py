import os
import requests
from datetime import datetime, timedelta, timezone


APP_NAME = "CENTENO AI"

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip().rstrip("/")

SUPABASE_SERVICE_ROLE_KEY = (
    os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    or os.getenv("SUPABASE_KEY", "").strip()
    or os.getenv("SUPABASE_ANON_KEY", "").strip()
)

OWNER_EMAILS = [
    "centenocolqueg@gmail.com",
    "profesionalhackeo19@gmail.com",
]


PLANES_APP = {
    "gratis": {
        "modelo": "apis_gratis",
        "creditos_mes": 0,
        "creditos_dia": 0,
        "herramientas": [
            "chat_gratis",
            "imagen_basica",
        ],
    },
    "basico": {
        "modelo": "ia_basica",
        "creditos_mes": 3000,
        "creditos_dia": 100,
        "herramientas": [
            "chat_inteligente",
            "redactor",
            "traductor",
            "resumen",
            "corrector",
        ],
    },
    "pro": {
        "modelo": "ia_pro",
        "creditos_mes": 8000,
        "creditos_dia": 300,
        "herramientas": [
            "chat_inteligente",
            "redactor",
            "traductor",
            "resumen",
            "corrector",
            "programacion",
            "respuestas_largas",
            "analizar_imagen",
            "leer_captura",
            "resolver_tarea_foto",
            "estudio",
            "negocios",
        ],
    },
    "premium": {
        "modelo": "ia_premium",
        "creditos_mes": 18000,
        "creditos_dia": 700,
        "herramientas": [
            "chat_inteligente",
            "redactor",
            "traductor",
            "resumen",
            "corrector",
            "programacion",
            "respuestas_largas",
            "analizar_imagen",
            "leer_captura",
            "resolver_tarea_foto",
            "estudio",
            "negocios",
            "pdf",
            "word",
            "preguntas_documentos",
            "voz_a_texto",
            "texto_a_voz",
            "hablar_con_ia",
            "imagen_premium",
            "herramientas_completas",
        ],
    },
}


COSTO_HERRAMIENTA = {
    "chat_inteligente": 1,
    "redactor": 1,
    "traductor": 1,
    "resumen": 1,
    "corrector": 1,
    "programacion": 2,
    "respuestas_largas": 2,
    "analizar_imagen": 3,
    "leer_captura": 3,
    "resolver_tarea_foto": 3,
    "estudio": 2,
    "negocios": 2,
    "pdf": 5,
    "word": 5,
    "preguntas_documentos": 5,
    "voz_a_texto": 3,
    "texto_a_voz": 3,
    "hablar_con_ia": 5,
    "imagen_premium": 6,
    "herramientas_completas": 6,
}


def limpiar_email(email: str) -> str:
    return (email or "").strip().lower()


def ahora_utc() -> datetime:
    return datetime.now(timezone.utc)


def supabase_disponible() -> bool:
    return bool(SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY)


def supabase_headers() -> dict:
    return {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


def es_admin(email: str) -> bool:
    return limpiar_email(email) in OWNER_EMAILS


def respuesta_limite_temporal() -> dict:
    return {
        "ok": False,
        "codigo": "limite_temporal",
        "mensaje": "Has alcanzado el uso disponible por ahora. Puedes seguir usando el chat de CENTENO AI normalmente.",
    }


def respuesta_plan_superior() -> dict:
    return {
        "ok": False,
        "codigo": "plan_superior",
        "mensaje": "Disponible en un plan superior. Esta función usa IA avanzada. Actualiza tu plan para desbloquearla.",
    }


def respuesta_imagen_gratis_espera(proxima_dt: datetime) -> dict:
    ahora = ahora_utc()
    minutos = 40

    try:
        restante = proxima_dt - ahora
        minutos = max(1, int(restante.total_seconds() // 60) + 1)
    except Exception:
        minutos = 40

    return {
        "ok": False,
        "codigo": "espera_imagen_gratis",
        "minutos_espera": minutos,
        "mensaje": f"Has alcanzado el límite de generación de imágenes por ahora. Podrás volver a generar imágenes en {minutos} minutos. Mientras tanto, puedes seguir usando el chat de CENTENO AI normalmente.",
    }


def obtener_plan_usuario(email: str) -> dict | None:
    email = limpiar_email(email)

    if not email:
        return None

    if es_admin(email):
        return {
            "email": email,
            "plan_actual": "premium",
            "estado_plan": "activo",
            "modelo_permitido": "ia_premium",
            "creditos_mes": 999999999,
            "creditos_usados_mes": 0,
            "creditos_dia": 999999999,
            "creditos_usados_hoy": 0,
            "imagenes_gratis_usadas": 0,
            "proxima_imagen_gratis_at": None,
            "es_admin": True,
        }

    if not supabase_disponible():
        print("SUPABASE NO CONFIGURADO:", SUPABASE_URL, bool(SUPABASE_SERVICE_ROLE_KEY))
        return None

    try:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/usuarios_planes",
            headers=supabase_headers(),
            params={
                "email": f"eq.{email}",
                "select": "*",
                "limit": "1",
            },
            timeout=15,
        )

        if r.status_code not in [200, 206]:
            print("ERROR LEYENDO USUARIO_PLAN:", r.status_code, r.text)
            return None

        data = r.json()

        if isinstance(data, list) and len(data) > 0:
            return data[0]

        return None

    except Exception as e:
        print("EXCEPTION LEYENDO USUARIO_PLAN:", str(e))
        return None


def crear_usuario_plan_si_no_existe(email: str) -> dict | None:
    email = limpiar_email(email)

    if not email or email == "usuario@app.com":
        print("EMAIL NO VALIDO PARA USUARIO_PLAN:", email)
        return None

    if es_admin(email):
        return obtener_plan_usuario(email)

    usuario = obtener_plan_usuario(email)

    if usuario:
        return usuario

    if not supabase_disponible():
        print("NO SE PUEDE CREAR USUARIO_PLAN, SUPABASE NO CONFIGURADO")
        return None

    ahora = ahora_utc()

    payload = {
        "email": email,
        "plan_actual": "gratis",
        "estado_plan": "activo",
        "modelo_permitido": "apis_gratis",
        "fecha_inicio_plan": None,
        "fecha_fin_plan": None,
        "creditos_mes": 0,
        "creditos_usados_mes": 0,
        "creditos_dia": 0,
        "creditos_usados_hoy": 0,
        "imagenes_gratis_usadas": 0,
        "proxima_imagen_gratis_at": None,
        "ultimo_reset_dia": ahora.date().isoformat(),
        "es_admin": False,
        "updated_at": ahora.isoformat(),
    }

    try:
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/usuarios_planes",
            headers=supabase_headers(),
            json=payload,
            timeout=15,
        )

        if r.status_code not in [200, 201]:
            print("ERROR CREANDO USUARIO_PLAN:", r.status_code, r.text)
            return None

        data = r.json()

        if isinstance(data, list) and len(data) > 0:
            return data[0]

        return obtener_plan_usuario(email)

    except Exception as e:
        print("EXCEPTION CREANDO USUARIO_PLAN:", str(e))
        return None


def resetear_creditos_diarios_si_corresponde(usuario: dict) -> dict:
    if not usuario:
        return usuario

    email = limpiar_email(usuario.get("email", ""))

    if es_admin(email):
        return usuario

    if not supabase_disponible():
        return usuario

    hoy = ahora_utc().date().isoformat()
    ultimo_reset = str(usuario.get("ultimo_reset_dia") or "")

    if ultimo_reset == hoy:
        return usuario

    try:
        r = requests.patch(
            f"{SUPABASE_URL}/rest/v1/usuarios_planes?email=eq.{email}",
            headers=supabase_headers(),
            json={
                "creditos_usados_hoy": 0,
                "ultimo_reset_dia": hoy,
                "updated_at": ahora_utc().isoformat(),
            },
            timeout=15,
        )

        if r.status_code in [200, 204]:
            usuario["creditos_usados_hoy"] = 0
            usuario["ultimo_reset_dia"] = hoy
        else:
            print("ERROR RESET CREDITOS:", r.status_code, r.text)

    except Exception as e:
        print("EXCEPTION RESET CREDITOS:", str(e))

    return usuario


def plan_vencido(usuario: dict) -> bool:
    if not usuario:
        return False

    fecha_fin = usuario.get("fecha_fin_plan")

    if not fecha_fin:
        return False

    try:
        fecha_fin_dt = datetime.fromisoformat(str(fecha_fin).replace("Z", "+00:00"))
        return ahora_utc() > fecha_fin_dt
    except Exception:
        return False


def volver_a_gratis(email: str) -> dict | None:
    email = limpiar_email(email)

    if not email or es_admin(email):
        return obtener_plan_usuario(email)

    if not supabase_disponible():
        return None

    ahora = ahora_utc()

    try:
        r = requests.patch(
            f"{SUPABASE_URL}/rest/v1/usuarios_planes?email=eq.{email}",
            headers=supabase_headers(),
            json={
                "plan_actual": "gratis",
                "estado_plan": "activo",
                "modelo_permitido": "apis_gratis",
                "fecha_inicio_plan": None,
                "fecha_fin_plan": None,
                "creditos_mes": 0,
                "creditos_usados_mes": 0,
                "creditos_dia": 0,
                "creditos_usados_hoy": 0,
                "updated_at": ahora.isoformat(),
            },
            timeout=15,
        )

        if r.status_code not in [200, 204]:
            print("ERROR VOLVER A GRATIS:", r.status_code, r.text)

    except Exception as e:
        print("EXCEPTION VOLVER A GRATIS:", str(e))

    return obtener_plan_usuario(email)


def herramienta_permitida(usuario: dict, herramienta: str) -> bool:
    if not usuario:
        return False

    email = limpiar_email(usuario.get("email", ""))

    if es_admin(email) or bool(usuario.get("es_admin")):
        return True

    plan_actual = str(usuario.get("plan_actual") or "gratis").lower()
    config = PLANES_APP.get(plan_actual, PLANES_APP["gratis"])

    return herramienta in config.get("herramientas", [])


def descontar_creditos(email: str, herramienta: str) -> bool:
    email = limpiar_email(email)

    if es_admin(email):
        return True

    usuario = obtener_plan_usuario(email)

    if not usuario:
        usuario = crear_usuario_plan_si_no_existe(email)

    if not usuario:
        return False

    usuario = resetear_creditos_diarios_si_corresponde(usuario)

    plan_actual = str(usuario.get("plan_actual") or "gratis").lower()

    if plan_actual == "gratis":
        return True

    if plan_vencido(usuario):
        volver_a_gratis(email)
        return False

    costo = int(COSTO_HERRAMIENTA.get(herramienta, 1))

    creditos_mes = int(usuario.get("creditos_mes") or 0)
    creditos_dia = int(usuario.get("creditos_dia") or 0)
    usados_mes = int(usuario.get("creditos_usados_mes") or 0)
    usados_hoy = int(usuario.get("creditos_usados_hoy") or 0)

    if usados_mes + costo > creditos_mes:
        return False

    if usados_hoy + costo > creditos_dia:
        return False

    if not supabase_disponible():
        return False

    try:
        r = requests.patch(
            f"{SUPABASE_URL}/rest/v1/usuarios_planes?email=eq.{email}",
            headers=supabase_headers(),
            json={
                "creditos_usados_mes": usados_mes + costo,
                "creditos_usados_hoy": usados_hoy + costo,
                "updated_at": ahora_utc().isoformat(),
            },
            timeout=15,
        )

        if r.status_code not in [200, 204]:
            print("ERROR DESCONTANDO CREDITOS:", r.status_code, r.text)

        return r.status_code in [200, 204]

    except Exception as e:
        print("EXCEPTION DESCONTANDO CREDITOS:", str(e))
        return False


def validar_uso_ia(email: str, herramienta: str = "chat_inteligente") -> dict:
    email = limpiar_email(email)

    if es_admin(email):
        return {
            "ok": True,
            "plan": "premium",
            "modelo": "ia_premium",
            "admin": True,
            "mensaje": "Uso permitido",
        }

    usuario = obtener_plan_usuario(email)

    if not usuario:
        usuario = crear_usuario_plan_si_no_existe(email)

    if not usuario:
        return {
            "ok": False,
            "codigo": "usuario_no_creado",
            "mensaje": "No pudimos preparar tu cuenta. Intenta nuevamente en unos minutos.",
        }

    usuario = resetear_creditos_diarios_si_corresponde(usuario)

    if plan_vencido(usuario):
        usuario = volver_a_gratis(email)

    plan_actual = str(usuario.get("plan_actual") or "gratis").lower()

    if not herramienta_permitida(usuario, herramienta):
        return respuesta_plan_superior()

    if plan_actual != "gratis":
        if not descontar_creditos(email, herramienta):
            return respuesta_limite_temporal()

    modelo = PLANES_APP.get(plan_actual, PLANES_APP["gratis"]).get("modelo", "apis_gratis")

    return {
        "ok": True,
        "plan": plan_actual,
        "modelo": modelo,
        "mensaje": "Uso permitido",
    }


def activar_plan_app(email: str, plan: str, dias: int = 30) -> dict:
    email = limpiar_email(email)
    plan = str(plan or "").strip().lower()

    if not email:
        return {
            "ok": False,
            "mensaje": "Email no válido",
        }

    if plan not in ["basico", "pro", "premium"]:
        return {
            "ok": False,
            "mensaje": "Plan no válido",
        }

    if not supabase_disponible():
        return {
            "ok": False,
            "mensaje": "Supabase no configurado",
        }

    config = PLANES_APP[plan]
    ahora = ahora_utc()
    fecha_fin = ahora + timedelta(days=dias)

    payload = {
        "email": email,
        "plan_actual": plan,
        "estado_plan": "activo",
        "modelo_permitido": config["modelo"],
        "fecha_inicio_plan": ahora.isoformat(),
        "fecha_fin_plan": fecha_fin.isoformat(),
        "creditos_mes": config["creditos_mes"],
        "creditos_usados_mes": 0,
        "creditos_dia": config["creditos_dia"],
        "creditos_usados_hoy": 0,
        "ultimo_reset_dia": ahora.date().isoformat(),
        "es_admin": es_admin(email),
        "updated_at": ahora.isoformat(),
    }

    try:
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/usuarios_planes",
            headers={
                **supabase_headers(),
                "Prefer": "resolution=merge-duplicates,return=representation",
            },
            json=payload,
            timeout=15,
        )

        if r.status_code not in [200, 201]:
            print("ERROR ACTIVANDO PLAN:", r.status_code, r.text)
            return {
                "ok": False,
                "mensaje": "No se pudo activar el plan",
                "detalle": r.text,
            }

        return {
            "ok": True,
            "email": email,
            "plan": plan,
            "fecha_fin_plan": fecha_fin.isoformat(),
            "mensaje": "Plan activado correctamente",
        }

    except Exception as e:
        print("EXCEPTION ACTIVANDO PLAN:", str(e))
        return {
            "ok": False,
            "mensaje": "Error activando plan",
            "detalle": str(e),
        }


def controlar_imagen_gratis(email: str) -> dict:
    """
    Control real de imágenes:
    - Admins ilimitados.
    - Usuario normal debe existir o crearse en usuarios_planes.
    - Gratis: 10 imágenes, luego espera 40 minutos.
    - Si no puede leer/guardar contador, bloquea imagen para evitar ilimitado gratis.
    """
    email = limpiar_email(email)

    if not email or email == "usuario@app.com":
        return {
            "ok": False,
            "codigo": "email_no_valido",
            "mensaje": "No pudimos reconocer tu cuenta. Cierra sesión e inicia sesión nuevamente.",
        }

    if es_admin(email):
        return {
            "ok": True,
            "admin": True,
            "plan": "premium",
            "mensaje": "Imagen permitida",
        }

    if not supabase_disponible():
        print("CONTROL IMAGEN: SUPABASE NO DISPONIBLE")
        return {
            "ok": False,
            "codigo": "supabase_no_configurado",
            "mensaje": "No pudimos validar tu uso de imágenes por ahora. Intenta nuevamente en unos minutos.",
        }

    usuario = obtener_plan_usuario(email)

    if not usuario:
        usuario = crear_usuario_plan_si_no_existe(email)

    if not usuario:
        print("CONTROL IMAGEN: USUARIO_PLAN NO CREADO:", email)
        return {
            "ok": False,
            "codigo": "usuario_plan_no_creado",
            "mensaje": "No pudimos preparar tu cuenta para generar imágenes. Intenta nuevamente en unos minutos.",
        }

    plan_actual = str(usuario.get("plan_actual") or "gratis").lower()
    es_admin_db = bool(usuario.get("es_admin") or False)

    if es_admin_db or plan_actual in ["basico", "pro", "premium"]:
        return {
            "ok": True,
            "plan": plan_actual,
            "mensaje": "Imagen permitida",
        }

    ahora = ahora_utc()
    proxima = usuario.get("proxima_imagen_gratis_at")

    if proxima:
        try:
            proxima_dt = datetime.fromisoformat(str(proxima).replace("Z", "+00:00"))
            if ahora < proxima_dt:
                return respuesta_imagen_gratis_espera(proxima_dt)
        except Exception:
            pass

    usadas = int(usuario.get("imagenes_gratis_usadas") or 0)

    if usadas >= 10:
        proxima_dt = ahora + timedelta(minutes=40)

        try:
            r = requests.patch(
                f"{SUPABASE_URL}/rest/v1/usuarios_planes?email=eq.{email}",
                headers=supabase_headers(),
                json={
                    "imagenes_gratis_usadas": 0,
                    "proxima_imagen_gratis_at": proxima_dt.isoformat(),
                    "updated_at": ahora.isoformat(),
                },
                timeout=15,
            )

            if r.status_code not in [200, 204]:
                print("ERROR ACTUALIZANDO ESPERA IMAGEN:", r.status_code, r.text)

        except Exception as e:
            print("EXCEPTION ACTUALIZANDO ESPERA IMAGEN:", str(e))

        return respuesta_imagen_gratis_espera(proxima_dt)

    nuevo_total = usadas + 1

    try:
        r = requests.patch(
            f"{SUPABASE_URL}/rest/v1/usuarios_planes?email=eq.{email}",
            headers=supabase_headers(),
            json={
                "imagenes_gratis_usadas": nuevo_total,
                "updated_at": ahora.isoformat(),
            },
            timeout=15,
        )

        if r.status_code not in [200, 204]:
            print("ERROR ACTUALIZANDO LIMITE IMAGEN:", r.status_code, r.text)
            return {
                "ok": False,
                "codigo": "no_se_pudo_actualizar_limite",
                "mensaje": "No pudimos validar tu límite de imágenes por ahora. Intenta nuevamente en unos minutos.",
            }

    except Exception as e:
        print("EXCEPTION ACTUALIZANDO LIMITE IMAGEN:", str(e))
        return {
            "ok": False,
            "codigo": "error_actualizando_limite",
            "mensaje": "No pudimos validar tu límite de imágenes por ahora. Intenta nuevamente en unos minutos.",
        }

    return {
        "ok": True,
        "plan": "gratis",
        "imagenes_usadas": nuevo_total,
        "imagenes_restantes": max(0, 10 - nuevo_total),
        "mensaje": "Imagen permitida",
    }
