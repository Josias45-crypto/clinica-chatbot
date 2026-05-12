"""
main.py — Backend FastAPI para el chatbot de Clínica Salud Total.

Endpoints:
  POST /chat   → recibe historial + nuevo mensaje, devuelve respuesta del bot
  GET  /health → comprueba que el servidor está vivo
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal
import logging

from config import client, MODEL, SYSTEM_PROMPT

# ── Logging básico ─────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(levelname)s │ %(message)s")
logger = logging.getLogger(__name__)

# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Chatbot — Clínica Salud Total",
    description="API de atención al cliente potenciada por xAI Grok.",
    version="1.0.0",
)

# Permite peticiones desde el frontend (ajusta origins en producción)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


# ── Modelos Pydantic ───────────────────────────────────────────────────────────
class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1, max_length=2000)


class ChatRequest(BaseModel):
    """
    El frontend envía el historial completo de la sesión + el nuevo mensaje.
    Mantener el historial en el cliente simplifica el backend (sin estado).
    """
    history: list[Message] = Field(default_factory=list)
    message: str = Field(..., min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    reply: str
    model_used: str


# ── Endpoints ──────────────────────────────────────────────────────────────────
@app.get("/health")
def health_check():
    return {"status": "ok", "model": MODEL}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Recibe el historial de la conversación y el mensaje actual.
    Construye el array de mensajes para la API de xAI y devuelve la respuesta.
    """
    # Construir el hilo de mensajes: system → historial → mensaje nuevo
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for msg in request.history:
        messages.append({"role": msg.role, "content": msg.content})

    messages.append({"role": "user", "content": request.message})

    logger.info("Enviando %d mensajes al modelo %s", len(messages), MODEL)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=512,
            temperature=0.6,   # un poco de calidez sin perder precisión
        )
    except Exception as exc:
        logger.error("Error xAI API: %s", exc)
        raise HTTPException(
            status_code=502,
            detail=f"Error al contactar la API de xAI: {exc}",
        )

    reply_text = response.choices[0].message.content.strip()
    logger.info("Respuesta recibida (%d chars)", len(reply_text))

    return ChatResponse(reply=reply_text, model_used=MODEL)
