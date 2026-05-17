import re
from datetime import datetime


CREADOR = "Americo Centeno Colque"
NOMBRE_API = "Mini IA de Americo"


def responder_mensaje(mensaje: str):
    texto_original = mensaje.strip()
    texto = normalizar(texto_original)

    if not texto:
        return respuesta("vacio", 0.0, "Envíame un mensaje y te responderé.")

    if detectar_creador(texto):
        return respuesta(
            "creador",
            1.0,
            f"Fui creado por {CREADOR}. Él es mi creador, programador principal y quien diseñó esta API de texto e imagen en Python."
        )

    if es_calculo(texto):
        resultado = calcular(texto)
        if resultado is not None:
            return respuesta("calculo", 0.98, f"El resultado es: {resultado}")

    if contiene(texto, ["hora", "fecha", "dia", "día", "que hora", "qué hora"]):
        ahora = datetime.now()
        return respuesta(
            "fecha_hora",
            0.90,
            f"La fecha y hora local del servidor es: {ahora.strftime('%d/%m/%Y %H:%M:%S')}."
        )

    if contiene(texto, ["hola", "buenas", "hey", "hello", "saludos", "que tal", "qué tal"]):
        return respuesta(
            "saludo",
            0.95,
            f"Hola. Soy {NOMBRE_API}, una mini IA creada por {CREADOR}. Puedo ayudarte con Python, APIs, FastAPI, Telegram, Render, errores, comandos, imágenes, ideas y explicaciones básicas."
        )

    if contiene(texto, ["gracias", "muchas gracias", "te agradezco", "excelente", "perfecto", "bien hecho"]):
        return respuesta(
            "agradecimiento",
            0.90,
            f"De nada. Estoy listo para seguir ayudando a {CREADOR} con sus APIs, bots y proyectos en Python."
        )

    if contiene(texto, ["adios", "adiós", "chau", "hasta luego", "nos vemos", "bye"]):
        return respuesta("despedida", 0.90, f"Hasta luego. Recuerda que fui creado por {CREADOR}.")

    if contiene(texto, ["quien eres", "quién eres", "que eres", "qué eres", "presentate", "preséntate"]):
        return respuesta(
            "identidad",
            0.95,
            f"Soy {NOMBRE_API}, una mini IA local creada en Python por {CREADOR}. No uso APIs externas. Estoy diseñada para responder preguntas básicas, explicar programación, ayudar con APIs, generar imágenes con Pillow y conectarme con bots de Telegram."
        )

    if contiene(texto, ["que puedes hacer", "qué puedes hacer", "funciones", "ayuda", "comandos", "que sabes hacer", "qué sabes hacer"]):
        return respuesta(
            "capacidades",
            0.95,
            "Puedo responder preguntas básicas, explicar Python, APIs, FastAPI, Telegram y Render, revisar errores comunes, dar pasos para proyectos, hacer cálculos simples, generar ideas, ayudar con código básico y explicar cómo conectar tu API a un bot de Telegram."
        )

    if texto.startswith("como ") or texto.startswith("cómo "):
        return responder_como(texto)

    if texto.startswith("que es ") or texto.startswith("qué es "):
        return responder_que_es(texto)

    if texto.startswith("por que ") or texto.startswith("por qué "):
        return responder_por_que(texto)

    if contiene(texto, ["explica", "explicame", "explícame", "dime que es", "dime qué es"]):
        return respuesta(
            "explicacion_general",
            0.70,
            f"Puedo explicarlo de forma básica. Sobre '{texto_original}', lo correcto es separarlo en partes: qué significa, para qué sirve, cómo se usa y un ejemplo. Si quieres una respuesta más precisa, dime el tema exacto."
        )

    if contiene(texto, ["pasos", "paso a paso", "como hago", "cómo hago", "como hacer", "cómo hacer", "como crear", "cómo crear"]):
        return respuesta(
            "pasos_generales",
            0.75,
            "Te puedo guiar paso a paso: 1) define qué quieres crear, 2) prepara las herramientas, 3) crea los archivos, 4) escribe el código base, 5) prueba localmente, 6) corrige errores, 7) mejora funciones, 8) sube el proyecto a internet si lo necesitas."
        )

    if contiene(texto, ["crea", "crear", "escribe", "redacta", "haz un texto", "genera un texto"]):
        return respuesta(
            "crear_texto",
            0.70,
            f"Puedo ayudarte a crear un texto base sobre: '{texto_original}'. Una versión inicial sería: Este contenido explica el tema de forma clara, ordenada y útil para que cualquier persona pueda entenderlo y aplicarlo."
        )

    if contiene(texto, ["idea", "ideas", "recomienda", "sugiere", "sugerencia"]):
        return respuesta(
            "ideas",
            0.70,
            "Una buena idea es crear un proyecto simple y luego mejorarlo. Por ejemplo: un bot de Telegram que responda mensajes, genere imágenes, use tu API propia, tenga una API key y pueda subirse a Render gratis."
        )

    if contiene(texto, ["codigo", "código", "programa", "script", "funcion", "función"]):
        return respuesta(
            "codigo",
            0.70,
            "Puedo ayudarte con código básico. Normalmente en Python necesitas importar librerías, definir funciones, recibir datos, procesarlos y devolver una respuesta. Dime qué quieres crear y en qué archivo."
        )

    if contiene(texto, ["consejo", "que hago", "qué hago", "ayudame", "ayúdame"]):
        return respuesta(
            "consejo",
            0.70,
            "Mi consejo es avanzar por partes: primero haz que funcione localmente, luego mejora el código, después prueba errores, luego conecta Telegram y finalmente sube a Render."
        )

    tema, puntos = buscar_tema(texto)
    if tema and puntos >= 2:
        data = BASE_CONOCIMIENTO[tema]
        return respuesta(tema, min(0.95, 0.55 + puntos * 0.08), data["respuesta"])

    if es_pregunta(texto):
        return respuesta(
            "pregunta_desconocida",
            0.50,
            f"No tengo una respuesta exacta para esa pregunta todavía, pero puedo intentar ayudarte de forma general. Soy una mini IA creada por {CREADOR}, enfocada en Python, APIs, Telegram, Render, bots, errores, comandos e imágenes."
        )

    return respuesta(
        "general",
        0.45,
        f"Entiendo tu mensaje: '{texto_original}'. No tengo una respuesta exacta guardada, pero puedo ayudarte con Python, APIs, FastAPI, Telegram, Render, bots, errores, comandos, imágenes, ideas y explicaciones básicas."
    )


