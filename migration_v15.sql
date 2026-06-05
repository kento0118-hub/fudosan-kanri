-- ============================================================
-- migration_v15.sql — 顧客情報・値下げ履歴 テーブル追加
-- Supabase SQL Editor で実行してください
-- ============================================================

-- 1. properties テーブルに seller_info カラムを追加（仲介物件の顧客情報）
ALTER TABLE properties ADD COLUMN IF NOT EXISTS seller_info JSONB;

-- 2. price_history: 値下げ履歴
CREATE TABLE IF NOT EXISTS price_history (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  property_id   UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
  old_price     NUMERIC(10,2),
  new_price     NUMERIC(10,2),
  recorded_date DATE NOT NULL DEFAULT CURRENT_DATE,
  memo          TEXT,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- RLS
ALTER TABLE price_history ENABLE ROW LEVEL SECURITY;
CREATE POLICY "anon_all_price_history" ON price_history FOR ALL TO anon USING (true) WITH CHECK (true);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_price_history_property_id ON price_history (property_id);
CREATE INDEX IF NOT EXISTS idx_price_history_date        ON price_history (recorded_date DESC);
