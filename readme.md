# 🏥 Clínica Salud Total — Chatbot IA de Atención al Cliente

> Asistente virtual inteligente que atiende pacientes 24/7, responde consultas frecuentes y libera al personal administrativo de tareas repetitivas.

**Demo en vivo:** [clinica-chatbot.netlify.app](https://clinica-chatbot.netlify.app)  
**Backend API:** [clinica-chatbot-k8in.onrender.com](https://clinica-chatbot-k8in.onrender.com)

---

## ¿Qué hace este chatbot?

Un asistente conversacional con IA integrado en la web de una clínica. Conoce todo sobre el negocio y responde de forma natural, rápida y precisa — sin intervención humana.

- Atiende múltiples pacientes simultáneamente
- Disponible las 24 horas, los 7 días de la semana
- Responde en menos de 1 segundo
- Mantiene el historial de conversación por sesión
- Se adapta completamente a cualquier clínica o negocio

---

## Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Backend | Python · FastAPI · Uvicorn |
| IA | Groq API · LLaMA 3.3 70B |
| Frontend | HTML · CSS · JavaScript puro |
| Deploy Backend | Render (free tier) |
| Deploy Frontend | Netlify (free tier) |
| Control de versiones | Git · GitHub |

---

## Estructura del proyecto

```
clinica-chatbot/
├── backend/
│   ├── main.py              # Servidor FastAPI · endpoint /chat
│   ├── config.py            # Cliente Groq + system prompt
│   ├── requirements.txt     # Dependencias Python
│   ├── .python-version      # Python 3.11.9
│   └── .env                 # Variables de entorno (no subir a Git)
├── frontend/
│   └── index.html           # Chat UI completa
├── .gitignore
└── README.md
```

---

## Instalación local

### Requisitos
- Python 3.11+
- API Key de [Groq](https://console.groq.com)

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/Josias45-crypto/clinica-chatbot.git
cd clinica-chatbot/backend

# 2. Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
# Crear archivo .env con:
GROQ_API_KEY=tu_api_key_aqui
GROQ_MODEL=llama-3.3-70b-versatile

# 5. Iniciar el servidor
uvicorn main:app --reload
```

Abrir `frontend/index.html` en el navegador.

---

## API Reference

### POST /chat

Envía un mensaje y recibe la respuesta del asistente.

**Request:**
```json
{
  "message": "¿Cuáles son los horarios de atención?",
  "history": []
}
```

**Response:**
```json
{
  "reply": "Atendemos de lunes a sábado de 8am a 6pm. ¿Deseas agendar una cita?"
}
```

### GET /health

Verifica que el servidor esté activo.

```json
{ "status": "ok" }
```

---

## Casos de uso reales

### 🏥 Clínicas y consultorios
Responde preguntas sobre horarios, especialidades, precios y agendamiento de citas. Reduce llamadas telefónicas en un 60-80%.

### 🦷 Odontologías
Informa sobre tratamientos, precios, disponibilidad de turnos y preparación pre-consulta.

### 💆 Centros de estética y spa
Gestiona consultas sobre servicios, precios, duración de tratamientos y reservas.

### 🏋️ Gimnasios y academias
Responde sobre membresías, horarios de clases, instructores y promociones.

### 🍽️ Restaurantes
Informa sobre el menú, horarios, reservas, delivery y precios.

### 🏠 Inmobiliarias
Presenta propiedades disponibles, precios, zonas y agenda visitas.

### 🎓 Academias e institutos
Responde sobre cursos, precios, modalidades, fechas de inicio y proceso de inscripción.

---

## Funcionalidades actuales

- ✅ Chat conversacional con historial de sesión
- ✅ Respuestas rápidas (chips de acceso rápido)
- ✅ Indicador de escritura animado
- ✅ Diseño responsive (móvil y desktop)
- ✅ Personalidad y contexto del negocio 100% configurable
- ✅ Backend desplegado en la nube
- ✅ Frontend desplegado en la nube
- ✅ Costo operativo: $0/mes (tier gratuito)

---

## Roadmap — Próximas funcionalidades

### Corto plazo
- [ ] Integración con WhatsApp Business API
- [ ] Widget embebible (una línea de JS en cualquier web)
- [ ] Panel de administración para editar respuestas sin código
- [ ] Soporte multi-idioma (español / inglés)

### Mediano plazo
- [ ] Base de datos para guardar conversaciones (SQLite / Supabase)
- [ ] Dashboard de analytics: preguntas más frecuentes, horarios pico
- [ ] Sistema de agendamiento de citas integrado
- [ ] Notificaciones por email o WhatsApp al negocio

### Largo plazo
- [ ] Autenticación de usuarios
- [ ] Multi-tenant: un sistema, múltiples clientes
- [ ] Integración con CRMs (HubSpot, Zoho)
- [ ] Voz: respuestas de audio con Text-to-Speech

---

## Valor de negocio

| Métrica | Valor |
|---------|-------|
| Disponibilidad | 24/7 sin costo de personal |
| Tiempo de respuesta | < 1 segundo |
| Usuarios simultáneos | Ilimitados |
| Costo mensual | $0 (tier gratuito) |
| Tiempo de implementación | 1-3 días por cliente |

---

## Personalización

Para adaptar el chatbot a otro negocio, solo se necesita modificar el **system prompt** en `backend/config.py`:

```python
SYSTEM_PROMPT = """
Eres [nombre del asistente], asistente virtual de [nombre del negocio].
Tu rol es atender consultas de clientes sobre:
- [información del negocio]
- [servicios y precios]
- [horarios y contacto]
Responde siempre de forma amable, clara y profesional.
"""
```

---

## Autor

**Joel Josias Rojas Alca**  
Desarrollador de Software · IA & Automatización  
📧 joeljosias45@gmail.com  
🔗 [github.com/Josias45-crypto](https://github.com/Josias45-crypto)  
💼 [linkedin.com/in/joel-josias-rojas-alca](https://linkedin.com/in/joel-josias-rojas-alca-260145268)

---

## Licencia

MIT — libre de usar, modificar y distribuir.

---

*Este chatbot es un producto base. Puede ser personalizado e implementado para cualquier negocio en 1-3 días.*