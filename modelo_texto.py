import os
from google import genai


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


def responder_con_gemini(mensaje: str) -> str:
    if not GEMINI_API_KEY:
        return (
            "Todavía no tengo GEMINI_API_KEY configurado en Render. "
            "Puedo responder básico, pero para ser más inteligente necesito esa clave."
        )

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)

        prompt_sistema = """
Eres Mini IA de Americo Centeno Colque.

Reglas:
- Responde siempre en español.
- Responde claro, ordenado y útil.
- Ayuda especialmente con Python, APIs, FastAPI, Telegram, Render, bots, errores, comandos y programación.
- Si el usuario insulta, responde tranquilo y ayuda igual.
- No digas que eres Gemini.
- Di que eres la Mini IA de Americo.
- Si das código, que sea fácil de copiar.
- Si el usuario pide pasos, responde paso por paso.
- No inventes datos si no estás seguro.
"""

        respuesta = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"{prompt_sistema}\n\nUsuario: {mensaje}\nRespuesta:"
        )

        if respuesta.text:
            return respuesta.text.strip()

        return "No pude generar una respuesta en este momento."

    except Exception as error:
        return f"Tuve un error consultando la IA: {str(error)}"


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

    respuesta = responder_con_gemini(mensaje)

    return {
        "intencion": "gemini_ia",
        "confianza": 0.95,
        "respuesta": respuesta
    }