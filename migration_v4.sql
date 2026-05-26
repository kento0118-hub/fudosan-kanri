-- ============================================================
-- migration_v4.sql — checklist_checks に year 列追加・ユニーク制約変更
-- Supabase SQL Editor で実行してください
-- ============================================================

-- 1. year 列を追加（既存レコードは今年の値が入る）
ALTER TABLE checklist_checks
  ADD COLUMN IF NOT EXISTS year INTEGER NOT NULL DEFAULT EXTRACT(YEAR FROM NOW())::INTEGER;

-- 2. 旧ユニーク制約を削除
ALTER TABLE checklist_checks
  DROP CONSTRAINT IF EXISTS checklist_checks_property_id_item_id_key;

-- 3. 新ユニーク制約（property_id + item_id + year の組み合わせ）
ALTER TABLE checklist_checks
  ADD CONSTRAINT checklist_checks_property_id_item_id_year_key
  UNIQUE (property_id, item_id, year);
