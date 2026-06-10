"""
patch_v23.py
  - 物件一覧の「掲載中」バッジ表示ロジック変更
    suumo_listed / hp_listed / for_sale_sign いずれかが true の場合は非表示
    全て false のときのみ statusBadge を表示
実行: python patch_v23.py
"""
import sys

SRC = 'index.html'
with open(SRC, 'rb') as f:
    raw = f.read()
text = raw.replace(b'\r\n', b'\n').decode('utf-8')
original = text

# ════════════════════════════════════════════
# Step 1: buildListTable の statusCell 内（テーブル行）
# ════════════════════════════════════════════
find1 = (
    "    return `<div style=\"display:flex;flex-direction:column;gap:3px;\">\n"
    "      ${statusBadge(p.status)}\n"
    "      ${d.suumo_listed   ? '<span class=\"badge-suumo\">SUUMO掲載</span>' : ''}\n"
    "      ${d.hp_listed      ? '<span class=\"badge-hp\">🌐 HP掲載</span>' : ''}\n"
    "      ${d.for_sale_sign  ? '<span class=\"badge-sign\">🪧 売看板あり</span>' : ''}"
)
repl1 = (
    "    return `<div style=\"display:flex;flex-direction:column;gap:3px;\">\n"
    "      ${(p.status === 'active' && (d.suumo_listed || d.hp_listed || d.for_sale_sign)) ? '' : statusBadge(p.status)}\n"
    "      ${d.suumo_listed   ? '<span class=\"badge-suumo\">SUUMO掲載</span>' : ''}\n"
    "      ${d.hp_listed      ? '<span class=\"badge-hp\">🌐 HP掲載</span>' : ''}\n"
    "      ${d.for_sale_sign  ? '<span class=\"badge-sign\">🪧 売看板あり</span>' : ''}"
)
if find1 not in text:
    print('Step 1 FAILED'); sys.exit(1)
text = text.replace(find1, repl1, 1)
print('Step 1 OK: buildListTable statusCell 更新')

# ════════════════════════════════════════════
# Step 2: buildListCards のカードヘッダ内
# ════════════════════════════════════════════
find2 = (
    "      <div class=\"prop-card-top\">\n"
    "        <span class=\"prop-card-code\">${esc(p.code||'')}</span>\n"
    "        ${typeBadge}\n"
    "        ${statusBadge(p.status)}\n"
    "      </div>"
)
repl2 = (
    "      <div class=\"prop-card-top\">\n"
    "        <span class=\"prop-card-code\">${esc(p.code||'')}</span>\n"
    "        ${typeBadge}\n"
    "        ${(p.status === 'active' && (d.suumo_listed || d.hp_listed || d.for_sale_sign)) ? '' : statusBadge(p.status)}\n"
    "      </div>"
)
if find2 not in text:
    print('Step 2 FAILED'); sys.exit(1)
text = text.replace(find2, repl2, 1)
print('Step 2 OK: buildListCards カードヘッダ 更新')

# ════════════════════════════════════════════
# 書き出し
# ════════════════════════════════════════════
if text == original:
    print('ERROR: no changes'); sys.exit(1)

out = text.replace('\n', '\r\n').encode('utf-8')
with open(SRC, 'wb') as f:
    f.write(out)
print('\nAll steps OK')
