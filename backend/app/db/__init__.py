"""
db/__init__.py — Exportaciones del paquete de base de datos.
"""

from app.db.supabase_client import supabase
from app.db import repositories

__all__ = ["supabase", "repositories"]
