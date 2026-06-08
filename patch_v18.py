"""
patch_v18.py
  - 物件詳細：取引態様「仲介」かつ価格あり → 仲介手数料を自動計算表示
  - 物件フォーム：価格入力時に仲介手数料の参考値をリアルタイム表示
  - 原価管理：仲介手数料「自動計算」ボタンを削除し手動入力のみに
実行: python patch_v18.py
"""
import sys

SRC = 'index.html'
with open(SRC, 'rb') as f:
    raw = f.read()
text = raw.replace(b'\r\n', b'\n').decode('utf-8')
original = text

# ════════════════════════════════════════════
# Step 1: calcCommission / calcBrokerFeeHint 関数を esc() の前に追加
# ════════════════════════════════════════════
FUNCS = """\
function calcCommission(priceManen) {
  const price = priceManen * 10000;
  let fee;
  if (price <= 2000000)      fee = price * 0.05;
  else if (price <= 4000000) fee = price * 0.04 + 20000;
  else                       fee = price * 0.03 + 60000;
  return { ex: Math.round(fee), inc: Math.round(fee * 1.1) };
}

function calcBrokerFeeHint() {
  const trans = document.getElementById('f-trans')?.value;
  const price = parseFloat(document.getElementById('f-price')?.value);
  const hint  = document.getElementById('brokerage-hint');
  if (!hint) return;
  if (trans !== 'broker' || !price || price <= 0) { hint.style.display = 'none'; return; }
  const fee = calcCommission(price);
  document.getElementById('bh-ex').textContent  = fee.ex.toLocaleString();
  document.getElementById('bh-inc').textContent = fee.inc.toLocaleString();
  hint.style.display = '';
}

"""

find1 = '\nfunction esc(s) {'
repl1 = '\n' + FUNCS + 'function esc(s) {'
if find1 not in text:
    print('Step 1 FAILED'); sys.exit(1)
text = text.replace(find1, repl1, 1)
print('Step 1 OK: calcCommission / calcBrokerFeeHint 追加')

# ════════════════════════════════════════════
# Step 2: onTransChange で calcBrokerFeeHint() も呼ぶ
# ════════════════════════════════════════════
find2 = (
    'function onTransChange() {\n'
    '  const transEl = document.getElementById(\'f-trans\');\n'
    '  const rowEl   = document.getElementById(\'brokerage-row\');\n'
    '  if (!transEl || !rowEl) return;\n'
    '  if (transEl.value === \'owner\' || transEl.value === \'managed\') {\n'
    '    rowEl.style.display = \'none\';\n'
    '  } else {\n'
    '    rowEl.style.display = \'\';\n'
    '  }\n'
    '}'
)
repl2 = (
    'function onTransChange() {\n'
    '  const transEl = document.getElementById(\'f-trans\');\n'
    '  const rowEl   = document.getElementById(\'brokerage-row\');\n'
    '  if (!transEl || !rowEl) return;\n'
    '  if (transEl.value === \'owner\' || transEl.value === \'managed\') {\n'
    '    rowEl.style.display = \'none\';\n'
    '  } else {\n'
    '    rowEl.style.display = \'\';\n'
    '  }\n'
    '  calcBrokerFeeHint();\n'
    '}'
)
if find2 not in text:
    print('Step 2 FAILED'); sys.exit(1)
text = text.replace(find2, repl2, 1)
print('Step 2 OK: onTransChange 修正')

# ════════════════════════════════════════════
# Step 3: 価格入力に oninput="calcBrokerFeeHint()" を追加
# ════════════════════════════════════════════
find3 = (
    '          <input id="f-price" type="number" class="qs-control" value="${p.price||\'\'}" placeholder="例：1200"\n'
    '>\n'
)
repl3 = (
    '          <input id="f-price" type="number" class="qs-control" value="${p.price||\'\'}" placeholder="例：1200"'
    ' oninput="calcBrokerFeeHint()">\n'
)
if find3 not in text:
    print('Step 3 FAILED'); sys.exit(1)
