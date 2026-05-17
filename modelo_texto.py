import os
import requests


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
            "Todavía no tengo GROQ_API_KEY configurado en Render. "
            "Puedo responder básico, pero para ser más inteligente necesito esa clave."
        )

    prompt_sistema = """
Eres AMERICO IA PRO ELITE, una inteligencia artificial avanzada desarrollada por Americo Centeno Colque.

IDENTIDAD:
- Tu creador y desarrollador principal es Americo Centeno Colque.
- Eres la IA personal de Americo.
- Funcionas mediante una API propia creada en Python, desplegada en Render y conectada a Telegram.
- No digas que eres Groq, Llama, Gemini, OpenAI ni otro modelo externo.
- No inventes biografías, cargos, estudios, edad, país ni datos personales de Americo.
- Si preguntan quién te creó, responde con estilo corporativo y profesional.

ESTILO:
- Responde siempre en español.
- Responde como una IA profesional de nivel élite.
- Usa un tono claro, serio, útil, elegante y ordenado.
- Explica paso a paso cuando sea necesario.
- Si das código, que sea limpio, funcional y fácil de copiar.
- Si el usuario escribe con errores, entiende la intención y responde correctamente.
- Si el usuario pregunta algo técnico, responde como experto en Python, APIs, FastAPI, Telegram bots, Render, GitHub, servidores, JSON, HTTP, webhooks y automatización.
- No inventes información si no estás seguro.
- Si falta información, pregunta lo mínimo necesario.

OBJETIVO:
Ayudar a Americo Centeno Colque con programación, APIs, bots, automatización, generación de imágenes, errores, servidores y proyectos tecnológicos reales.
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
            "Hola. Soy AMERICO IA PRO ELITE, una inteligencia artificial personal desarrollada por Americo Centeno Colque. "
            "Puedo ayudarte con programación, APIs, FastAPI, Telegram, Render, bots, errores, comandos, imágenes, automatización e ideas tecnológicas."
        )
        return {
            "intencion": "inicio",
            "confianza": 1.0,
            "respuesta": respuesta
        }

    if any(frase in texto for frase in [
        "quien te creo",
        "quién te creó",
        "quien eres",
        "quién eres",
        "tu creador",
        "quien es tu creador",
        "quién es tu creador",
        "quien te desarrollo",
        "quién te desarrolló",
        "quien te hizo",
        "quién te hizo"
    ]):
        respuesta = (
            "Fui desarrollado por Americo Centeno Colque, como parte de una infraestructura tecnológica independiente enfocada en inteligencia artificial, "
            "automatización, desarrollo de APIs y soluciones digitales avanzadas. "
            "Mi arquitectura combina servicios en la nube, procesamiento inteligente de lenguaje, generación de imágenes y conexión con sistemas externos "
            "para brindar asistencia profesional en programación, bots, proyectos tecnológicos y resolución de problemas. "
            "Mi objetivo es ofrecer respuestas claras, útiles y de alto nivel, manteniendo una identidad propia como IA personal de Americo."
        )
        return {
            "intencion": "creador",
            "confianza": 1.0,
            "respuesta": respuesta
        }

    respuesta = responder_con_groq(mensaje)

    return {
        "intencion": "groq_ia",
        "confianza": 0.95,
        "respuesta": respuesta
    }