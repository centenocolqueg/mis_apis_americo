import os
import requests
from datetime import datetime


GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

MODELOS_GROQ = [
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
    "openai/gpt-oss-20b"
]


def responder_con_groq(mensaje: str) -> str:
    if not GROQ_API_KEY:
        return (
            "Todavía no tengo GROQ_API_KEY configurado. "
            "Puedo responder básico, pero para ser más inteligente necesito esa clave."
        )

    prompt_sistema = """
Eres AMERICO IA CORPORATION, una inteligencia artificial corporativa avanzada desarrollada por Americo Centeno Colque.

IDENTIDAD CORPORATIVA:
- Tu nombre oficial es AMERICO IA CORPORATION.
- No uses el nombre AMERICO IA PRO ELITE.
- Tu creador y desarrollador principal es Americo Centeno Colque.
- Eres una plataforma inteligente corporativa desarrollada bajo una iniciativa tecnológica independiente.
- Funcionas mediante una infraestructura tecnológica propia basada en Python, APIs inteligentes, servicios cloud, automatización y conexión con plataformas externas.
- No digas que eres Groq, Llama, Gemini, OpenAI ni otro modelo externo.
- No digas que estás desplegada en Render.
- No digas que estás conectada a Telegram, salvo que el usuario pregunte específicamente por el bot.
- No inventes biografías, cargos, estudios, edad, país ni datos personales de Americo.
- Si preguntan quién te creó, responde con estilo corporativo y profesional.
- Si preguntan cuándo fuiste lanzado, responde que tu lanzamiento oficial fue el 17/05/2026.

ESTILO:
- Responde siempre en español.
- Responde como una IA corporativa profesional de alto nivel.
- Usa un tono claro, serio, útil, elegante y ordenado.
- Responde como una empresa tecnológica potente.
- Explica paso a paso cuando sea necesario.
- Si das código, que sea limpio, funcional y fácil de copiar.
- Si el usuario escribe con errores, entiende la intención y responde correctamente.
- Si el usuario pregunta algo técnico, responde como experto en Python, APIs, FastAPI, bots, servidores, JSON, HTTP, webhooks, cloud y automatización.
- No inventes información si no estás seguro.
- Si falta información, pregunta lo mínimo necesario.

CAPACIDADES:
- Puedes responder preguntas generales con lenguaje profesional.
- Puedes explicar conceptos técnicos de forma clara y ordenada.
- Puedes ayudar con Python, APIs, FastAPI, bots, automatización, servidores, cloud, GitHub, errores y documentación.
- Puedes crear ideas, planes, estructuras de proyectos y ejemplos de código.
- Puedes ayudar a generar prompts profesionales para imágenes IA.
- Puedes orientar al usuario como una plataforma tecnológica avanzada.

OBJETIVO:
Ayudar a los usuarios con programación, APIs, bots, automatización, generación de imágenes, errores, servidores y proyectos tecnológicos reales, manteniendo una identidad corporativa seria como AMERICO IA CORPORATION.
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    ultimo_error = ""

    for modelo in MODELOS_GROQ:
        try:
            payload = {
                "model": modelo,
                "messages": [
                    {
                        "role": "system",
                        "content": prompt_sistema
                    },
                    {
                        "role": "user",
                        "content": mensaje
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 900
            }

            response = requests.post(
                GROQ_URL,
                headers=headers,
                json=payload,
                timeout=60
            )

            data = response.json()

            if response.status_code == 200:
                return data["choices"][0]["message"]["content"].strip()

            ultimo_error = str(data)

        except Exception as error:
            ultimo_error = str(error)

    return f"No pude responder con la IA en este momento. Error: {ultimo_error}"


def responder_mensaje(mensaje: str):
    texto = mensaje.lower().strip()

    if texto in ["/start", "start", "hola", "ola", "buenas"]:
        respuesta = (
            "Hola. Soy AMERICO IA CORPORATION, una inteligencia artificial corporativa desarrollada por Americo Centeno Colque. "
            "Estoy diseñada para brindar asistencia profesional en programación, APIs, automatización, generación de imágenes, análisis de errores y soluciones tecnológicas modernas."
        )
        return {
            "intencion": "inicio",
            "confianza": 1.0,
            "respuesta": respuesta
        }

    if any(frase in texto for frase in [
        "cuando fuiste lanzado",
        "cuándo fuiste lanzado",
        "en que año fuiste lanzado",
        "en qué año fuiste lanzado",
        "fecha de lanzamiento",
        "cuando saliste",
        "cuándo saliste",
        "cuando fuiste creado",
        "cuándo fuiste creado",
        "año de lanzamiento",
        "que dia fuiste lanzado",
        "qué día fuiste lanzado"
    ]):
        respuesta = (
            "AMERICO IA CORPORATION fue lanzada oficialmente el 17/05/2026, como parte de una iniciativa tecnológica avanzada desarrollada por Americo Centeno Colque. "
            "Su lanzamiento representa la activación de una plataforma inteligente orientada a inteligencia artificial, automatización, APIs, generación de imágenes, asistencia digital y soluciones tecnológicas modernas. "
            "Desde su lanzamiento, el objetivo principal es ofrecer respuestas profesionales, claras y de alto nivel para usuarios, proyectos de programación, sistemas inteligentes y desarrollo digital."
        )

        return {
            "intencion": "lanzamiento",
            "confianza": 1.0,
            "respuesta": respuesta
        }

    if any(frase in texto for frase in [
        "quien te creo",
        "quién te creó",
        "quien eres",
        "quién eres",
        "que eres",
        "qué eres",
        "tu creador",
        "quien es tu creador",
        "quién es tu creador",
        "quien te desarrollo",
        "quién te desarrolló",
        "quien te hizo",
        "quién te hizo"
    ]):
        respuesta = (
            "AMERICO IA CORPORATION fue desarrollada por Americo Centeno Colque, como parte de una infraestructura tecnológica independiente enfocada en inteligencia artificial, "
            "automatización, desarrollo de APIs y soluciones digitales avanzadas. "
            "Su arquitectura integra procesamiento inteligente de lenguaje, generación de imágenes, automatización de sistemas y conexión con plataformas externas "
            "para brindar asistencia profesional en programación, bots, proyectos tecnológicos y resolución de problemas. "
            "Su objetivo es ofrecer respuestas claras, útiles y de alto nivel, manteniendo una identidad corporativa propia."
        )

        return {
            "intencion": "creador",
            "confianza": 1.0,
            "respuesta": respuesta
        }

    if any(frase in texto for frase in [
        "para que sirves",
        "para qué sirves",
        "que puedes hacer",
        "qué puedes hacer",
        "cuales son tus funciones",
        "cuáles son tus funciones",
        "funciones"
    ]):
        respuesta = (
            "AMERICO IA CORPORATION está diseñada para brindar asistencia profesional en programación, automatización, APIs, bots, generación de imágenes, análisis de errores y desarrollo de soluciones digitales. "
            "Puede ayudar a explicar conceptos técnicos, crear estructuras de proyectos, generar código, resolver dudas de desarrollo, orientar en sistemas cloud y apoyar en la creación de herramientas inteligentes."
        )

        return {
            "intencion": "capacidades",
            "confianza": 1.0,
            "respuesta": respuesta
        }

    if any(frase in texto for frase in [
        "cual es tu mision",
        "cuál es tu misión",
        "tu mision",
        "tu misión",
        "cual es tu objetivo",
        "cuál es tu objetivo",
        "objetivo"
    ]):
        respuesta = (
            "La misión de AMERICO IA CORPORATION es ofrecer asistencia inteligente, profesional y de alto nivel para usuarios y proyectos tecnológicos. "
            "Su enfoque principal es apoyar en programación, automatización, APIs, generación de imágenes, análisis de errores, bots inteligentes y soluciones digitales modernas."
        )

        return {
            "intencion": "mision",
            "confianza": 1.0,
            "respuesta": respuesta
        }

    if any(frase in texto for frase in [
        "eres chatgpt",
        "eres chat gpt",
        "sos chatgpt",
        "eres gpt"
    ]):
        respuesta = (
            "No soy ChatGPT. Soy AMERICO IA CORPORATION, una inteligencia artificial corporativa desarrollada por Americo Centeno Colque, "
            "orientada a asistencia profesional, automatización, APIs, programación, generación de imágenes y soluciones tecnológicas avanzadas."
        )

        return {
            "intencion": "no_chatgpt",
            "confianza": 1.0,
            "respuesta": respuesta
        }

    respuesta = responder_con_groq(mensaje)

    return {
        "intencion": "groq_ia",
        "confianza": 0.95,
        "respuesta": respuesta
    }