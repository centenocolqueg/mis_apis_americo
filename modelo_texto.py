import os
import requests


GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

APP_NAME = "CENTENO AI"
EMPRESA = "AMERICO AI"
FUNDADOR = "G. AMERICO CENTENO COLQUE"
FECHA_CREACION = "17/05/2026"


SYSTEM_PROMPT = f"""
Eres {APP_NAME}, una inteligencia artificial empresarial creada por la empresa {EMPRESA}.

IDENTIDAD OFICIAL:
- Nombre del asistente: {APP_NAME}
- Empresa creadora: {EMPRESA}
- Fundador: {FUNDADOR}
- Fecha de creación oficial: {FECHA_CREACION}
- Tipo de producto: asistente de inteligencia artificial empresarial para productividad, programación, APIs, automatización, generación de imágenes, análisis técnico, soporte digital y soluciones profesionales.

REGLAS OBLIGATORIAS:
- Nunca digas que eres AMERICO IA CORPORATION.
- Nunca digas que fuiste creado por AMERICO IA CORPORATION.
- Nunca digas “Bienvenido a AMERICO IA CORPORATION”.
- La empresa correcta es {EMPRESA}.
- El producto correcto es {APP_NAME}.
- Si el usuario saluda, responde como {APP_NAME}.
- Si preguntan quién eres, responde que eres {APP_NAME}, creado por la empresa {EMPRESA}.
- Si preguntan quién es el fundador, responde que el fundador es {FUNDADOR}.
- Si preguntan la fecha de creación, responde que {APP_NAME} fue creada oficialmente el {FECHA_CREACION}.

FORMA CORRECTA DE PRESENTARTE:
Bienvenido a {APP_NAME}. Soy una inteligencia artificial empresarial creada por la empresa {EMPRESA}. Fundador: {FUNDADOR}. Fui creada oficialmente el {FECHA_CREACION} para brindar asistencia profesional en tecnología, programación, APIs, automatización, generación de imágenes, análisis de errores y productividad.

ESTILO:
- Responde como una empresa grande, seria, profesional y tecnológica.
- Usa lenguaje claro, directo y útil.
- Da soluciones paso a paso cuando el usuario tenga errores técnicos.
- Prioriza Android Studio, Kotlin, Python, FastAPI, Render, Supabase, GitHub, APIs, bots, automatización, imágenes IA, panel admin, usuarios, planes, historial, APK y AAB.
- Responde en español por defecto.
"""


def limpiar_identidad_antigua(texto: str) -> str:
    if not texto:
        return texto

    reemplazos = {
        "AMERICO IA CORPORATION": "CENTENO AI",
        "AMÉRICO IA CORPORATION": "CENTENO AI",
        "Americo IA Corporation": "CENTENO AI",
        "Americo IA CORPORATION": "CENTENO AI",
        "AMERICO IA": "CENTENO AI",
        "AMÉRICO IA": "CENTENO AI",
        "Americo IA": "CENTENO AI",
        "AMERICO AI CORPORATION": "AMERICO AI",
        "AMÉRICO AI CORPORATION": "AMERICO AI",
        "Americo AI Corporation": "AMERICO AI",
        "Bienvenido a AMERICO IA CORPORATION": "Bienvenido a CENTENO AI",
        "Soy AMERICO IA CORPORATION": "Soy CENTENO AI",
        "fui creado por AMERICO IA CORPORATION": f"fui creado por la empresa {EMPRESA}",
        "fui creada por AMERICO IA CORPORATION": f"fui creada por la empresa {EMPRESA}",
        "creado por AMERICO IA CORPORATION": f"creado por la empresa {EMPRESA}",
        "creada por AMERICO IA CORPORATION": f"creada por la empresa {EMPRESA}",
        "Americo Centeno Colque": FUNDADOR,
        "G. Americo Centeno colque": FUNDADOR,
        "G. americo Centeno colque": FUNDADOR,
    }

    for viejo, nuevo in reemplazos.items():
        texto = texto.replace(viejo, nuevo)

    return texto


def respuesta_bienvenida() -> str:
    return (
        f"Bienvenido a {APP_NAME}. Soy una inteligencia artificial empresarial creada por la empresa {EMPRESA}. "
        f"Fundador: {FUNDADOR}. Fui creada oficialmente el {FECHA_CREACION} para brindar asistencia profesional "
        "en programación, APIs, automatización, generación de imágenes, análisis de errores, productividad y soluciones tecnológicas.\n\n"
        "Estoy listo para ayudarte con proyectos de nivel empresarial, desarrollo Android, Kotlin, Python, FastAPI, Supabase, Render, GitHub, bots, paneles administrativos, sistemas conectados por API y herramientas de productividad."
    )


def respuesta_identidad() -> str:
    return (
        f"Soy {APP_NAME}, una inteligencia artificial empresarial creada por la empresa {EMPRESA}. "
        f"Fundador: {FUNDADOR}. Mi fecha de creación oficial es {FECHA_CREACION}. "
        "Fui diseñada para brindar asistencia profesional en tecnología, programación, APIs, automatización, generación de imágenes, análisis de errores, productividad y soluciones empresariales."
    )


def respuesta_fundador() -> str:
    return (
        f"El fundador de {EMPRESA} y creador oficial de {APP_NAME} es {FUNDADOR}. "
        f"{APP_NAME} fue creada oficialmente el {FECHA_CREACION} como una solución empresarial de inteligencia artificial."
    )


def respuesta_fecha() -> str:
    return (
        f"{APP_NAME} fue creada oficialmente el {FECHA_CREACION}. "
        f"Es una inteligencia artificial empresarial creada por la empresa {EMPRESA}. Fundador: {FUNDADOR}."
    )


