"""
chat_service.py — Lógica de negocio del chat.

Esta capa es la única que conoce cómo hablar con Groq.
Las routes solo llaman a get_chat_reply() y devuelven el resultado —
no saben nada del LLM, del system prompt ni del formato de mensajes.
"""

import logging
from fastapi import HTTPException

from app.core.config import get_settings
from app.core.groq_client import groq_client
from app.models.schemas import Message
from app.services.prompt_builder import SYSTEM_PROMPT  # ← Phase 2: desde JSON

logger = logging.getLogger(__name__)


async def get_chat_reply(history: list[Message], message: str) -> tuple[str, str]:
    """
    Arma el hilo de mensajes y llama a Groq.
    Devuelve (reply_text, model_used).
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

    return reply_text, settings.groq_model
