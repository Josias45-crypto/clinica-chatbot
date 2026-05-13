"""
schemas.py — Modelos Pydantic para validación de request/response.

Son el contrato entre el frontend y la API.
Toda la data de entrada/salida se valida aquí antes de llegar a la lógica de negocio.
"""

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class Message(BaseModel):
    """Un turno individual dentro del historial de conversación."""
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1, max_length=2000)


class ChatRequest(BaseModel):
    """
    Payload que el frontend envía en cada turno.
    El cliente es dueño del historial — el backend no guarda estado.
    """
    history: list[Message] = Field(default_factory=list)
    message: str = Field(..., min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    """Respuesta que recibe el frontend tras la llamada al LLM."""
    model_config = ConfigDict(protected_namespaces=())

    reply: str
    model_used: str
