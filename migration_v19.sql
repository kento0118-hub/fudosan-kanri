-- ============================================================
-- migration_v19.sql — property_details 全カラム一括補完
-- Supabase SQL Editor で実行してください
--
-- 初期スキーマ(supabase_schema.sql)作成後に追加されたカラムを
-- ADD COLUMN IF NOT EXISTS で一括追加します。
-- 既にカラムが存在する場合はスキップされるため、何度でも安全に実行できます。
--
-- 初期スキーマ時点で既に存在するカラム（追加不要）:
--   school_elementary, school_junior, water_supply, sewage,
--   buried_artifacts, documents, zoning, other_laws,
--   area_sqm, area_tsubo, land_condition, land_area_sqm,
--   land_area_tsubo, building_area_sqm, building_area_tsubo,
--   built_date, floor_plan, floor_plan_image
-- ============================================================

-- ── migration_v2 相当 ──────────────────────────────────────
ALTER TABLE property_details ADD COLUMN IF NOT EXISTS publish_date             DATE;
ALTER TABLE property_details ADD COLUMN IF NOT EXISTS road_width               TEXT;
ALTER TABLE property_details ADD COLUMN IF NOT EXISTS frontage                 TEXT;
ALTER TABLE property_details ADD COLUMN IF NOT EXISTS building_coverage_ratio  NUMERIC(5,1);
ALTER TABLE property_details ADD COLUMN IF NOT EXISTS floor_area_ratio         NUMERIC(5,1);
ALTER TABLE property_details ADD COLUMN IF NOT EXISTS rights                   TEXT;
ALTER TABLE property_details ADD COLUMN IF NOT EXISTS transaction_type         TEXT;
ALTER TABLE property_details ADD COLUMN IF NOT EXISTS brokerage_fee            TEXT;
ALTER TABLE property_details ADD COLUMN IF NOT EXISTS suumo_listed             BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE property_details ADD COLUMN IF NOT EXISTS renovation_history       TEXT;

-- ── migration_v5 相当 ──────────────────────────────────────
ALTER TABLE property_details ADD COLUMN IF NOT EXISTS for_sale_sign            BOOLEAN NOT NULL DEFAULT FALSE;

-- ── migration_v6 相当 ──────────────────────────────────────
ALTER TABLE property_details ADD COLUMN IF NOT EXISTS hp_listed                BOOLEAN NOT NULL DEFAULT FALSE;

-- ── migration_v10 相当 ─────────────────────────────────────
ALTER TABLE property_details ADD COLUMN IF NOT EXISTS sale_type                TEXT;

-- ── migration_v16 相当 ─────────────────────────────────────
ALTER TABLE property_details ADD COLUMN IF NOT EXISTS sale_start_date          DATE;
ALTER TABLE property_details ADD COLUMN IF NOT EXISTS suumo_start_date         DATE;
ALTER TABLE property_details ADD COLUMN IF NOT EXISTS hp_start_date            DATE;
ALTER TABLE property_details ADD COLUMN IF NOT EXISTS sign_start_date          DATE;

-- ── migration_v17 相当 ─────────────────────────────────────
ALTER TABLE property_details ADD COLUMN IF NOT EXISTS purchase_offer_date      DATE;
ALTER TABLE property_details ADD COLUMN IF NOT EXISTS contract_date            DATE;
ALTER TABLE property_details ADD COLUMN IF NOT EXISTS delivery_date            DATE;

-- ── 確認用 ────────────────────────────────────────────────
-- 実行後にこのSELECTで全カラムを確認できます
SELECT column_name, data_type, column_default, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name   = 'property_details'
ORDER BY ordinal_position;
