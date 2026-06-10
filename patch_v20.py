"""
patch_v20.py
  - 掲載状況に「契約準備中」「契約済み」を追加
  - 詳細フォームに買付申込日・契約日・引渡し日を追加
  - 詳細ビューに契約情報を表示
実行: python patch_v20.py
"""
import sys

SRC = 'index.html'
with open(SRC, 'rb') as f:
    raw = f.read()
text = raw.replace(b'\r\n', b'\n').decode('utf-8')
original = text

# ════════════════════════════════════════════
# Step 1: CSS バッジを追加
# ════════════════════════════════════════════
find1 = '    .badge-negotiating{ font-size: 10px; background: #e67e00; color: #ffffff;       padding: 2px 8px; border-radius: 6px; font-weight: 600; white-space: nowrap; }'
repl1 = (
    '    .badge-negotiating{ font-size: 10px; background: #e67e00; color: #ffffff;       padding: 2px 8px; border-radius: 6px; font-weight: 600; white-space: nowrap; }\n'
    '    .badge-contract-prep { font-size: 10px; background: #cc6600; color: #ffffff;     padding: 2px 8px; border-radius: 6px; font-weight: 600; white-space: nowrap; }\n'
    '    .badge-contracted    { font-size: 10px; background: #1a6e1a; color: #ffffff;     padding: 2px 8px; border-radius: 6px; font-weight: 600; white-space: nowrap; }'
)
if find1 not in text:
    print('Step 1 FAILED'); sys.exit(1)
text = text.replace(find1, repl1, 1)
print('Step 1 OK: CSS バッジ追加')

# ════════════════════════════════════════════
# Step 2: statusOpts に新ステータスを追加
# ════════════════════════════════════════════
find2 = "  const statusOpts    = [['active','掲載中'],['negotiating','商談中'],['preparing','販売準備中'],['inactive','非掲載'],['sold','成約済']];"
repl2 = "  const statusOpts    = [['active','掲載中'],['negotiating','商談中'],['preparing','販売準備中'],['inactive','非掲載'],['contract_prep','契約準備中'],['contracted','契約済み'],['sold','成約済']];"
if find2 not in text:
    print('Step 2 FAILED'); sys.exit(1)
text = text.replace(find2, repl2, 1)
print('Step 2 OK: statusOpts 更新')

# ════════════════════════════════════════════
# Step 3: statusBadge に新ステータスを追加
# ════════════════════════════════════════════
find3 = (
    "  const map = {\n"
    "    active:   '<span class=\"badge-active\">掲載中</span>',\n"
    "    inactive: '<span class=\"badge-inactive\">非掲載</span>',\n"
    "    sold:     '<span class=\"badge-sold-s\">成約済</span>',\n"
    "    negotiating:'<span class=\"badge-negotiating\">商談中</span>',\n"
    "    preparing:'<span class=\"badge-preparing\">販売準備中</span>',\n"
    "  };"
)
repl3 = (
    "  const map = {\n"
    "    active:        '<span class=\"badge-active\">掲載中</span>',\n"
    "    inactive:      '<span class=\"badge-inactive\">非掲載</span>',\n"
    "    sold:          '<span class=\"badge-sold-s\">成約済</span>',\n"
    "    negotiating:   '<span class=\"badge-negotiating\">商談中</span>',\n"
    "    preparing:     '<span class=\"badge-preparing\">販売準備中</span>',\n"
    "    contract_prep: '<span class=\"badge-contract-prep\">契約準備中</span>',\n"
    "    contracted:    '<span class=\"badge-contracted\">契約済み</span>',\n"
    "  };"
)
if find3 not in text:
    print('Step 3 FAILED'); sys.exit(1)
text = text.replace(find3, repl3, 1)
print('Step 3 OK: statusBadge 更新')

# ════════════════════════════════════════════
# Step 4: statusLabel に新ステータスを追加
# ════════════════════════════════════════════
find4 = "  return { active:'掲載中', negotiating:'商談中', inactive:'非掲載', sold:'成約済', preparing:'販売準備中' }[s] || s;"
repl4 = "  return { active:'掲載中', negotiating:'商談中', inactive:'非掲載', sold:'成約済', preparing:'販売準備中', contract_prep:'契約準備中', contracted:'契約済み' }[s] || s;"
if find4 not in text:
    print('Step 4 FAILED'); sys.exit(1)
text = text.replace(find4, repl4, 1)
print('Step 4 OK: statusLabel 更新')