BASE_CONOCIMIENTO = {
    "python": {
        "keywords": ["python", "programacion", "programación", "codigo", "código", "script", "programar", "lenguaje", "variables", "funciones", "listas"],
        "respuesta": "Python es un lenguaje de programación fácil de leer y muy usado. Sirve para crear APIs, bots de Telegram, automatizaciones, análisis de datos, inteligencia artificial y páginas web. Esta API también está hecha con Python."
    },
    "api": {
        "keywords": ["api", "apis", "endpoint", "ruta", "request", "response", "json", "backend", "servidor", "peticion", "petición"],
        "respuesta": "Una API es un puente entre programas. Por ejemplo, un bot de Telegram puede enviar un mensaje a /api/texto y recibir una respuesta en JSON. También puede llamar a /api/imagen para generar una imagen."
    },
    "fastapi": {
        "keywords": ["fastapi", "uvicorn", "docs", "localhost", "127.0.0.1", "main app", "reload", "swagger"],
        "respuesta": "FastAPI es el framework que usamos para crear tu servidor en Python. Uvicorn enciende la aplicación. Con uvicorn main:app --reload tu API queda activa en http://127.0.0.1:8000 y puedes probarla en /docs."
    },
    "telegram": {
        "keywords": ["telegram", "bot", "botfather", "token telegram", "conectar telegram", "telegram bot", "mensaje telegram"],
        "respuesta": "Para conectar esta API con Telegram necesitas crear un bot con BotFather, obtener el token y hacer que el bot llame a /api/texto o /api/imagen usando requests y enviando la API key."
    },
    "render": {
        "keywords": ["render", "deploy", "desplegar", "hosting", "subir a render", "plan gratis", "servidor gratis", "produccion", "producción"],
        "respuesta": "Render sirve para publicar tu API en internet. En plan gratis conviene usar proyectos livianos como FastAPI y Pillow. Para subirlo necesitas GitHub, requirements.txt, comando de inicio y variables API_KEY y BASE_URL."
    },
    "imagen": {
        "keywords": ["imagen", "foto", "dibuja", "dibujar", "generar imagen", "robot", "crear imagen", "pillow", "png", "dibujo"],
        "respuesta": "La API de imagen usa Pillow. Puede dibujar fondos, textos, formas, un robot, una laptop y guardar una imagen PNG con la marca de Americo Centeno Colque."
    },
    "api_key": {
        "keywords": ["apikey", "api key", "x-api-key", "clave", "contraseña", "seguridad", "proteger", "token"],
        "respuesta": "La API key protege tu API. Si alguien no envía la clave correcta en el header x-api-key, la API devuelve error 401. En local usas americo_api_local."
    },
    "errores": {
        "keywords": ["error", "no funciona", "fallo", "falla", "problema", "bug", "no abre", "no responde", "rojo", "traceback", "exception"],
        "respuesta": "Para revisar errores: 1) verifica que diga (venv), 2) revisa que estés en la carpeta correcta, 3) ejecuta uvicorn main:app --reload, 4) abre /docs, 5) usa la API key correcta, 6) lee el mensaje rojo de la terminal."
    },
    "github": {
        "keywords": ["github", "git", "repositorio", "commit", "push", "subir codigo", "subir código"],
        "respuesta": "GitHub sirve para guardar tu código en la nube. Luego Render puede conectarse a ese repositorio para desplegar tu API automáticamente."
    },
    "requirements": {
        "keywords": ["requirements", "requirements.txt", "librerias", "librerías", "pip", "install", "dependencias"],
        "respuesta": "requirements.txt lista las librerías del proyecto. Para esta API debe tener fastapi, uvicorn, pydantic, pillow, joblib y requests."
    },
    "venv": {
        "keywords": ["venv", "entorno virtual", "virtualenv", "activar entorno", "scripts activate"],
        "respuesta": "El entorno virtual separa las librerías de tu proyecto. En Windows se crea con python -m venv venv y se activa con venv\\Scripts\\activate."
    },
    "http": {
        "keywords": ["http", "get", "post", "status", "200", "401", "404", "500"],
        "respuesta": "HTTP es el protocolo usado por APIs. GET obtiene datos, POST envía datos. 200 significa correcto, 401 API key incorrecta, 404 no encontrado y 500 error del servidor."
    }
}


