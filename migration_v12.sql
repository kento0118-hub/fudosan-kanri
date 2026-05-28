-- ============================================================
-- migration_v12.sql — properties.status に「negotiating」を追加
-- Supabase SQL Editor で実行してください
-- ============================================================

-- 既存の CHECK 制約を削除して再作成
ALTER TABLE properties
  DROP CONSTRAINT IF EXISTS properties_status_check;

ALTER TABLE properties
  ADD CONSTRAINT properties_status_check
  CHECK (status IN ('active', 'negotiating', 'preparing', 'inactive', 'sold'));
