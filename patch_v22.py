"""
patch_v22.py
  - 「契約準備中」バッジ: 背景黄色(#ffd700)・文字赤(#cc0000)に変更
  - 「契約済み」ステータスを全箇所から削除
実行: python patch_v22.py
"""
import sys

SRC = 'index.html'
with open(SRC, 'rb') as f:
    raw = f.read()
text = raw.replace(b'\r\n', b'\n').decode('utf-8')
original = text

# ════════════════════════════════════════════
# Step 1: CSS バッジ更新（契約準備中: 黄背景・赤文字 / 契約済み削除）
# ════════════════════════════════════════════
find1 = (
    '    .badge-contract-prep { font-size: 10px; background: #cc6600; color: #ffffff;     padding: 2px 8px; border-radius: 6px; font-weight: 600; white-space: nowrap; }\n'
    '    .badge-contracted    { font-size: 10px; background: #1a6e1a; color: #ffffff;     padding: 2px 8px; border-radius: 6px; font-weight: 600; white-space: nowrap; }'
)
repl1 = (
    '    .badge-contract-prep { font-size: 10px; background: #ffd700; color: #cc0000;     padding: 2px 8px; border-radius: 6px; font-weight: 600; white-space: nowrap; }'
)
if find1 not in text:
    print('Step 1 FAILED'); sys.exit(1)
text = text.replace(find1, repl1, 1)
print('Step 1 OK: CSS バッジ更新・契約済みCSS削除')

# ════════════════════════════════════════════
# Step 2: statusOpts から「契約済み」を削除
# ════════════════════════════════════════════
find2 = "  const statusOpts    = [['active','掲載中'],['negotiating','商談中'],['preparing','販売準備中'],['inactive','非掲載'],['contract_prep','契約準備中'],['contracted','契約済み'],['sold','成約済']];"
repl2 = "  const statusOpts    = [['active','掲載中'],['negotiating','商談中'],['preparing','販売準備中'],['inactive','非掲載'],['contract_prep','契約準備中'],['sold','成約済']];"
if find2 not in text:
    print('Step 2 FAILED'); sys.exit(1)
text = text.replace(find2, repl2, 1)
print('Step 2 OK: statusOpts から契約済み削除')

# ════════════════════════════════════════════
# Step 3: statusBadge map から「契約済み」を削除
# ════════════════════════════════════════════
find3 = (
    "    contract_prep: '<span class=\"badge-contract-prep\">契約準備中</span>',\n"
    "    contracted:    '<span class=\"badge-contracted\">契約済み</span>',"
)
repl3 = (
    "    contract_prep: '<span class=\"badge-contract-prep\">契約準備中</span>',"
)
if find3 not in text:
    print('Step 3 FAILED'); sys.exit(1)
text = text.replace(find3, repl3, 1)
print('Step 3 OK: statusBadge から契約済み削除')

# ════════════════════════════════════════════
# Step 4: statusLabel から「契約済み」を削除
# ════════════════════════════════════════════
find4 = "  return { active:'掲載中', negotiating:'商談中', inactive:'非掲載', sold:'成約済', preparing:'販売準備中', contract_prep:'契約準備中', contracted:'契約済み' }[s] || s;"
repl4 = "  return { active:'掲載中', negotiating:'商談中', inactive:'非掲載', sold:'成約済', preparing:'販売準備中', contract_prep:'契約準備中' }[s] || s;"
if find4 not in text:
    print('Step 4 FAILED'); sys.exit(1)
text = text.replace(find4, repl4, 1)
print('Step 4 OK: statusLabel から契約済み削除')

# ════════════════════════════════════════════
# 書き出し
# ════════════════════════════════════════════
if text == original:
    print('ERROR: no changes'); sys.exit(1)

out = text.replace('\n', '\r\n').encode('utf-8')
with open(SRC, 'wb') as f:
    f.write(out)
print('\nAll steps OK')
