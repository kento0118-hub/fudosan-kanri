-- ============================================================
-- migration_v23.sql — repair_logs 新カラム追加・repair_tasks 作成
-- Supabase SQL Editor で実行してください
-- ============================================================

ALTER TABLE repair_logs ADD COLUMN IF NOT EXISTS property_id UUID REFERENCES properties(id) ON DELETE CASCADE;
ALTER TABLE repair_logs ADD COLUMN IF NOT EXISTS visitor_name TEXT;
ALTER TABLE repair_logs ADD COLUMN IF NOT EXISTS notes TEXT;
ALTER TABLE repair_logs ADD COLUMN IF NOT EXISTS photo_urls TEXT DEFAULT '[]';
ALTER TABLE repair_logs ADD COLUMN IF NOT EXISTS admin_approved_at TIMESTAMPTZ;
ALTER TABLE repair_logs ADD COLUMN IF NOT EXISTS season TEXT DEFAULT 'normal';

CREATE TABLE IF NOT EXISTS repair_tasks (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  repair_id  UUID NOT NULL REFERENCES repair_logs(id) ON DELETE CASCADE,
  content    TEXT NOT NULL,
  is_done    BOOLEAN NOT NULL DEFAULT FALSE,
  done_at    TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE repair_tasks ENABLE ROW LEVEL SECURITY;
CREATE POLICY IF NOT EXISTS "anon_all" ON repair_tasks FOR ALL TO anon USING (true) WITH CHECK (true);
