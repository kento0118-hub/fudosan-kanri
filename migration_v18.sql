-- ============================================================
-- migration_v18.sql — properties.status CHECK制約を更新
-- Supabase SQL Editor で実行してください
-- ============================================================

-- 既存のCHECK制約を削除して新しい値を含む制約を再作成
ALTER TABLE properties DROP CONSTRAINT IF EXISTS properties_status_check;

ALTER TABLE properties
  ADD CONSTRAINT properties_status_check
  CHECK (status IN (
    'active',
    'inactive',
    'preparing',
    'negotiating',
    'contract_prep',
    'contracted',
    'sold'
  ));
