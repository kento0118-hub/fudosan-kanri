-- ============================================================
-- migration_v21.sql — 社員確認・管理者承認カラム追加
-- Supabase SQL Editor で実行してください
-- ============================================================

ALTER TABLE properties ADD COLUMN IF NOT EXISTS staff_checked_at TIMESTAMPTZ;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS admin_checked_at TIMESTAMPTZ;
