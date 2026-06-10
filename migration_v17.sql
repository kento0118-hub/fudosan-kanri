-- ============================================================
-- migration_v17.sql — 契約情報カラム追加
-- Supabase SQL Editor で実行してください
-- ============================================================

ALTER TABLE property_details ADD COLUMN IF NOT EXISTS purchase_offer_date DATE;
ALTER TABLE property_details ADD COLUMN IF NOT EXISTS contract_date        DATE;
ALTER TABLE property_details ADD COLUMN IF NOT EXISTS delivery_date        DATE;
