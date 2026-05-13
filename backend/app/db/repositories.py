"""
repositories.py — Todas las operaciones de base de datos en un solo lugar.

Principio: si algo de DB falla, el chat NO se rompe.
Cada función tiene su propio try/except y loguea el error silenciosamente.
"""

import logging
from app.db.supabase_client import supabase

logger = logging.getLogger(__name__)


async def save_conversation(session_id: str, clinic_slug: str) -> str | None:
    """
    Crea una nueva conversación en Supabase y devuelve su UUID.
    Si ya existe una conversación con el mismo session_id, crea una nueva
    (cada recarga del frontend es una sesión nueva).
    Retorna el conversation_id o None si falla.
    """
    try:
        result = (
            supabase.table("conversations")
            .insert({
                "session_id":  session_id,
                "clinic_slug": clinic_slug,
            })
            .execute()
        )
        conversation_id = result.data[0]["id"]
        logger.info("Conversación creada: %s (sesión %s)", conversation_id, session_id)
        return conversation_id
    except Exception as exc:
        logger.error("Error al crear conversación en Supabase: %s", exc)
        return None


async def save_message(
    conversation_id: str,
    clinic_slug: str,
    role: str,
    content: str,
) -> None:
    """
    Guarda un mensaje individual (user o assistant) en la tabla messages.
    role debe ser "user" o "assistant" — validado por el CHECK en el schema SQL.
    """
    try:
        supabase.table("messages").insert({
            "conversation_id": conversation_id,
            "clinic_slug":     clinic_slug,
            "role":            role,
            "content":         content,
        }).execute()
    except Exception as exc:
        logger.error("Error al guardar mensaje [%s] en Supabase: %s", role, exc)


async def increment_message_count(conversation_id: str) -> None:
    """
    Incrementa el contador de mensajes de la conversación.
    Se llama una vez por turno (user + assistant = 1 turno = +2 mensajes).
    Usa rpc para hacer el incremento atómico en el servidor de DB.
    """
    try:
        supabase.rpc(
            "increment_message_count",
            {"conv_id": conversation_id},
        ).execute()
    except Exception as exc:
        # No crítico — el contador es solo para analytics
        logger.error("Error al incrementar message_count: %s", exc)
