# Nexvora Chatbot — Backend

Backend del chatbot médico configurable. Construido con FastAPI + Groq (llama-3.3-70b-versatile).

## Estructura

```
backend/
└── app/
    ├── main.py              # Entry point FastAPI
    ├── api/routes/          # Endpoints: /chat, /health
    ├── core/                # Config (pydantic-settings) + cliente Groq
    ├── models/              # Schemas Pydantic
    ├── services/            # Lógica de negocio + prompt_builder
    └── data/
        └── clinic_data.json # Datos de la clínica (editar para cambiar de cliente)
```

## Instalación local

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
```

## Variables de entorno

Crea un archivo `.env` en `backend/` basándote en `.env.example`:

```
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

## Arrancar en local

```bash
uvicorn app.main:app --reload --port 8000
```

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/health` | Estado del servidor y modelo activo |
| `POST` | `/chat` | Envía mensaje y recibe respuesta del bot |

### Ejemplo POST /chat

```json
{
  "message": "¿Cuáles son sus servicios?",
  "history": []
}
```

## Cambiar de clínica

Edita únicamente `app/data/clinic_data.json` y reinicia el servidor.
No se requiere ningún cambio de código Python.

---

## Deploy en Render

1. Conecta el repositorio en [render.com](https://render.com)
2. Crea un nuevo **Web Service** con esta configuración:

| Campo | Valor |
|-------|-------|
| **Root Directory** | `backend` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

3. En **Environment Variables** agrega:
   - `GROQ_API_KEY` → tu clave de Groq
   - `GROQ_MODEL` → `llama-3.3-70b-versatile`

> **Nota:** El Start Command debe ser `app.main:app` (no `main:app`).
> `app` es el paquete Python, `main` es el módulo, `app` es la instancia FastAPI.
