"""
auth.py — Sistema de autenticación JWT para el panel admin.

Flujo: el admin hace POST /admin/login → recibe un JWT de 24h →
lo adjunta como Bearer token en cada request al panel admin.
"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

from app.core.config import get_settings

# Contexto de hashing — bcrypt es el estándar seguro para passwords
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24


def create_access_token(data: dict) -> str:
    """
    Crea un JWT firmado con el secret key de Settings.
    Incluye expiración de 24 horas desde el momento de emisión.
    """
    settings = get_settings()
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS)
    payload.update({"exp": expire})
    return jwt.encode(payload, settings.admin_secret_key, algorithm=ALGORITHM)


def verify_token(token: str) -> dict:
    """
    Verifica y decodifica un JWT. Lanza HTTP 401 si es inválido o expirado.
    Usado como dependencia en todos los endpoints protegidos del admin.
    """
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.admin_secret_key, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


def hash_password(password: str) -> str:
    """
    Genera un hash bcrypt del password.
    Usar al crear o cambiar credenciales de admin — nunca almacenar texto plano.
    """
    return _pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """
    Compara un password en texto plano con su hash bcrypt.
    Devuelve True si coinciden, False si no.
    """
    return _pwd_context.verify(plain, hashed)
