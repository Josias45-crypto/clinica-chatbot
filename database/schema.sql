-- ============================================================
-- Schema: Chatbot SaaS para Clínicas — Nexvora Systems
-- Ejecutar en: Supabase SQL Editor
-- ============================================================

-- Tabla de clínicas (preparada para multi-tenant en Fase 6)
CREATE TABLE IF NOT EXISTS clinics (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug        TEXT UNIQUE NOT NULL,  -- ej: "medivida", "sanjuan"
    name        TEXT NOT NULL,
    data        JSONB NOT NULL,        -- contenido completo de clinic_data.json
    is_active   BOOLEAN DEFAULT true,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de conversaciones (una por sesión de usuario)
CREATE TABLE IF NOT EXISTS conversations (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id   UUID REFERENCES clinics(id) ON DELETE CASCADE,
    clinic_slug TEXT NOT NULL,         -- redundante para queries rápidas
    session_id  TEXT NOT NULL,         -- generado en el frontend
    started_at  TIMESTAMPTZ DEFAULT NOW(),
    ended_at    TIMESTAMPTZ,
    message_count INTEGER DEFAULT 0,
    metadata    JSONB DEFAULT '{}'     -- para datos extra futuros
);

-- Tabla de mensajes individuales
CREATE TABLE IF NOT EXISTS messages (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    clinic_slug     TEXT NOT NULL,
    role            TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content         TEXT NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para queries frecuentes del panel admin
CREATE INDEX IF NOT EXISTS idx_conversations_clinic_slug
    ON conversations(clinic_slug);
CREATE INDEX IF NOT EXISTS idx_conversations_started_at
    ON conversations(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id
    ON messages(conversation_id);

-- Row Level Security (preparado para Fase 6)
ALTER TABLE clinics       ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages      ENABLE ROW LEVEL SECURITY;

-- Política temporal: acceso total con service_role key
-- En Fase 6 se restringe por clinic_id
CREATE POLICY "service_role_all" ON clinics
    FOR ALL USING (true);
CREATE POLICY "service_role_all" ON conversations
    FOR ALL USING (true);
CREATE POLICY "service_role_all" ON messages
    FOR ALL USING (true);

-- Trigger para actualizar updated_at en clinics
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER clinics_updated_at
    BEFORE UPDATE ON clinics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
