"""
groq_client.py — Cliente Groq global (singleton).

Se instancia UNA sola vez cuando la app arranca (lifespan).
Todos los servicios importan `groq_client` desde aquí — nunca crean
su propio cliente, evitando conexiones duplicadas por request.
"""

from openai import AsyncOpenAI
from app.core.config import get_settings

_settings = get_settings()

# Singleton: una conexión compartida por toda la app
groq_client = AsyncOpenAI(
    api_key=_settings.groq_api_key,
    base_url="https://api.groq.com/openai/v1",
)
