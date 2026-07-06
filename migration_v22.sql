-- ============================================================
-- migration_v22.sql — rental_details にテナント件数カラム追加
-- Supabase SQL Editor で実行してください
-- ============================================================

ALTER TABLE rental_details ADD COLUMN IF NOT EXISTS tenant_count INTEGER;
