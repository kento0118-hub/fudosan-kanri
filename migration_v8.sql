-- ============================================================
-- migration_v8.sql — properties に property_name を追加
-- Supabase SQL Editor で実行してください
-- ============================================================

ALTER TABLE properties
  ADD COLUMN IF NOT EXISTS property_name TEXT;
