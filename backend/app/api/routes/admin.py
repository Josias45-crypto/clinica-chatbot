"""
admin.py — Rutas del panel de administración, protegidas con JWT.

Flujo de autenticación:
  1. POST /admin/login  → devuelve access_token
  2. Resto de endpoints → requieren header: Authorization: Bearer <token>
"""

import json
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from app.core.auth import create_access_token, verify_token, verify_password
from app.core.config import get_settings
from app.db import repositories
from app.services import prompt_builder

logger = logging.getLogger(__name__)
router = APIRouter()
_bearer = HTTPBearer()

_CLINIC_DATA_PATH = Path(__file__).parent.parent.parent / "data" / "clinic_data.json"


# ── Dependencia de autenticación ───────────────────────────────────────────────

def require_auth(credentials: HTTPAuthorizationCredentials = Depends(_bearer)) -> dict:
    """Dependencia reutilizable: verifica el Bearer token en cada request protegido."""
    return verify_token(credentials.credentials)


# ── Schemas de request ─────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post("/login")
async def login(body: LoginRequest):
    """
    Autentica al administrador y devuelve un JWT de 24 horas.
    Las credenciales se comparan contra Settings (variables de entorno).
    """
    settings = get_settings()
    if (
        body.username != settings.admin_username
        or not verify_password(body.password, settings.admin_password_hash)
    ):
        logger.warning("Intento de login fallido para usuario: %s", body.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )
    token = create_access_token({"sub": body.username})
    logger.info("Login exitoso: %s", body.username)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/stats")
async def get_stats(_: dict = Depends(require_auth)):
    """
    Métricas globales y del día para el dashboard.
    Requiere Bearer token válido.
    """
    settings = get_settings()
    stats = await repositories.get_stats(settings.clinic_slug)
    return stats


@router.get("/conversations")
async def list_conversations(
    page: int = 1,
    limit: int = 20,
    _: dict = Depends(require_auth),
):
    """
    Lista conversaciones paginadas, ordenadas por fecha descendente.
    Requiere Bearer token válido.
    """
    settings = get_settings()
    conversations = await repositories.get_conversations(settings.clinic_slug, page, limit)
    return {"page": page, "limit": limit, "data": conversations}


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: str,
    _: dict = Depends(require_auth),
):
    """
    Retorna todos los mensajes de una conversación ordenados cronológicamente.
    Requiere Bearer token válido.
    """
    messages = await repositories.get_messages(conversation_id)
    if not messages:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    return {"conversation_id": conversation_id, "messages": messages}


@router.put("/clinic")
async def update_clinic_data(
    clinic_data: dict,
    _: dict = Depends(require_auth),
):
    """
    Actualiza clinic_data.json en disco y recarga el system prompt en memoria
    sin necesidad de reiniciar el servidor.
    Requiere Bearer token válido.
    """
    try:
        with open(_CLINIC_DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(clinic_data, f, ensure_ascii=False, indent=2)

        # Recarga el prompt en memoria sin reiniciar
        prompt_builder._CLINIC_DATA = prompt_builder._load_clinic_data()
        prompt_builder.SYSTEM_PROMPT = prompt_builder.build_system_prompt()

        logger.info("clinic_data.json actualizado y prompt recargado en memoria")
        return {"success": True, "message": "Datos actualizados correctamente"}
    except Exception as exc:
        logger.error("Error al actualizar clinic_data: %s", exc)
        raise HTTPException(status_code=500, detail=f"Error al guardar datos: {exc}")
