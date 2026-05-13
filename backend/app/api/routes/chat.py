"""
chat.py — Endpoint POST /chat.

La route solo recibe, valida y delega.
Toda la lógica vive en chat_service.get_chat_reply().
"""

from fastapi import APIRouter
from app.models.schemas import ChatRequest, ChatResponse
from app.services.chat_service import get_chat_reply

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    reply, model_used = await get_chat_reply(request.history, request.message)
    return ChatResponse(reply=reply, model_used=model_used)
