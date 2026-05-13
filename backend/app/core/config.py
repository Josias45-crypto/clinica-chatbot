"""
config.py — Configuración centralizada con pydantic-settings.

Lee variables de entorno desde .env y las expone como un objeto tipado.
Usar `get_settings()` en lugar de importar `settings` directamente
permite sobreescribir valores en tests sin efectos secundarios.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Todas las variables de entorno que necesita la app."""

    groq_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"

    # Metadatos de la API (usados en los docs de FastAPI)
    app_title: str = "Nexvora Chatbot API"
    app_version: str = "1.0.0"
    app_description: str = "Backend del chatbot médico — Nexvora Systems"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,   # GROQ_API_KEY == groq_api_key
    )


@lru_cache
def get_settings() -> Settings:
    """
    Singleton de settings: se instancia una vez y se cachea.
    lru_cache garantiza que .env se lee una sola vez al arrancar.
    """
    return Settings()
