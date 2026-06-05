-- ============================================================
-- migration_v16.sql — 内見・問い合わせ記録 & 掲載開始日
-- Supabase SQL Editor で実行してください
-- ============================================================

-- 1. property_details に掲載開始日・販売開始日カラムを追加
ALTER TABLE property_details ADD COLUMN IF NOT EXISTS sale_start_date  DATE;
ALTER TABLE property_details ADD COLUMN IF NOT EXISTS suumo_start_date DATE;
ALTER TABLE property_details ADD COLUMN IF NOT EXISTS hp_start_date    DATE;
ALTER TABLE property_details ADD COLUMN IF NOT EXISTS sign_start_date  DATE;

-- 2. inquiry_logs: 内見・問い合わせ記録（売買・賃貸共通）
CREATE TABLE IF NOT EXISTS inquiry_logs (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  property_id   UUID NOT NULL,
  property_type TEXT NOT NULL CHECK (property_type IN ('sale', 'rental')),
  date          DATE NOT NULL DEFAULT CURRENT_DATE,
  type          TEXT NOT NULL CHECK (type IN ('viewing', 'inquiry')),
  route         TEXT CHECK (route IN ('suumo', 'hp', 'sign', 'referral', 'other')),
  status        TEXT CHECK (status IN ('considering', 'positive', 'declined', 'contracted')),
  memo          TEXT,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- RLS
ALTER TABLE inquiry_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "anon_all_inquiry_logs" ON inquiry_logs FOR ALL TO anon USING (true) WITH CHECK (true);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_inquiry_logs_property_id   ON inquiry_logs (property_id);
CREATE INDEX IF NOT EXISTS idx_inquiry_logs_date          ON inquiry_logs (date DESC);
CREATE INDEX IF NOT EXISTS idx_inquiry_logs_property_type ON inquiry_logs (property_type);