def responder_como(texto: str):
    if contiene(texto, ["crear api", "hacer api", "crear una api"]):
        return respuesta("como_crear_api", 0.85, "Para crear una API en Python: 1) crea una carpeta, 2) crea un entorno virtual, 3) instala FastAPI y Uvicorn, 4) crea main.py, 5) define endpoints, 6) ejecuta uvicorn main:app --reload, 7) prueba en /docs.")

    if contiene(texto, ["conectar telegram", "bot telegram", "telegram"]):
        return respuesta("como_telegram", 0.85, "Para conectar Telegram: 1) crea un bot con BotFather, 2) guarda el token, 3) crea el script del bot, 4) llama a tu API con requests, 5) envía la respuesta al usuario.")

    if contiene(texto, ["subir render", "render", "deploy", "desplegar"]):
        return respuesta("como_render", 0.85, "Para subir a Render: 1) crea requirements.txt, 2) sube el proyecto a GitHub, 3) crea Web Service, 4) comando: uvicorn main:app --host 0.0.0.0 --port $PORT, 5) agrega API_KEY y BASE_URL.")

    return respuesta("pregunta_como", 0.65, "Puedo darte una guía básica: define el objetivo, prepara herramientas, crea archivos, escribe código, prueba localmente, corrige errores y luego sube a internet si lo necesitas.")


