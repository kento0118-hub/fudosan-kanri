-- ============================================================
-- migration_v20.sql — properties.status CHECK制約から「contracted」を削除
-- フロントエンドの「契約済み」削除に合わせてDB側も同期
-- Supabase SQL Editor で実行してください
-- ============================================================

-- 既存制約を名前に関わらずすべて削除
DO $$
DECLARE r RECORD;
BEGIN
  FOR r IN
    SELECT con.conname
    FROM pg_constraint con
    JOIN pg_class rel ON rel.oid = con.conrelid
    WHERE rel.relname = 'properties'
      AND con.contype = 'c'
      AND pg_get_constraintdef(con.oid) LIKE '%status IN%'
  LOOP
    EXECUTE format('ALTER TABLE properties DROP CONSTRAINT IF EXISTS %I', r.conname);
  END LOOP;
END $$;

-- contracted を除いた制約を再作成
ALTER TABLE properties
  ADD CONSTRAINT properties_status_check
  CHECK (status IN (
    'active',
    'inactive',
    'preparing',
    'negotiating',
    'contract_prep',
    'sold'
  ));

-- 確認
SELECT conname AS "制約名", pg_get_constraintdef(oid) AS "制約定義"
FROM pg_constraint
WHERE conrelid = 'properties'::regclass
  AND contype = 'c';