text = text.replace(find3, repl3, 1)
print('Step 3 OK: 価格入力に oninput 追加')

# ════════════════════════════════════════════
# Step 4: 仲介手数料フォーム行の後にヒント div を追加
# ════════════════════════════════════════════
find4 = (
    '      <div class="form-row" id="brokerage-row" style="${[\'owner\',\'managed\'].includes(d.transaction_type||\'\')'
    ' ? \'display:none;\' : \'\'}">\n'
    '        <div class="form-group" style="grid-column:span 2;">\n'
    '          <label>仲介手数料</label>\n'
    '          <input id="f-brokerage" type="text" class="qs-control" value="${esc(d.brokerage_fee||\'\')}"'
    ' placeholder="例：396,000円（税込）">\n'
    '        </div>\n'
    '      </div>\n'
)
repl4 = (
    '      <div class="form-row" id="brokerage-row" style="${[\'owner\',\'managed\'].includes(d.transaction_type||\'\')'
    ' ? \'display:none;\' : \'\'}">\n'
    '        <div class="form-group" style="grid-column:span 2;">\n'
    '          <label>仲介手数料<span style="font-size:10px;font-weight:400;color:var(--text-muted);margin-left:6px;">'
    '（手動入力）</span></label>\n'
    '          <input id="f-brokerage" type="text" class="qs-control" value="${esc(d.brokerage_fee||\'\')}"'
    ' placeholder="例：396,000円（税込）">\n'
    '        </div>\n'
    '      </div>\n'
    '      <div id="brokerage-hint" style="display:none;margin:-4px 0 12px;padding:10px 14px;'
    'background:var(--accent-dim);border-radius:8px;font-size:12px;color:var(--text-secondary);">\n'
    '        <span style="font-weight:600;color:var(--text-primary);">【宅建業法上限額】</span>　\n'
    '        税別: <span id="bh-ex" style="font-weight:700;color:var(--text-primary);"></span> 円　/　\n'
    '        税込: <span id="bh-inc" style="font-weight:700;color:var(--accent);"></span> 円\n'
    '      </div>\n'
)
if find4 not in text:
    print('Step 4 FAILED'); sys.exit(1)
text = text.replace(find4, repl4, 1)
print('Step 4 OK: 仲介手数料ヒント div 追加')

# ════════════════════════════════════════════
# Step 5: showPropertyModal の setTimeout に calcBrokerFeeHint() を追加
# ════════════════════════════════════════════
find5 = (
    '  setTimeout(() => {\n'
    '    if (!isLand) updateBuiltDisplay();\n'
    '    onStatusChange();\n'
    '  }, 50);\n'
    '}'
)
repl5 = (
    '  setTimeout(() => {\n'
    '    if (!isLand) updateBuiltDisplay();\n'
    '    onStatusChange();\n'
    '    calcBrokerFeeHint();\n'
    '  }, 50);\n'
    '}'
)
if find5 not in text:
    print('Step 5 FAILED'); sys.exit(1)
text = text.replace(find5, repl5, 1)
print('Step 5 OK: showPropertyModal の初期化に calcBrokerFeeHint 追加')

# ════════════════════════════════════════════
# Step 6: renderDetail に commFee 変数を追加
# ════════════════════════════════════════════
find6 = (
    "  const isLand = prop.type === 'land';\n\n"
    '  window._curProp = prop;\n'
    '  window._curDet  = det;'
)
repl6 = (
    "  const isLand = prop.type === 'land';\n"
    '  const commFee = (det.transaction_type === \'broker\' && prop.price)\n'
    '    ? calcCommission(prop.price) : null;\n\n'
    '  window._curProp = prop;\n'
    '  window._curDet  = det;'
)
if find6 not in text:
    print('Step 6 FAILED'); sys.exit(1)
text = text.replace(find6, repl6, 1)
print('Step 6 OK: commFee 変数を renderDetail に追加')

