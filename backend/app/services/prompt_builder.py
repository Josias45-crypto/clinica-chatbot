"""
prompt_builder.py — Construye el SYSTEM_PROMPT dinámicamente desde clinic_data.json.

Principio: cambiar de clínica = solo cambiar el JSON. Cero cambios de código.

El JSON se carga UNA sola vez al importar este módulo (al arrancar el servidor).
Todos los requests comparten el mismo prompt en memoria — sin I/O por request.
"""

import json
from pathlib import Path

# Ruta al JSON relativa a este archivo (funciona sin importar desde dónde se arranque)
_DATA_PATH = Path(__file__).parent.parent / "data" / "clinic_data.json"


def _load_clinic_data() -> dict:
    """Carga y valida clinic_data.json al iniciar. Falla rápido si hay problemas."""
    if not _DATA_PATH.exists():
        raise FileNotFoundError(
            f"clinic_data.json no encontrado en {_DATA_PATH}. "
            "Crea el archivo con los datos de la clínica antes de arrancar."
        )
    try:
        with open(_DATA_PATH, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(f"clinic_data.json tiene un error de formato JSON: {exc}") from exc

    # Validar que las secciones mínimas existen
    required = ["clinic", "assistant", "schedule", "services", "contact", "bot_rules"]
    missing = [key for key in required if key not in data]
    if missing:
        raise KeyError(f"clinic_data.json le faltan estas secciones: {missing}")

    return data


def build_system_prompt() -> str:
    """
    Construye el prompt completo desde los datos en memoria.
    Llamar esta función es O(1) — no hace I/O, solo formatea strings.
    """
    d = _CLINIC_DATA
    clinic    = d["clinic"]
    assistant = d["assistant"]
    schedule  = d["schedule"]
    services  = d["services"]
    contact   = d["contact"]
    extras    = d["extras"]
    rules     = d["bot_rules"]

    # ── Identidad del asistente ────────────────────────────────────────────────
    header = (
        f"Eres {assistant['name']}, el asistente virtual de {clinic['name']}.\n"
        f"Tu personalidad es {assistant['personality']}.\n"
        f"Tu tono es {assistant['tone']}.\n"
        f"Habla en {assistant['language']}.\n"
    )

    # ── Información de la clínica ──────────────────────────────────────────────
    clinic_info = (
        f"\n{'═' * 43}\n"
        f" INFORMACIÓN OFICIAL DE {clinic['name'].upper()}\n"
        f"{'═' * 43}\n\n"
        f"DATOS GENERALES\n"
        f"  • Nombre:     {clinic['name']} — {clinic.get('slogan', '')}\n"
        f"  • Ciudad:     {clinic.get('city', '')}\n"
        f"  • Dirección:  {clinic['address']}\n"
        f"  • Referencia: {clinic.get('reference', '')}\n"
        f"  • Fundada:    {clinic['founded']} ({clinic.get('years', '')})\n"
    )

    # ── Horarios ───────────────────────────────────────────────────────────────
    schedule_lines = "\n".join(
        f"  • {label}: {value}"
        for label, value in {
            "Lunes a Viernes": schedule.get("monday_friday", ""),
            "Sábados":         schedule.get("saturday", ""),
            "Domingos":        schedule.get("sunday", ""),
            "Feriados":        schedule.get("holidays", ""),
        }.items()
        if value  # omite entradas vacías automáticamente
    )
    schedule_section = f"\nHORARIOS DE ATENCIÓN\n{schedule_lines}\n"

    # ── Servicios y precios ────────────────────────────────────────────────────
    service_lines = "\n".join(
        f"  • {s['name']:<18} → S/ {s['price']:.2f}"
        + (f"  ({s['note']})" if s.get("note") else "")
        + (" ⭐ más solicitado" if s.get("popular") else "")
        for s in services
    )
    services_section = f"\nSERVICIOS Y PRECIOS\n{service_lines}\n"

    # ── Contacto ───────────────────────────────────────────────────────────────
    contact_lines = "\n".join(
        f"  • {label}: {value}"
        for label, value in {
            "WhatsApp":  contact.get("whatsapp", ""),
            "Teléfono":  contact.get("phone", ""),
            "Email":     contact.get("email", ""),
            "Facebook":  contact.get("facebook", ""),
            "Citas":     contact.get("appointments", ""),
        }.items()
        if value
    )
    contact_section = f"\nCONTACTO Y CITAS\n{contact_lines}\n"

    # ── Extras (seguros, pagos, etc.) ──────────────────────────────────────────
    # Esta sección se construye dinámicamente — si añades un campo al JSON,
    # aparece automáticamente en el prompt sin tocar este código.
    extra_lines = []
    if extras.get("insurance"):
        extra_lines.append(f"  • Seguros aceptados: {', '.join(extras['insurance'])}")
    if extras.get("payments"):
        extra_lines.append(f"  • Formas de pago:    {', '.join(extras['payments'])}")
    for key in ("parking", "pharmacy", "certificates"):
        if extras.get(key):
            extra_lines.append(f"  • {extras[key]}")
    extras_section = f"\nSERVICIOS ADICIONALES\n" + "\n".join(extra_lines) + "\n" if extra_lines else ""

    # ── Reglas de comportamiento ───────────────────────────────────────────────
    rules_lines = "\n".join(f"{i+1}. {rule}" for i, rule in enumerate(rules))
    rules_section = (
        f"\n{'═' * 43}\n"
        f" REGLAS DE COMPORTAMIENTO\n"
        f"{'═' * 43}\n\n"
        f"{rules_lines}\n"
    )

    return (
        header
        + clinic_info
        + schedule_section
        + services_section
        + contact_section
        + extras_section
        + rules_section
    ).strip()


# Carga al importar el módulo — una sola vez, al arrancar el servidor
_CLINIC_DATA: dict = _load_clinic_data()

# Prompt preconstruido en memoria — sin I/O por request
SYSTEM_PROMPT: str = build_system_prompt()
