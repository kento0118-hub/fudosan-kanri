-- ============================================================
-- 株式会社アジリノ 不動産物件管理システム
-- Supabase Schema  (PostgreSQL 15)
-- ============================================================

-- ────────────────────────────────────────
-- 1. 物件基本情報
-- ────────────────────────────────────────
CREATE TABLE properties (
  id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  type        TEXT        NOT NULL CHECK (type IN ('land','house')),
  code        TEXT,
  status      TEXT        NOT NULL DEFAULT 'active'
                CHECK (status IN ('active','inactive','sold')),
  address     TEXT,
  price       NUMERIC(12,0),
  is_sold     BOOLEAN     NOT NULL DEFAULT FALSE,
  notes       TEXT,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE  properties         IS '物件基本情報';
COMMENT ON COLUMN properties.type    IS 'land=土地 / house=中古住宅';
COMMENT ON COLUMN properties.status  IS 'active=掲載中 / inactive=非掲載 / sold=成約済';
COMMENT ON COLUMN properties.price   IS '販売価格（万円）';

-- ────────────────────────────────────────
-- 2. 物件詳細（土地・中古住宅を1テーブルに）
-- ────────────────────────────────────────
CREATE TABLE property_details (
  id                   UUID    PRIMARY KEY DEFAULT gen_random_uuid(),
  property_id          UUID    NOT NULL UNIQUE REFERENCES properties(id) ON DELETE CASCADE,
  -- 共通フィールド
  school_elementary    TEXT,   -- 学区（小学校）
  school_junior        TEXT,   -- 学区（中学校）
  water_supply         TEXT,   -- 上水道
  sewage               TEXT,   -- 下水道
  buried_artifacts     TEXT,   -- 埋蔵
  documents            TEXT,   -- 取得書類
  -- 土地専用
  area_sqm             NUMERIC(10,2),  -- 面積（㎡）
  area_tsubo           NUMERIC(10,2),  -- 面積（坪）
  land_condition       TEXT,           -- 土地状況
  zoning               TEXT,           -- 用途地域
  other_laws           TEXT,           -- 他の法令
  -- 中古住宅専用
  land_area_sqm        NUMERIC(10,2),  -- 土地面積（㎡）
  land_area_tsubo      NUMERIC(10,2),  -- 土地面積（坪）
  building_area_sqm    NUMERIC(10,2),  -- 建物面積（㎡）
  building_area_tsubo  NUMERIC(10,2),  -- 建物面積（坪）
  built_date           TEXT,           -- 築年月
  floor_plan           TEXT,           -- 間取
  floor_plan_image     TEXT            -- 間取り図 Storage URL
);

-- ────────────────────────────────────────
-- 3. 物件写真（最大6枚）
-- ────────────────────────────────────────
CREATE TABLE property_photos (
  id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  property_id  UUID        NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
  url          TEXT        NOT NULL,
  storage_path TEXT        NOT NULL,
  order_index  INTEGER     NOT NULL DEFAULT 0,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ────────────────────────────────────────
-- 4. チェックリスト項目マスタ
-- ────────────────────────────────────────
CREATE TABLE checklist_items (
  id            UUID    PRIMARY KEY DEFAULT gen_random_uuid(),
  property_type TEXT    NOT NULL CHECK (property_type IN ('land','house','both')),
  season        TEXT    NOT NULL CHECK (season IN ('spring','summer','fall','winter','all')),
  label         TEXT    NOT NULL,
  order_index   INTEGER NOT NULL DEFAULT 0
);
COMMENT ON TABLE checklist_items IS '季節別チェックリスト項目マスタ';

-- ────────────────────────────────────────
-- 5. チェック状態（物件ごと）
-- ────────────────────────────────────────
CREATE TABLE checklist_checks (
  id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  property_id  UUID        NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
  item_id      UUID        NOT NULL REFERENCES checklist_items(id) ON DELETE CASCADE,
  is_checked   BOOLEAN     NOT NULL DEFAULT FALSE,
  checked_at   TIMESTAMPTZ,
  UNIQUE(property_id, item_id)
);

-- ────────────────────────────────────────
-- 6. 実施記録（草刈り・除雪など）
-- ────────────────────────────────────────
CREATE TABLE task_logs (
  id                   UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  property_id          UUID        NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
  task_type            TEXT        NOT NULL,    -- 草刈り / 除雪 / 清掃 / 点検 など
  performed_date       DATE        NOT NULL,
  next_scheduled_date  DATE,
  memo                 TEXT,
  created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ────────────────────────────────────────
-- 7. メモ
-- ────────────────────────────────────────
CREATE TABLE notes (
  id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  property_id  UUID        NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
  content      TEXT        NOT NULL,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- インデックス
-- ============================================================
CREATE INDEX idx_properties_type        ON properties(type);
CREATE INDEX idx_properties_status      ON properties(status);
CREATE INDEX idx_properties_is_sold     ON properties(is_sold);
CREATE INDEX idx_property_photos_prop   ON property_photos(property_id);
CREATE INDEX idx_checklist_checks_prop  ON checklist_checks(property_id);
CREATE INDEX idx_task_logs_prop         ON task_logs(property_id);
CREATE INDEX idx_task_logs_date         ON task_logs(performed_date DESC);

-- ============================================================
-- updated_at 自動更新トリガー
-- ============================================================
CREATE OR REPLACE FUNCTION _update_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$;

CREATE TRIGGER trg_properties_updated_at
  BEFORE UPDATE ON properties
  FOR EACH ROW EXECUTE FUNCTION _update_updated_at();

-- ============================================================
-- RLS（Row Level Security）
-- ログイン不要・URL共有運用のため anon に全権限
-- ============================================================
ALTER TABLE properties       ENABLE ROW LEVEL SECURITY;
ALTER TABLE property_details ENABLE ROW LEVEL SECURITY;
ALTER TABLE property_photos  ENABLE ROW LEVEL SECURITY;
ALTER TABLE checklist_items  ENABLE ROW LEVEL SECURITY;
ALTER TABLE checklist_checks ENABLE ROW LEVEL SECURITY;
ALTER TABLE task_logs        ENABLE ROW LEVEL SECURITY;
ALTER TABLE notes            ENABLE ROW LEVEL SECURITY;

CREATE POLICY "anon_all" ON properties       FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_all" ON property_details FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_all" ON property_photos  FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_all" ON checklist_items  FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_all" ON checklist_checks FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_all" ON task_logs        FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_all" ON notes            FOR ALL TO anon USING (true) WITH CHECK (true);

-- ============================================================
-- チェックリスト初期データ
-- ============================================================

-- ── 土地 ──
INSERT INTO checklist_items (property_type, season, label, order_index) VALUES
  ('land','spring','境界杭・境界標の確認',1),
  ('land','spring','除草・整地確認',2),
  ('land','spring','排水状況確認',3),
  ('land','summer','草刈り（1回目）',1),
  ('land','summer','雑草繁茂状況の確認',2),
  ('land','summer','不法投棄の有無確認',3),
  ('land','fall',  '草刈り（2回目）',1),
  ('land','fall',  '枯れ葉・落ち葉の清掃',2),
  ('land','fall',  '排水路の詰まり確認',3),
  ('land','winter','除雪対応確認',1),
  ('land','winter','凍結・融雪リスク確認',2),
  ('land','winter','近隣への影響（雪害）確認',3),
  ('land','all',   '掲載状況の確認・更新',1),
  ('land','all',   '取得書類の整理・保管確認',2);

-- ── 中古住宅 ──
INSERT INTO checklist_items (property_type, season, label, order_index) VALUES
  ('house','spring','外壁・屋根の目視点検',1),
  ('house','spring','給排水管の通水確認',2),
  ('house','spring','庭・外構の除草',3),
  ('house','spring','窓・サッシの開閉確認',4),
  ('house','summer','草刈り（庭・外周）',1),
  ('house','summer','通風・換気確認',2),
  ('house','summer','防虫対策（床下・天井裏）',3),
  ('house','summer','雨漏り確認（大雨後）',4),
  ('house','fall',  '落ち葉清掃・雨樋点検',1),
  ('house','fall',  '外部水道の凍結防止準備',2),
  ('house','fall',  '暖房設備の動作確認',3),
  ('house','winter','除雪（屋根・外構）',1),
  ('house','winter','凍結防止（水道管・メーター）',2),
  ('house','winter','結露・カビの確認',3),
  ('house','winter','雪害リスク箇所の点検',4),
  ('house','all',   '掲載状況の確認・更新',1),
  ('house','all',   '取得書類の整理・保管',2),
  ('house','all',   '電気・ガス・水道の開閉確認',3);

-- ============================================================
-- Storage バケット（ダッシュボードで手動作成）
-- ============================================================
-- 手順:
--   Supabase ダッシュボード → Storage → New bucket
--   1) 名前: property-photos  公開: ON（Public bucket）
--   2) 名前: floor-plans      公開: ON（Public bucket）
--
-- Storage RLS ポリシー（各バケット）:
--   INSERT / SELECT / DELETE → anon に許可
--   SQLエディタで実行:
--
-- INSERT INTO storage.buckets (id, name, public) VALUES
--   ('property-photos', 'property-photos', true),
--   ('floor-plans',     'floor-plans',     true)
-- ON CONFLICT DO NOTHING;
--
-- CREATE POLICY "anon_storage_all" ON storage.objects
--   FOR ALL TO anon USING (true) WITH CHECK (true);
