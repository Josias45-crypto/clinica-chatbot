"""
repositories.py — Todas las operaciones de base de datos en un solo lugar.

Principio: si algo de DB falla, el chat NO se rompe.
Cada función tiene su propio try/except y loguea el error silenciosamente.
"""

import logging
from datetime import datetime, timezone
from app.db.supabase_client import supabase

logger = logging.getLogger(__name__)


# ── Chat (existentes) ──────────────────────────────────────────────────────────

async def save_conversation(session_id: str, clinic_slug: str) -> str | None:
    """
    Crea una nueva conversación en Supabase y devuelve su UUID.
    Retorna el conversation_id o None si falla.
    """
    try:
        result = (
            supabase.table("conversations")
            .insert({"session_id": session_id, "clinic_slug": clinic_slug})
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
    Incrementa el contador de mensajes de la conversación via RPC atómica.
    """
    try:
        supabase.rpc(
            "increment_message_count",
            {"conv_id": conversation_id},
        ).execute()
    except Exception as exc:
        logger.error("Error al incrementar message_count: %s", exc)


# ── Admin ──────────────────────────────────────────────────────────────────────

async def get_stats(clinic_slug: str) -> dict:
    """
    Retorna métricas globales y del día para el dashboard admin.
    Consulta directa a Supabase — solo el admin autenticado llega aquí.
    """
    try:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        total_conv = supabase.table("conversations") \
            .select("id", count="exact") \
            .eq("clinic_slug", clinic_slug) \
            .execute()

        total_msg = supabase.table("messages") \
            .select("id", count="exact") \
            .eq("clinic_slug", clinic_slug) \
            .execute()

        today_conv = supabase.table("conversations") \
            .select("id", count="exact") \
            .eq("clinic_slug", clinic_slug) \
            .gte("started_at", today) \
            .execute()

        today_msg = supabase.table("messages") \
            .select("id", count="exact") \
            .eq("clinic_slug", clinic_slug) \
            .gte("created_at", today) \
            .execute()

        return {
            "total_conversations":  total_conv.count or 0,
            "total_messages":       total_msg.count or 0,
            "conversations_today":  today_conv.count or 0,
            "messages_today":       today_msg.count or 0,
        }
    except Exception as exc:
        logger.error("Error al obtener stats: %s", exc)
        return {
            "total_conversations": 0,
            "total_messages": 0,
            "conversations_today": 0,
            "messages_today": 0,
        }


async def get_conversations(clinic_slug: str, page: int, limit: int) -> list:
    """
    Lista conversaciones paginadas ordenadas por fecha descendente.
    page empieza en 1.
    """
    try:
        offset = (page - 1) * limit
        result = supabase.table("conversations") \
            .select("id, session_id, started_at, message_count") \
            .eq("clinic_slug", clinic_slug) \
            .order("started_at", desc=True) \
            .range(offset, offset + limit - 1) \
            .execute()
        return result.data or []
    except Exception as exc:
        logger.error("Error al obtener conversaciones: %s", exc)
        return []


async def get_messages(conversation_id: str) -> list:
    """
    Retorna todos los mensajes de una conversación ordenados cronológicamente.
    """
    try:
        result = supabase.table("messages") \
            .select("id, role, content, created_at") \
            .eq("conversation_id", conversation_id) \
            .order("created_at", desc=False) \
            .execute()
        return result.data or []
    except Exception as exc:
        logger.error("Error al obtener mensajes: %s", exc)
        return []
