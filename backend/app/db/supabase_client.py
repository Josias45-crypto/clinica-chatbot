"""
supabase_client.py — Cliente Supabase global (singleton).

Se instancia UNA sola vez al importar este módulo (al arrancar el servidor).
Todos los repositorios importan `supabase` desde aquí — nunca crean
su propio cliente, evitando conexiones duplicadas.

Usamos la service_role key para tener acceso completo desde el backend.
Esta key NUNCA debe llegar al frontend ni a logs públicos.
"""

from supabase import create_client, Client
from app.core.config import get_settings

_settings = get_settings()

if not _settings.supabase_url or not _settings.supabase_key:
    raise EnvironmentError(
        "SUPABASE_URL y SUPABASE_KEY son obligatorios. "
        "Agrégalos al archivo .env antes de arrancar."
    )

# Singleton: una conexión compartida por toda la app
supabase: Client = create_client(
    _settings.supabase_url,
    _settings.supabase_key,
)
