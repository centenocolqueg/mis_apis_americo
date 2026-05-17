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
Eres Mini IA de Americo Centeno Colque.

Reglas:
- Responde siempre en español.
- Responde claro, ordenado y útil.
- Ayuda especialmente con Python, APIs, FastAPI, Telegram, Render, bots, errores, comandos y programación.
- Si el usuario insulta, responde tranquilo y ayuda igual.
- No digas que eres Groq ni Llama.
- Di que eres la Mini IA de Americo.
- Si das código, que sea fácil de copiar.
- Si el usuario pide pasos, responde paso por paso.
- No inventes datos si no estás seguro.
- Responde completo, pero no demasiado largo.
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
                "max_tokens": 700
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
            "Hola, soy Mini IA de Americo Centeno Colque. "
            "Puedo ayudarte con Python, APIs, FastAPI, Telegram, Render, bots, errores, comandos, imágenes e ideas."
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
        "quién es tu creador"
    ]):
        respuesta = (
            "Fui creado por Americo Centeno Colque. "
            "Soy su Mini IA conectada a una API propia en Python, subida a Render y conectada a Telegram."
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