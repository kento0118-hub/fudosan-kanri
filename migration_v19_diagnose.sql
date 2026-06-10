-- ============================================================
-- migration_v19_diagnose.sql — propertiesテーブルの状態診断
-- Supabase SQL Editor で実行して結果を確認してください
-- 変更は一切行いません（SELECT のみ）
-- ============================================================

-- 1. properties テーブルの全 CHECK 制約を表示
SELECT
  con.conname   AS "制約名",
  pg_get_constraintdef(con.oid) AS "定義"
FROM pg_constraint con
JOIN pg_class rel ON rel.oid = con.conrelid
JOIN pg_namespace ns ON ns.oid = rel.relnamespace
WHERE rel.relname = 'properties'
  AND ns.nspname  = 'public'
  AND con.contype = 'c'
ORDER BY con.conname;

-- 2. properties テーブルのトリガーを表示
SELECT
  trigger_name,
  event_manipulation,
  action_statement
FROM information_schema.triggers
WHERE event_object_schema = 'public'
  AND event_object_table  = 'properties';

-- 3. properties テーブルの RLS ポリシーを表示
SELECT
  polname AS "ポリシー名",
  polcmd  AS "コマンド",
  pg_get_expr(polqual,      polrelid) AS "USING 条件",
  pg_get_expr(polwithcheck, polrelid) AS "WITH CHECK 条件"
FROM pg_policy p
JOIN pg_class c ON c.oid = p.polrelid
WHERE c.relname = 'properties';
