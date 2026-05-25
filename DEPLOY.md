# デプロイ手順 — アジリノ不動産物件管理システム

---

## STEP 1：Supabase セットアップ（5分）

### 1-1. プロジェクト作成
1. https://supabase.com にアクセス → 「Start your project」
2. GitHub アカウントでサインイン
3. 「New project」→ 名前：`ajireno-fudosan`、パスワード設定、リージョン：`Northeast Asia (Tokyo)`
4. 「Create new project」→ 2〜3分待つ

### 1-2. テーブル作成
1. ダッシュボード左メニュー → 「SQL Editor」
2. `supabase_schema.sql` の内容をすべてコピー＆ペースト
3. 「Run」をクリック → エラーなければOK

### 1-3. Storage バケット作成
1. 左メニュー → 「Storage」→「New bucket」
2. 以下の2つを作成（どちらも **Public にチェック**）

| バケット名 | 公開設定 |
|---|---|
| `property-photos` | Public |
| `floor-plans` | Public |

3. SQL Editor で以下を実行（Storage RLS）：
```sql
CREATE POLICY "anon_storage_all" ON storage.objects
  FOR ALL TO anon USING (true) WITH CHECK (true);
```

### 1-4. 接続情報をメモ
「Settings」→「API」から以下をコピーしておく：
- **Project URL**：`https://xxxxxxxx.supabase.co`
- **anon public key**：`eyJ...` から始まる長い文字列

---

## STEP 2：index.html に接続情報を入力

`fudosan_kanri/index.html` を開き、冒頭の2行を書き換える：

```js
const SUPABASE_URL  = 'https://xxxxxxxx.supabase.co';  // ← Project URL
const SUPABASE_ANON = 'eyJ...';                         // ← anon key
```

---

## STEP 3：Vercel にデプロイ（3分）

### 方法A：ドラッグ＆ドロップ（最速・GitHubなし）

1. https://vercel.com にアクセス → 「Sign Up」（GitHubアカウント推奨）
2. ダッシュボード → 「Add New」→「Project」
3. 「Deploy without Git」→ `fudosan_kanri` フォルダをドラッグ＆ドロップ
4. 「Deploy」→ 1〜2分で完了
5. 発行されたURL（例：`https://ajireno-fudosan.vercel.app`）をチームに共有

### 方法B：GitHub 経由（更新が楽）

```bash
# 1. GitHubリポジトリ作成後
cd fudosan_kanri
git init
git add .
git commit -m "初回デプロイ"
git remote add origin https://github.com/YOUR_NAME/ajireno-fudosan.git
git push -u origin main

# 2. Vercel ダッシュボードでリポジトリを選択してデプロイ
# → index.html があるルートをそのまま指定
```

以降は `git push` するたびに自動で再デプロイされます。

---

## STEP 4：動作確認チェックリスト

- [ ] URLを開いて物件一覧が表示される
- [ ] 「＋ 土地を追加」で物件が登録できる
- [ ] 「＋ 中古住宅を追加」で物件が登録できる
- [ ] 写真をアップロードして表示される
- [ ] チェックリストのチェックが保存される
- [ ] 実施記録を追加できる
- [ ] 記録台帳で一覧表示・絞り込みできる

---

## よくある問題

| 症状 | 原因 | 対処 |
|---|---|---|
| 「Supabase 接続設定が必要です」と表示 | URLかKeyが未入力 | `index.html` の設定行を確認 |
| データが保存されない | RLS ポリシー未設定 | SQL Schema の RLS 部分を再実行 |
| 写真がアップロードできない | Storageバケット未作成 or RLS未設定 | STEP 1-3 を再確認 |
| 403エラー | anon key が間違っている | Settings → API で再確認 |

---

## ファイル構成

```
fudosan_kanri/
├── index.html          ← フロントエンド（これ1ファイルのみをデプロイ）
├── supabase_schema.sql ← Supabaseに実行するSQL
└── DEPLOY.md           ← この手順書
```

---

## 無料プランの制限（参考）

| サービス | 無料枠 | アジリノでの目安 |
|---|---|---|
| Supabase DB | 500MB | 物件数百件でも余裕 |
| Supabase Storage | 1GB | 写真約500〜1000枚分 |
| Vercel | 帯域100GB/月 | 問題なし |
