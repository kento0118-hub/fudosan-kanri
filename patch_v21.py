"""
patch_v21.py
  - saveProperty の properties update/insert エラー箇所に
    console.error ログを追加（ブラウザ DevTools でデバッグ可能にする）
  - migration_v19_diagnose.sql を同時に作成
実行: python patch_v21.py
"""
import sys

SRC = 'index.html'
with open(SRC, 'rb') as f:
    raw = f.read()
text = raw.replace(b'\r\n', b'\n').decode('utf-8')
original = text

# ════════════════════════════════════════════
# Step 1: properties UPDATE エラートーストにconsole.error追加
# ════════════════════════════════════════════
find1 = (
    "    const { error } = await db.from('properties').update(propData).eq('id', id);\n"
    "    if (error) { toast('保存失敗: ' + error.message, 'error'); return; }"
)
repl1 = (
    "    const { error } = await db.from('properties').update(propData).eq('id', id);\n"
    "    if (error) { console.error('[saveProperty update]', error, 'propData.status=', propData.status); toast('保存失敗: ' + error.message + ' [status=' + propData.status + ']', 'error'); return; }"
)
if find1 not in text:
    print('Step 1 FAILED'); sys.exit(1)
text = text.replace(find1, repl1, 1)
print('Step 1 OK: update エラートーストにログ追加')

# ════════════════════════════════════════════
# Step 2: properties INSERT エラートーストにconsole.error追加
# ════════════════════════════════════════════
find2 = (
    "    const { data, error } = await db.from('properties').insert(propData).select().single();\n"
    "    if (error) { toast('保存失敗: ' + error.message, 'error'); return; }"
)
repl2 = (
    "    const { data, error } = await db.from('properties').insert(propData).select().single();\n"
    "    if (error) { console.error('[saveProperty insert]', error, 'propData.status=', propData.status); toast('保存失敗: ' + error.message + ' [status=' + propData.status + ']', 'error'); return; }"
)
if find2 not in text:
    print('Step 2 FAILED'); sys.exit(1)
text = text.replace(find2, repl2, 1)
print('Step 2 OK: insert エラートーストにログ追加')

# ════════════════════════════════════════════
# 書き出し
# ════════════════════════════════════════════
if text == original:
    print('ERROR: no changes'); sys.exit(1)

out = text.replace('\n', '\r\n').encode('utf-8')
with open(SRC, 'wb') as f:
    f.write(out)
print('\nAll steps OK')
