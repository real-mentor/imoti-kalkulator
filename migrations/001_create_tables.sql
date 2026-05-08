-- ============================================================
-- Real Mentor — Supabase Migration 001
-- Изпълни в Supabase Dashboard → SQL Editor
-- ============================================================

-- Разреши Row Level Security на всички таблици
-- Всеки потребител вижда САМО своите данни

-- ─── PROFILES ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS profiles (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    data        JSONB NOT NULL DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (user_id)
);

ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Потребителят вижда само своя профил"
    ON profiles FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Потребителят създава своя профил"
    ON profiles FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Потребителят обновява своя профил"
    ON profiles FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Потребителят изтрива своя профил"
    ON profiles FOR DELETE
    USING (auth.uid() = user_id);

-- Автоматично обновяване на updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER profiles_updated_at
    BEFORE UPDATE ON profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ─── SAVED CALCULATIONS ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS saved_calculations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name            VARCHAR(200) NOT NULL,
    property_data   JSONB NOT NULL DEFAULT '{}',
    results         JSONB NOT NULL DEFAULT '{}',
    strategy        VARCHAR(100),
    notes           TEXT DEFAULT '',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE saved_calculations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Потребителят вижда само своите калкулации"
    ON saved_calculations FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Потребителят създава свои калкулации"
    ON saved_calculations FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Потребителят обновява свои калкулации"
    ON saved_calculations FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Потребителят изтрива свои калкулации"
    ON saved_calculations FOR DELETE
    USING (auth.uid() = user_id);

-- Индекс за бързо зареждане по потребител
CREATE INDEX IF NOT EXISTS idx_saved_calculations_user_id
    ON saved_calculations (user_id, created_at DESC);
