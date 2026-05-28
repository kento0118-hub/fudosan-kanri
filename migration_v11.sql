-- ============================================================
-- migration_v11.sql
-- Supabase SQL Editor で実行してください
-- ============================================================

-- 1. cost_periodic_records にインデックスを追加（検索高速化）
CREATE INDEX IF NOT EXISTS idx_cost_periodic_property_cat
  ON cost_periodic_records (property_id, category);

-- 2. 水道光熱費の新カテゴリについて（スキーマ変更なし）
-- 月毎管理の水道光熱費を以下3カテゴリに分割（コード側のみ変更）
-- 'water_monthly'       : 水道代（月額）
-- 'electricity_monthly' : 電気代（月額）
-- 'gas_monthly'         : ガス代（月額）
-- ※ 旧カテゴリ 'utilities_monthly' のレコードは自動移行されません。
--    既存レコードがある場合は手動で UPDATE してください。
-- UPDATE cost_periodic_records
--   SET category = 'water_monthly'
--   WHERE category = 'utilities_monthly';
