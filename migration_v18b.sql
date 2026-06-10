-- ============================================================
-- migration_v18b.sql — properties.status CHECK制約を確実に更新
-- Supabase SQL Editor で実行してください
--
-- migration_v18.sql を実行済みでもエラーが続く場合はこちらを実行。
-- pg_constraint を参照して status 列の CHECK制約を名前に関わらず
-- すべて削除してから再作成します。
-- ============================================================

DO $$
DECLARE
  r RECORD;
BEGIN
  FOR r IN
    SELECT con.conname
    FROM pg_constraint con
    JOIN pg_class rel ON rel.oid = con.conrelid
    WHERE rel.relname = 'properties'
      AND con.contype = 'c'
      AND pg_get_constraintdef(con.oid) LIKE '%status IN%'
  LOOP
    RAISE NOTICE 'Dropping constraint: %', r.conname;
    EXECUTE format('ALTER TABLE properties DROP CONSTRAINT IF EXISTS %I', r.conname);
  END LOOP;
END $$;

ALTER TABLE properties
  ADD CONSTRAINT properties_status_check
  CHECK (status IN (
    'active',
    'inactive',
    'preparing',
    'negotiating',
    'contract_prep',
    'contracted',
    'sold'
  ));

-- 確認用：現在の status 列に関する CHECK制約を表示
SELECT con.conname, pg_get_constraintdef(con.oid) AS definition
FROM pg_constraint con
JOIN pg_class rel ON rel.oid = con.conrelid
WHERE rel.relname = 'properties'
  AND con.contype = 'c'
  AND pg_get_constraintdef(con.oid) LIKE '%status IN%';
