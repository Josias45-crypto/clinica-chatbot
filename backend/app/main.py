"""
main.py — Entry point de la aplicación FastAPI.

Aquí se crea la app, se configura el middleware y se registran
todos los routers. No contiene lógica de negocio.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api.routes import chat, health

logging.basicConfig(level=logging.INFO, format="%(levelname)s │ %(message)s")

settings = get_settings()

app = FastAPI(
    title=settings.app_title,
    description=settings.app_description,
    version=settings.app_version,
)

# CORS abierto durante desarrollo — restringir origins en producción (Fase 3)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(health.router)
