-- ============================================================
-- migration_v6.sql — property_details に HP掲載フラグ追加
-- Supabase SQL Editor で実行してください
-- ============================================================

ALTER TABLE property_details
  ADD COLUMN IF NOT EXISTS hp_listed BOOLEAN NOT NULL DEFAULT FALSE;