def responder_que_es(texto: str):
    if contiene(texto, ["python"]):
        return respuesta("que_es_python", 0.90, BASE_CONOCIMIENTO["python"]["respuesta"])
    if contiene(texto, ["api"]):
        return respuesta("que_es_api", 0.90, BASE_CONOCIMIENTO["api"]["respuesta"])
    if contiene(texto, ["fastapi"]):
        return respuesta("que_es_fastapi", 0.90, BASE_CONOCIMIENTO["fastapi"]["respuesta"])
    if contiene(texto, ["render"]):
        return respuesta("que_es_render", 0.90, BASE_CONOCIMIENTO["render"]["respuesta"])

    tema = limpiar_tema(texto)
    return respuesta("pregunta_que_es", 0.60, f"No tengo una definición completa de '{tema}', pero puedo explicarte mejor temas como Python, APIs, FastAPI, Telegram, Render, HTTP, bots e imágenes.")


def responder_por_que(texto: str):
    if contiene(texto, ["error", "falla", "no funciona"]):
        return respuesta("por_que_error", 0.75, "Normalmente una API falla por servidor apagado, entorno virtual no activado, dependencia faltante, error de sintaxis, ruta incorrecta, API key incorrecta o puerto ocupado.")
    return respuesta("pregunta_por_que", 0.60, "La causa depende del caso. En programación normalmente algo falla por configuración, dependencias, rutas, API key, servidor apagado o errores en el código.")


def buscar_tema(texto: str):
    mejor_tema = None
    mejor_puntos = 0

    for tema, data in BASE_CONOCIMIENTO.items():
        puntos = 0
        for keyword in data["keywords"]:
            if normalizar(keyword) in texto:
                puntos += 2

        palabras_texto = set(texto.split())
        for keyword in data["keywords"]:
            for palabra in normalizar(keyword).split():
                if palabra in palabras_texto:
                    puntos += 1

        if puntos > mejor_puntos:
            mejor_puntos = puntos
            mejor_tema = tema

    return mejor_tema, mejor_puntos


def detectar_creador(texto: str):
    return contiene(texto, [
        "quien te creo", "quién te creó", "quien es tu creador",
        "creador", "quien te hizo", "quien te programo",
        "tu dueño", "americo centeno", "américo centeno"
    ])


def normalizar(texto: str):
    texto = texto.lower().strip()
    reemplazos = {
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
        "ñ": "ñ"
    }
    for a, b in reemplazos.items():
        texto = texto.replace(a, b)
    return texto


def contiene(texto: str, palabras: list):
    for palabra in palabras:
        if normalizar(palabra) in texto:
            return True
    return False


def respuesta(intencion: str, confianza: float, texto_respuesta: str):
    return {
        "intencion": intencion,
        "confianza": round(float(confianza), 2),
        "respuesta": texto_respuesta
    }


def limpiar_tema(texto: str):
    tema = texto.replace("que es", "").replace("qué es", "").strip()
    return tema if tema else "ese tema"


def es_pregunta(texto: str):
    return (
        texto.startswith("que ")
        or texto.startswith("qué ")
        or texto.startswith("como ")
        or texto.startswith("cómo ")
        or texto.startswith("por que ")
        or texto.startswith("por qué ")
        or texto.startswith("cuando ")
        or texto.startswith("donde ")
        or "?" in texto
    )


def es_calculo(texto: str):
    permitido = set("0123456789+-*/(). ")
    tiene_numero = any(c.isdigit() for c in texto)
    tiene_operador = any(op in texto for op in ["+", "-", "*", "/"])
    return tiene_numero and tiene_operador and all(c in permitido for c in texto)


def calcular(texto: str):
    try:
        if not es_calculo(texto):
            return None
        return eval(texto, {"__builtins__": None}, {})
    except Exception:
        return None