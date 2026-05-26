-- ============================================================
-- migration_v3.sql — task_logs に写真URL列追加
-- Supabase SQL Editor で実行してください
-- ============================================================

ALTER TABLE task_logs
  ADD COLUMN IF NOT EXISTS photo_urls TEXT;

-- photo_urls は JSON 配列で保存（例: ["https://...","https://..."]）
