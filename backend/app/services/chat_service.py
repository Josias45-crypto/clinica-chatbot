"""
chat_service.py — Lógica de negocio del chat.

Esta capa es la única que conoce cómo hablar con Groq.
Las routes solo llaman a get_chat_reply() y devuelven el resultado —
no saben nada del LLM, del system prompt ni del formato de mensajes.
"""

import asyncio
import logging
from fastapi import HTTPException

from app.core.config import get_settings
from app.core.groq_client import groq_client
from app.models.schemas import Message
from app.services.prompt_builder import SYSTEM_PROMPT
from app.db import repositories

logger = logging.getLogger(__name__)


async def _log_conversation(
    session_id: str,
    clinic_slug: str,
    user_message: str,
    assistant_reply: str,
) -> None:
    """
    Persiste la conversación en Supabase de forma silenciosa.
    Si algo falla aquí, el chat ya respondió — el usuario nunca lo nota.
    """
    try:
        conversation_id = await repositories.save_conversation(session_id, clinic_slug)
        if conversation_id is None:
            return  # save_conversation ya logueó el error

        await repositories.save_message(conversation_id, clinic_slug, "user", user_message)
        await repositories.save_message(conversation_id, clinic_slug, "assistant", assistant_reply)
        await repositories.increment_message_count(conversation_id)
    except Exception as exc:
        logger.error("Error inesperado en _log_conversation: %s", exc)


async def get_chat_reply(
    history: list[Message],
    message: str,
    session_id: str,
) -> tuple[str, str]:
    """
    Arma el hilo de mensajes, llama a Groq y dispara el guardado en background.
    Devuelve (reply_text, model_used) — el guardado no bloquea esta respuesta.
    """
    settings = get_settings()

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": message})

    logger.info("Enviando %d mensajes al modelo %s", len(messages), settings.groq_model)

    try:
        response = await groq_client.chat.completions.create(
            model=settings.groq_model,
            messages=messages,
            max_tokens=512,
            temperature=0.6,
        )
    except Exception as exc:
        logger.error("Error Groq API: %s", exc)
        raise HTTPException(status_code=502, detail=f"Error al contactar Groq: {exc}")

    reply_text = response.choices[0].message.content.strip()
    logger.info("Respuesta recibida (%d chars)", len(reply_text))

    # El usuario ya recibió su respuesta.
    # Guardamos en background sin hacerlo esperar.
    asyncio.create_task(
        _log_conversation(session_id, settings.clinic_slug, message, reply_text)
    )

    return reply_text, settings.groq_model