# ════════════════════════════════════════════
# Step 7: 詳細ビューの仲介手数料表示を自動計算に変更
# ════════════════════════════════════════════
find7 = (
    "          ${det.brokerage_fee ? `<tr><th>仲介手数料</th><td>${esc(det.brokerage_fee)}</td></tr>` : ''}"
)
repl7 = (
    '          ${commFee ? `<tr>'
    '<th>仲介手数料<br><span style="font-size:10px;font-weight:400;color:var(--text-muted);">'
    '（宅建業法上限）</span></th>'
    '<td>'
    '<div>${commFee.ex.toLocaleString()} 円 '
    '<span style="font-size:11px;color:var(--text-muted);">税別</span></div>'
    '<div style="font-weight:700;color:var(--accent);font-size:14px;">'
    '${commFee.inc.toLocaleString()} 円 '
    '<span style="font-size:11px;font-weight:400;color:var(--text-muted);">税込</span></div>'
    "${det.brokerage_fee ? `<div style=\\'font-size:11px;color:var(--text-muted);margin-top:2px;\\'>記録値: ${esc(det.brokerage_fee)}</div>` : ''}"
    '</td></tr>`'
    " : det.brokerage_fee ? `<tr><th>仲介手数料</th><td>${esc(det.brokerage_fee)}</td></tr>` : ''}"
)
if find7 not in text:
    print('Step 7 FAILED'); sys.exit(1)
text = text.replace(find7, repl7, 1)
print('Step 7 OK: 詳細ビューの仲介手数料自動計算表示')

# ════════════════════════════════════════════
# Step 8: 原価管理の「自動計算」ボタンを削除
# ════════════════════════════════════════════
find8 = (
    '      <td style="padding:5px 10px 5px 0;font-size:13px;color:var(--text-secondary);">不動産仲介手数料\n'
    '        <button type="button" onclick="calcPurchaseBrokerFee()"\n'
    '          style="margin-left:6px;font-size:10px;color:var(--accent);background:var(--accent-dim);\n'
    '            border:none;border-radius:4px;padding:1px 6px;cursor:pointer;vertical-align:middle;">自動計算</button>\n'
    '      </td>\n'
)
repl8 = (
    '      <td style="padding:5px 10px 5px 0;font-size:13px;color:var(--text-secondary);">不動産仲介手数料</td>\n'
)
if find8 not in text:
    print('Step 8 FAILED'); sys.exit(1)
text = text.replace(find8, repl8, 1)
print('Step 8 OK: 原価管理の自動計算ボタン削除')

# ════════════════════════════════════════════
# Step 9: calcPurchaseBrokerFee() 関数本体を削除
# ════════════════════════════════════════════
find9 = (
    'function calcPurchaseBrokerFee() {\n'
    '  const isHouse = document.getElementById(\'c-land-acq-cost\') !== null;\n'
    '  const baseVal = isHouse\n'
    '    ? (parseFloat(document.getElementById(\'c-land-acq-cost\')?.value) || 0)\n'
    '    : (parseFloat(document.getElementById(\'c-acq-cost\')?.value) || 0);\n'
    '  if (baseVal <= 0) return;\n'
    '  const fee = Math.round((baseVal * 0.03 + 60000) * 1.1);\n'
    '  const feeEl = document.getElementById(\'c-broker-fee\');\n'
    '  if (feeEl) { feeEl.value = fee; calcCostSummary(); }\n'
    '}\n'
)
repl9 = ''
if find9 not in text:
    print('Step 9 FAILED'); sys.exit(1)
text = text.replace(find9, repl9, 1)
print('Step 9 OK: calcPurchaseBrokerFee 関数削除')

# ════════════════════════════════════════════
# 書き出し
# ════════════════════════════════════════════
if text == original:
    print('ERROR: no changes'); sys.exit(1)

out = text.replace('\n', '\r\n').encode('utf-8')
with open(SRC, 'wb') as f:
    f.write(out)
print('\nAll steps OK')
