-- ============================================================
-- migration_v2.sql — property_details に新列追加
-- Supabase SQL Editor で実行してください
-- ============================================================

ALTER TABLE property_details
  ADD COLUMN IF NOT EXISTS publish_date            DATE,
  ADD COLUMN IF NOT EXISTS road_width              TEXT,
  ADD COLUMN IF NOT EXISTS frontage                TEXT,
  ADD COLUMN IF NOT EXISTS building_coverage_ratio NUMERIC(5,1),
  ADD COLUMN IF NOT EXISTS floor_area_ratio        NUMERIC(5,1),
  ADD COLUMN IF NOT EXISTS rights                  TEXT,
  ADD COLUMN IF NOT EXISTS transaction_type        TEXT,
  ADD COLUMN IF NOT EXISTS brokerage_fee           TEXT,
  ADD COLUMN IF NOT EXISTS suumo_listed            BOOLEAN NOT NULL DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS renovation_history      TEXT;

-- Storage RLS（写真アップロードに必要）
DROP POLICY IF EXISTS "anon_storage_all" ON storage.objects;
CREATE POLICY "anon_storage_all" ON storage.objects
  FOR ALL TO anon USING (true) WITH CHECK (true);
