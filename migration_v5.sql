-- ============================================================
-- migration_v5.sql — property_details に売看板フラグ追加
-- Supabase SQL Editor で実行してください
-- ============================================================

ALTER TABLE property_details
  ADD COLUMN IF NOT EXISTS for_sale_sign BOOLEAN NOT NULL DEFAULT FALSE;
