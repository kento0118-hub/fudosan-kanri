-- ============================================================
-- migration_v13.sql — 賃貸管理システム テーブル追加
-- Supabase SQL Editor で実行してください
-- ============================================================

-- 1. rental_properties: 賃貸物件基本情報
CREATE TABLE IF NOT EXISTS rental_properties (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  property_name    TEXT,
  code             TEXT,
  type             TEXT NOT NULL DEFAULT 'house'
                   CHECK (type IN ('land','house','building')),
  address          TEXT,
  map_url          TEXT,
  status           TEXT NOT NULL DEFAULT 'vacant'
                   CHECK (status IN ('recruiting','occupied','vacant','leaving','closed')),
  transaction_type TEXT CHECK (transaction_type IN ('managed','broker')),
  notes            TEXT,
  created_at       TIMESTAMPTZ DEFAULT NOW(),
  updated_at       TIMESTAMPTZ DEFAULT NOW()
);

-- 2. rental_details: 賃貸物件詳細
CREATE TABLE IF NOT EXISTS rental_details (
  id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  rental_id            UUID NOT NULL REFERENCES rental_properties(id) ON DELETE CASCADE,
  -- 物件概要
  land_area_sqm        NUMERIC(10,2),
  zoning               TEXT,
  other_laws           TEXT,
  water_supply         TEXT,
  sewage               TEXT,
  rights               TEXT,
  docs                 TEXT,           -- JSON 配列
  publish_date         DATE,
  suumo_listed         BOOLEAN NOT NULL DEFAULT FALSE,
  hp_listed            BOOLEAN NOT NULL DEFAULT FALSE,
  -- 建物情報
  building_area_sqm    NUMERIC(10,2),
  built_year           INTEGER,
  built_month          INTEGER,
  structure            TEXT,
  layout               TEXT,
  floors               TEXT,
  renovation_history   TEXT,
  -- 賃貸条件
  rent                 NUMERIC(12,2),  -- 月額賃料（円）
  management_fee       NUMERIC(12,2),  -- 管理費（円）
  common_fee           NUMERIC(12,2),  -- 共益費（円）
  deposit_months       NUMERIC(4,1),   -- 敷金（ヶ月）
  key_money_months     NUMERIC(4,1),   -- 礼金（ヶ月）
  contract_type        TEXT,           -- 普通賃貸・定期借家
  contract_period      TEXT,
  renewal_fee          TEXT,
  parking_available    BOOLEAN NOT NULL DEFAULT FALSE,
  parking_count        INTEGER,
  parking_fee          NUMERIC(10,2),  -- 月額駐車場代（円）
  created_at           TIMESTAMPTZ DEFAULT NOW(),
  updated_at           TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT rental_details_rental_id_key UNIQUE (rental_id)
);