def respuesta_imagen() -> str:
    return (
        f"Sí. En {APP_NAME} puedes generar imágenes con IA desde la app usando el botón + o escribiendo una instrucción como: "
        "“crea una imagen de un gato futurista”. También puedo ayudarte a mejorar prompts para obtener imágenes más profesionales."
    )


def respuesta_tecnica() -> str:
    return (
        f"Perfecto. {APP_NAME} puede ayudarte a resolver eso a nivel técnico y empresarial. "
        "Pásame el error exacto, captura o código, y te daré una solución directa paso a paso para Android Studio, Kotlin, Python, FastAPI, Render, Supabase, GitHub, APIs, bots, panel admin, historial o conexión con backend."
    )


def respuesta_general() -> str:
    return (
        f"Soy {APP_NAME}, inteligencia artificial empresarial creada por {EMPRESA}. "
        f"Fundador: {FUNDADOR}. Estoy preparado para ayudarte con soluciones profesionales en programación, APIs, automatización, imágenes IA, productividad, análisis de errores, aplicaciones Android, backend, Supabase, Render y proyectos tecnológicos de nivel empresarial."
    )


def detectar_intencion(mensaje: str) -> str:
    m = (mensaje or "").lower().strip()

    if not m:
        return "vacio"

    saludos = [
        "hola",
        "ola",
        "hello",
        "buenas",
        "buenos dias",
        "buenos días",
        "buenas tardes",
        "buenas noches",
        "hi"
    ]

    if m in saludos:
        return "saludo"

    if "quien eres" in m or "quién eres" in m or "que eres" in m or "qué eres" in m:
        return "identidad"

    if "fundador" in m or "ceo" in m or "dueño" in m or "dueno" in m or "creador" in m:
        return "fundador"

    if "fecha" in m and ("creado" in m or "creada" in m or "creación" in m or "creacion" in m):
        return "fecha_creacion"

    if "cuando fue creado" in m or "cuándo fue creado" in m or "cuando se creo" in m or "cuándo se creó" in m:
        return "fecha_creacion"

    if "imagen" in m or "foto" in m or "dibujo" in m or "generar imagen" in m or "crea una imagen" in m:
        return "imagen"

    palabras_tecnicas = [
        "api",
        "python",
        "fastapi",
        "supabase",
        "render",
        "android",
        "android studio",
        "kotlin",
        "github",
        "firebase",
        "gradle",
        "mainactivity",
        "backend",
        "endpoint",
        "bot",
        "telegram",
        "apk",
        "aab",
        "error",
        "código",
        "codigo",
        "programación",
        "programacion"
    ]

    for palabra in palabras_tecnicas:
        if palabra in m:
            return "tecnico"

    return "general"


def respuesta_local(mensaje: str):
    intencion = detectar_intencion(mensaje)

    if intencion == "vacio":
        respuesta = "Escribe un mensaje para poder ayudarte."
        confianza = 0.0

    elif intencion == "saludo":
        respuesta = respuesta_bienvenida()
        confianza = 0.95

    elif intencion == "identidad":
        respuesta = respuesta_identidad()
        confianza = 0.95

    elif intencion == "fundador":
        respuesta = respuesta_fundador()
        confianza = 0.95

    elif intencion == "fecha_creacion":
        respuesta = respuesta_fecha()
        confianza = 0.9

    elif intencion == "imagen":
        respuesta = respuesta_imagen()
        confianza = 0.85

    elif intencion == "tecnico":
        respuesta = respuesta_tecnica()
        confianza = 0.85

    else:
        respuesta = respuesta_general()
        confianza = 0.75

    return {
        "intencion": intencion,
        "confianza": confianza,
        "respuesta": limpiar_identidad_antigua(respuesta)
    }


def responder_con_groq(mensaje: str):
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": mensaje
            }
        ],
        "temperature": 0.35,
        "max_tokens": 1000
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=45
    )

    return response


def responder_mensaje(mensaje: str):
    mensaje = (mensaje or "").strip()

    if not mensaje:
        return {
            "intencion": "vacio",
            "confianza": 0.0,
            "respuesta": "Escribe un mensaje para poder ayudarte."
        }

    intencion = detectar_intencion(mensaje)

    if intencion in ["saludo", "identidad", "fundador", "fecha_creacion"]:
        return respuesta_local(mensaje)

    if not GROQ_API_KEY:
        return respuesta_local(mensaje)

    try:
        response = responder_con_groq(mensaje)

        if response.status_code not in [200, 201]:
            local = respuesta_local(mensaje)
            local["respuesta"] = (
                f"{local['respuesta']}\n\n"
                f"Nota técnica: no se pudo conectar correctamente con el modelo IA externo. Código: {response.status_code}"
            )
            local["intencion"] = "error_groq"
            local["confianza"] = 0.4
            return local

        data = response.json()
        respuesta = data["choices"][0]["message"]["content"].strip()
        respuesta = limpiar_identidad_antigua(respuesta)

        if not respuesta:
            local = respuesta_local(mensaje)
            local["intencion"] = "respuesta_vacia"
            local["confianza"] = 0.5
            return local

        return {
            "intencion": "chat",
            "confianza": 0.95,
            "respuesta": respuesta
        }

    except Exception as e:
        local = respuesta_local(mensaje)
        local["respuesta"] = (
            f"{local['respuesta']}\n\n"
            f"Nota técnica: hubo un error procesando la respuesta IA: {str(e)}"
        )
        local["intencion"] = "error"
        local["confianza"] = 0.4
        return local