-- ============================================================
-- migration_v9.sql — 原価管理テーブル追加
-- Supabase SQL Editor で実行してください
-- ============================================================

CREATE TABLE IF NOT EXISTS cost_management (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  property_id         UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,

  -- 1. 仕入関連
  acquisition_date    DATE,
  acquisition_cost    NUMERIC(12,2),   -- 物件取得費（万円）
  broker_fee          NUMERIC(12,2),   -- 不動産仲介手数料（万円）
  acquisition_tax     NUMERIC(12,2),   -- 不動産取得税（万円）
  transfer_reg        NUMERIC(12,2),   -- 所有権移転登記費用（万円）
  stamp_tax           NUMERIC(12,2),   -- 印紙税・売買契約（万円）
  survey_purchase     NUMERIC(12,2),   -- 測量費（万円）
  demolition          NUMERIC(12,2),   -- 建物解体費（万円）
  mortgage_release    NUMERIC(12,2),   -- 抵当権抹消費用（万円）
  other_purchase      NUMERIC(12,2),   -- その他（仕入）（万円）

  -- 2. 施工関連
  land_prep           NUMERIC(12,2),   -- 造成工事費（万円）
  construction        NUMERIC(12,2),   -- 建築本体工事費（万円）
  design_supervision  NUMERIC(12,2),   -- 設計・監理費（万円）
  performance_cert    NUMERIC(12,2),   -- 性能評価・認定費用（万円）
  other_construction  NUMERIC(12,2),   -- その他（施工）（万円）

  -- 3. 登記・行政関連
  reg_survey          NUMERIC(12,2),   -- 表示登記・分筆合筆費用（万円）
  farmland            NUMERIC(12,2),   -- 農地転用費用（万円）
  dev_permit          NUMERIC(12,2),   -- 開発許可申請費用（万円）
  other_reg           NUMERIC(12,2),   -- その他（登記）（万円）

  -- 4. 販売費（一括入力）
  planning            NUMERIC(12,2),
  advertising         NUMERIC(12,2),
  site_maint          NUMERIC(12,2),
  hoa_fee             NUMERIC(12,2),
  furniture           NUMERIC(12,2),
  handover_finish     NUMERIC(12,2),
  sales_broker_fee    NUMERIC(12,2),
  sales_office        NUMERIC(12,2),
  ground_warranty     NUMERIC(12,2),
  survey_sales        NUMERIC(12,2),
  handover_docs       NUMERIC(12,2),
  consumption_tax     NUMERIC(12,2),
  personnel           NUMERIC(12,2),
  other_sales         NUMERIC(12,2),

  -- 4b. 月次・年次積み上げ
  prop_tax_annual     NUMERIC(12,2),   -- 固定資産税・都市計画税（万円/年）
  utilities_monthly   NUMERIC(12,2),   -- 水道光熱費（万円/月）
  fire_monthly        NUMERIC(12,2),   -- 火災保険料（万円/月）
  defect_lump         NUMERIC(12,2),   -- 瑕疵保険料（万円・一括）

  created_at          TIMESTAMPTZ DEFAULT NOW(),
  updated_at          TIMESTAMPTZ DEFAULT NOW(),

  CONSTRAINT cost_management_property_id_key UNIQUE (property_id)
);

-- RLS
ALTER TABLE cost_management ENABLE ROW LEVEL SECURITY;
CREATE POLICY "anon_all_cost" ON cost_management FOR ALL TO anon USING (true) WITH CHECK (true);