-- 3. rental_units: ビル区画管理
CREATE TABLE IF NOT EXISTS rental_units (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  rental_id       UUID NOT NULL REFERENCES rental_properties(id) ON DELETE CASCADE,
  unit_number     TEXT,
  floor           TEXT,
  usage           TEXT,               -- 事務所・店舗・倉庫・その他
  area_sqm        NUMERIC(10,2),
  rent            NUMERIC(12,2),      -- 円
  management_fee  NUMERIC(12,2),      -- 円
  tenant_name     TEXT,
  contract_start  DATE,
  contract_end    DATE,
  unit_status     TEXT NOT NULL DEFAULT 'vacant'
                  CHECK (unit_status IN ('occupied','vacant','leaving')),
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 4. rental_tenants: 現在の入居者情報
CREATE TABLE IF NOT EXISTS rental_tenants (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  rental_id         UUID NOT NULL REFERENCES rental_properties(id) ON DELETE CASCADE,
  tenant_name       TEXT,
  company_name      TEXT,
  phone             TEXT,
  emergency_phone   TEXT,
  guarantor_name    TEXT,
  guarantor_phone   TEXT,
  contract_start    DATE,
  contract_end      DATE,
  insurance_status  TEXT,
  insurance_company TEXT,
  insurance_expiry  DATE,
  key_count         INTEGER,
  key_location      TEXT,
  notes             TEXT,
  created_at        TIMESTAMPTZ DEFAULT NOW(),
  updated_at        TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT rental_tenants_rental_id_key UNIQUE (rental_id)
);

-- 5. rental_tenant_history: 入居履歴
CREATE TABLE IF NOT EXISTS rental_tenant_history (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  rental_id       UUID NOT NULL REFERENCES rental_properties(id) ON DELETE CASCADE,
  tenant_name     TEXT,
  company_name    TEXT,
  contract_start  DATE,
  contract_end    DATE,
  move_out_reason TEXT,
  rent            NUMERIC(12,2),
  notes           TEXT,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 6. rental_costs: 収支管理（一括入力）
CREATE TABLE IF NOT EXISTS rental_costs (
  id                         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  rental_id                  UUID NOT NULL REFERENCES rental_properties(id) ON DELETE CASCADE,
  acquisition_date           DATE,
  acquisition_cost           NUMERIC(12,2),  -- 円（土地のみ）
  land_acquisition_cost      NUMERIC(12,2),  -- 円（住宅・ビル）
  building_acquisition_cost  NUMERIC(12,2),  -- 円（住宅・ビル、税込）
  broker_fee                 NUMERIC(12,2),
  acquisition_tax            NUMERIC(12,2),
  transfer_reg               NUMERIC(12,2),
  stamp_tax                  NUMERIC(12,2),
  survey_purchase            NUMERIC(12,2),
  other_purchase             NUMERIC(12,2),
  reform_cost                NUMERIC(12,2),  -- リフォーム工事費
  equipment_cost             NUMERIC(12,2),  -- 設備交換費
  ground_warranty            NUMERIC(12,2),  -- 地盤保証料
  interior_cost              NUMERIC(12,2),  -- 展示内装費
  other_construction         NUMERIC(12,2),
  reg_survey                 NUMERIC(12,2),
  farmland                   NUMERIC(12,2),
  dev_permit                 NUMERIC(12,2),
  other_reg                  NUMERIC(12,2),
  created_at                 TIMESTAMPTZ DEFAULT NOW(),
  updated_at                 TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT rental_costs_rental_id_key UNIQUE (rental_id)
);

-- 7. rental_cost_logs: 積み上げ・収入履歴
-- categories:
--   Irregular expense: repair / cleaning / inspection / advertising / personnel / other_expense
--   Annual expense:    tax_annual / fire_annual / hoa_annual
--   Monthly expense:   water_monthly / electricity_monthly / gas_monthly
--   Monthly income:    income_rent / income_mgmt / income_parking
CREATE TABLE IF NOT EXISTS rental_cost_logs (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  rental_id    UUID NOT NULL REFERENCES rental_properties(id) ON DELETE CASCADE,
  category     TEXT NOT NULL,
  record_year  INTEGER,
  record_month INTEGER,
  record_date  DATE,
  amount       NUMERIC(12,2) NOT NULL,
  memo         TEXT,
  photo_urls   TEXT,  -- JSON 配列
  created_at   TIMESTAMPTZ DEFAULT NOW()
);

-- 8. repair_logs: 修繕台帳
CREATE TABLE IF NOT EXISTS repair_logs (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  rental_id       UUID NOT NULL REFERENCES rental_properties(id) ON DELETE CASCADE,
  repair_date     DATE NOT NULL,
  location        TEXT,
  description     TEXT,
  contractor      TEXT,
  cost            NUMERIC(12,2),
  next_inspection DATE,
  photo_urls      TEXT,  -- JSON 配列
  notes           TEXT,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- RLS（全テーブル）
ALTER TABLE rental_properties     ENABLE ROW LEVEL SECURITY;
ALTER TABLE rental_details        ENABLE ROW LEVEL SECURITY;
ALTER TABLE rental_units          ENABLE ROW LEVEL SECURITY;
ALTER TABLE rental_tenants        ENABLE ROW LEVEL SECURITY;
ALTER TABLE rental_tenant_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE rental_costs          ENABLE ROW LEVEL SECURITY;
ALTER TABLE rental_cost_logs      ENABLE ROW LEVEL SECURITY;
ALTER TABLE repair_logs           ENABLE ROW LEVEL SECURITY;

CREATE POLICY "anon_all_rental_properties"     ON rental_properties     FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_all_rental_details"        ON rental_details        FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_all_rental_units"          ON rental_units          FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_all_rental_tenants"        ON rental_tenants        FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_all_rental_tenant_history" ON rental_tenant_history FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_all_rental_costs"          ON rental_costs          FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_all_rental_cost_logs"      ON rental_cost_logs      FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_all_repair_logs"           ON repair_logs           FOR ALL TO anon USING (true) WITH CHECK (true);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_rental_details_rental_id        ON rental_details        (rental_id);
CREATE INDEX IF NOT EXISTS idx_rental_units_rental_id          ON rental_units          (rental_id);
CREATE INDEX IF NOT EXISTS idx_rental_tenants_rental_id        ON rental_tenants        (rental_id);
CREATE INDEX IF NOT EXISTS idx_rental_history_rental_id        ON rental_tenant_history (rental_id);
CREATE INDEX IF NOT EXISTS idx_rental_costs_rental_id          ON rental_costs          (rental_id);
CREATE INDEX IF NOT EXISTS idx_rental_cost_logs_rental_cat     ON rental_cost_logs      (rental_id, category);
CREATE INDEX IF NOT EXISTS idx_repair_logs_rental_id           ON repair_logs           (rental_id);
CREATE INDEX IF NOT EXISTS idx_repair_logs_date                ON repair_logs           (repair_date DESC);
