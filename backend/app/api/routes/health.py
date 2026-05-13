"""
health.py — Endpoint GET /health.

Permite que Render, monitores externos y el frontend verifiquen
que el servidor está vivo y saben qué modelo está activo.
"""

from fastapi import APIRouter
from app.core.config import get_settings

router = APIRouter()


@router.get("/health")
async def health_check():
    settings = get_settings()
    return {"status": "ok", "model": settings.groq_model}