# ════════════════════════════════════════════
# Step 5: フォームに買付申込日・契約日・引渡し日を追加（売看板設置日の後）
# ════════════════════════════════════════════
find5 = (
    '        <div class="form-group">\n'
    '          <label>売看板設置日</label>\n'
    '          <input id="f-sign-start" type="date" class="qs-control" value="${d.sign_start_date||\'\'}">\n'
    '        </div>\n'
    '      </div>\n'
    '\n'
    '      <!-- 価格・取引 -->'
)
repl5 = (
    '        <div class="form-group">\n'
    '          <label>売看板設置日</label>\n'
    '          <input id="f-sign-start" type="date" class="qs-control" value="${d.sign_start_date||\'\'}">\n'
    '        </div>\n'
    '      </div>\n'
    '      <div class="form-row">\n'
    '        <div class="form-group">\n'
    '          <label>買付申込日</label>\n'
    '          <input id="f-offer-date" type="date" class="qs-control" value="${d.purchase_offer_date||\'\'}">\n'
    '        </div>\n'
    '        <div class="form-group">\n'
    '          <label>契約日</label>\n'
    '          <input id="f-contract-date" type="date" class="qs-control" value="${d.contract_date||\'\'}">\n'
    '        </div>\n'
    '      </div>\n'
    '      <div class="form-row">\n'
    '        <div class="form-group">\n'
    '          <label>引渡し日</label>\n'
    '          <input id="f-delivery-date" type="date" class="qs-control" value="${d.delivery_date||\'\'}">\n'
    '        </div>\n'
    '      </div>\n'
    '\n'
    '      <!-- 価格・取引 -->'
)
if find5 not in text:
    print('Step 5 FAILED'); sys.exit(1)
text = text.replace(find5, repl5, 1)
print('Step 5 OK: フォームに日付フィールド追加')

# ════════════════════════════════════════════
# Step 6: 詳細ビューに契約情報日付を表示（掲載開始日の後）
# ════════════════════════════════════════════
find6 = (
    "          ${(det.suumo_start_date||det.hp_start_date||det.sign_start_date)"
    " ? `<tr><th>掲載開始日</th><td style=\"font-size:12px;\">"
    "${det.suumo_start_date?'SUUMO: '+det.suumo_start_date+'\\u3000':''}"
    "${det.hp_start_date?'HP: '+det.hp_start_date+'\\u3000':''}"
    "${det.sign_start_date?'売看板: '+det.sign_start_date:''}</td></tr>` : ''}\n"
    "          <tr><th>取引態様</th>"
)
repl6 = (
    "          ${(det.suumo_start_date||det.hp_start_date||det.sign_start_date)"
    " ? `<tr><th>掲載開始日</th><td style=\"font-size:12px;\">"
    "${det.suumo_start_date?'SUUMO: '+det.suumo_start_date+'\\u3000':''}"
    "${det.hp_start_date?'HP: '+det.hp_start_date+'\\u3000':''}"
    "${det.sign_start_date?'売看板: '+det.sign_start_date:''}</td></tr>` : ''}\n"
    "          ${(det.purchase_offer_date||det.contract_date||det.delivery_date)"
    " ? `<tr><th>契約情報</th><td style=\"font-size:12px;\">"
    "${det.purchase_offer_date?'買付: '+det.purchase_offer_date+'\\u3000':''}"
    "${det.contract_date?'契約: '+det.contract_date+'\\u3000':''}"
    "${det.delivery_date?'引渡: '+det.delivery_date:''}</td></tr>` : ''}\n"
    "          <tr><th>取引態様</th>"
)
if find6 not in text:
    print('Step 6 FAILED'); sys.exit(1)
text = text.replace(find6, repl6, 1)
print('Step 6 OK: 詳細ビューに契約情報表示')

# ════════════════════════════════════════════
# Step 7: saveProperty に3つの日付フィールドを追加
# ════════════════════════════════════════════
find7 = "    sign_start_date:  document.getElementById('f-sign-start')?.value        || null,\n  };"
repl7 = (
    "    sign_start_date:         document.getElementById('f-sign-start')?.value         || null,\n"
    "    purchase_offer_date:     document.getElementById('f-offer-date')?.value          || null,\n"
    "    contract_date:           document.getElementById('f-contract-date')?.value       || null,\n"
    "    delivery_date:           document.getElementById('f-delivery-date')?.value       || null,\n"
    "  };"
)
if find7 not in text:
    print('Step 7 FAILED'); sys.exit(1)
text = text.replace(find7, repl7, 1)
print('Step 7 OK: saveProperty に日付フィールド追加')

# ════════════════════════════════════════════
# 書き出し
# ════════════════════════════════════════════
if text == original:
    print('ERROR: no changes'); sys.exit(1)

out = text.replace('\n', '\r\n').encode('utf-8')
with open(SRC, 'wb') as f:
    f.write(out)
print('\nAll steps OK')
