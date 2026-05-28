-- ============================================================
-- migration_v10.sql
-- Supabase SQL Editor で実行してください
-- ============================================================

-- 1. 販売形態カラムを property_details に追加
ALTER TABLE property_details
  ADD COLUMN IF NOT EXISTS sale_type TEXT;

-- 2. cost_management に中古住宅用取得費カラムを追加
ALTER TABLE cost_management
  ADD COLUMN IF NOT EXISTS land_acquisition_cost   NUMERIC(12,2),  -- 土地取得費（万円）
  ADD COLUMN IF NOT EXISTS building_acquisition_cost NUMERIC(12,2); -- 建物取得費・税込（万円）

-- 3. 積み上げ原価記録テーブルを新規作成
CREATE TABLE IF NOT EXISTS cost_periodic_records (
  id           UUID    PRIMARY KEY DEFAULT gen_random_uuid(),
  property_id  UUID    NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
  category     TEXT    NOT NULL,
  -- annual: record_year のみ使用
  -- monthly: record_year + record_month 使用
  -- irregular: record_date 使用
  record_year  INTEGER,
  record_month INTEGER,
  record_date  DATE,
  amount       NUMERIC(12,2) NOT NULL,
  memo         TEXT,
  created_at   TIMESTAMPTZ DEFAULT NOW()
);

-- RLS
ALTER TABLE cost_periodic_records ENABLE ROW LEVEL SECURITY;
CREATE POLICY "anon_all_periodic" ON cost_periodic_records
  FOR ALL TO anon USING (true) WITH CHECK (true);

-- カテゴリ一覧 (参考)
-- 'hoa_annual'         : 町内会費（年額）
-- 'tax_annual'         : 固定資産税・都市計画税（年額）
-- 'fire_annual'        : 火災保険料（年額）
-- 'utilities_monthly'  : 水道光熱費（月額）
-- 'irregular_ad'       : 宣伝費（不定期）
-- 'irregular_maint'    : 敷地内整備費（不定期）
-- 'irregular_labor'    : 人件費（不定期）
-- 'irregular_other'    : その他（不定期）
