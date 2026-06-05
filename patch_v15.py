import os, re

base     = os.path.dirname(os.path.abspath(__file__))
html_path = os.path.join(base, 'index.html')
js_path   = os.path.join(base, 'feature_v15.js')

with open(html_path, 'rb') as f:
    raw = f.read()
crlf = b'\r\n' in raw
text = raw.decode('utf-8').replace('\r\n', '\n')

with open(js_path, 'rb') as f:
    feature_js = f.read().decode('utf-8').replace('\r\n', '\n')

# ─────────────────────────────────────────────────────────────
# 1. 【面積表示】詳細ビュー — 土地：㎡+坪を1行に
# ─────────────────────────────────────────────────────────────
old1 = (
    "            <tr><th>面積（㎡）</th><td>${det.area_sqm??'—'}</td></tr>\n"
    "            <tr><th>面積（坪）</th><td>${det.area_tsubo??'—'}</td></tr>"
)
new1 = (
    "            <tr><th>面積</th><td>${det.area_sqm != null"
    " ? det.area_sqm+' ㎡　/　'+(det.area_sqm/3.30579).toFixed(2)+' 坪' : '—'}</td></tr>"
)
if old1 not in text:
    raise RuntimeError('1: land area rows not found')
text = text.replace(old1, new1, 1)
print('1. 土地面積表示変更 OK')

# ─────────────────────────────────────────────────────────────
# 2. 【面積表示】詳細ビュー — 住宅：㎡+坪を1行に
# ─────────────────────────────────────────────────────────────
old2 = (
    "            <tr><th>土地面積（㎡）</th><td>${det.land_area_sqm??'—'}</td></tr>\n"
    "            <tr><th>土地面積（坪）</th><td>${det.land_area_tsubo??'—'}</td></tr>\n"
    "            <tr><th>建物面積（㎡）</th><td>${det.building_area_sqm??'—'}</td></tr>\n"
    "            <tr><th>建物面積（坪）</th><td>${det.building_area_tsubo??'—'}</td></tr>"
)
new2 = (
    "            <tr><th>土地面積</th><td>${det.land_area_sqm != null"
    " ? det.land_area_sqm+' ㎡　/　'+(det.land_area_sqm/3.30579).toFixed(2)+' 坪' : '—'}</td></tr>\n"
    "            <tr><th>建物面積</th><td>${det.building_area_sqm != null"
    " ? det.building_area_sqm+' ㎡　/　'+(det.building_area_sqm/3.30579).toFixed(2)+' 坪' : '—'}</td></tr>"
)
if old2 not in text:
    raise RuntimeError('2: house area rows not found')
text = text.replace(old2, new2, 1)
print('2. 住宅面積表示変更 OK')

# ─────────────────────────────────────────────────────────────
# 3. 【面積表示】フォーム — sqmInput ヘルパーを更新
# ─────────────────────────────────────────────────────────────
old3 = (
    "  const sqmInput = (idSuffix, sqmVal, tsuboId) =>\n"
    "    `<input id=\"${idSuffix}\" type=\"number\" step=\"0.01\" class=\"qs-control\"\n"
    "       value=\"${sqmVal||''}\"\n"
    "       oninput=\"const t=document.getElementById('${tsuboId}');if(t)t.value=this.value?(this.value*0.3025).toFixed(2):''\">`;"
)
new3 = (
    "  const sqmInput = (idSuffix, sqmVal, tsuboId) =>\n"
    "    `<div style=\"display:flex;align-items:center;gap:8px;\">\n"
    "       <input id=\"${idSuffix}\" type=\"number\" step=\"0.01\" class=\"qs-control\" style=\"flex:1;\"\n"
    "         value=\"${sqmVal||''}\"\n"
    "         oninput=\"(function(){var v=parseFloat(this.value);"
    "var d=document.getElementById('${tsuboId}_d');"
    "var h=document.getElementById('${tsuboId}');"
    "var t=v>0?(v/3.30579).toFixed(2):'';"
    "if(d)d.textContent=t?t+' 坪':'—';"
    "if(h)h.value=t;}).call(this)\">\n"
    "       <span id=\"${tsuboId}_d\" style=\"font-size:12px;color:var(--accent);white-space:nowrap;font-weight:600;min-width:70px;\">"
    "${sqmVal?(sqmVal/3.30579).toFixed(2)+' 坪':'—'}</span>\n"
    "       <input type=\"hidden\" id=\"${tsuboId}\" value=\"${sqmVal?(sqmVal/3.30579).toFixed(2):''}\">  \n"
    "     </div>`;"
)
if old3 not in text:
    raise RuntimeError('3: sqmInput helper not found')
text = text.replace(old3, new3, 1)
print('3. sqmInput更新 OK')

# ─────────────────────────────────────────────────────────────
# 4. 【面積表示】フォーム — 土地の坪入力欄を削除
# ─────────────────────────────────────────────────────────────
old4 = (
    "      <div class=\"form-group\">\n"
    "          <label>面積（坪）</label>\n"
    "          <input id=\"f-area-tsubo\" type=\"number\" step=\"0.01\" class=\"qs-control\" value=\"${d.area_tsubo||''}\">\n"
    "        </div>"
)
new4 = ""
if old4 not in text:
    raise RuntimeError('4: land tsubo input not found')
text = text.replace(old4, new4, 1)
print('4. 土地坪入力欄削除 OK')

# ─────────────────────────────────────────────────────────────
# 5. 【面積表示】フォーム — 住宅・土地面積の坪入力欄を削除
# ─────────────────────────────────────────────────────────────
old5 = (
    "      <div class=\"form-group\">\n"
    "          <label>土地面積（坪）</label>\n"
    "          <input id=\"f-land-tsubo\" type=\"number\" step=\"0.01\" class=\"qs-control\" value=\"${d.land_area_tsubo||''}\">\n"
    "        </div>"
)
new5 = ""
if old5 not in text:
    raise RuntimeError('5: land-tsubo input not found')
text = text.replace(old5, new5, 1)
print('5. 住宅土地坪入力欄削除 OK')

# ─────────────────────────────────────────────────────────────
# 6. 【面積表示】フォーム — 住宅・建物面積の坪入力欄を削除
# ─────────────────────────────────────────────────────────────
old6 = (
    "      <div class=\"form-group\">\n"
    "          <label>建物面積（坪）</label>\n"
    "          <input id=\"f-bld-tsubo\" type=\"number\" step=\"0.01\" class=\"qs-control\" value=\"${d.building_area_tsubo||''}\">\n"
    "        </div>"
)
new6 = ""
if old6 not in text:
    raise RuntimeError('6: bld-tsubo input not found')
text = text.replace(old6, new6, 1)
print('6. 建物坪入力欄削除 OK')

# ─────────────────────────────────────────────────────────────
# 7. 【面積表示】saveProperty — 坪を㎡から自動計算
# ─────────────────────────────────────────────────────────────
old7 = (
    "  if (isLand) {\n"
    "    detData.area_sqm       = parseFloat(document.getElementById('f-area-sqm')?.value)    || null;\n"
    "    detData.area_tsubo     = parseFloat(document.getElementById('f-area-tsubo')?.value)  || null;\n"
    "    detData.land_condition = document.getElementById('f-land-cond')?.value.trim()        || null;\n"
    "  } else {\n"
    "    detData.land_area_sqm       = parseFloat(document.getElementById('f-land-sqm')?.value)   || null;\n"
    "    detData.land_area_tsubo     = parseFloat(document.getElementById('f-land-tsubo')?.value)  || null;\n"
    "    detData.building_area_sqm   = parseFloat(document.getElementById('f-bld-sqm')?.value)     || null;\n"
    "    detData.building_area_tsubo = parseFloat(document.getElementById('f-bld-tsubo')?.value)   || null;"
)
new7 = (
    "  const _toTsubo = v => v ? parseFloat((v/3.30579).toFixed(2)) : null;\n"
    "  if (isLand) {\n"
    "    detData.area_sqm       = parseFloat(document.getElementById('f-area-sqm')?.value)    || null;\n"
    "    detData.area_tsubo     = _toTsubo(detData.area_sqm);\n"
    "    detData.land_condition = document.getElementById('f-land-cond')?.value.trim()        || null;\n"
    "  } else {\n"
    "    detData.land_area_sqm       = parseFloat(document.getElementById('f-land-sqm')?.value)   || null;\n"
    "    detData.land_area_tsubo     = _toTsubo(detData.land_area_sqm);\n"
    "    detData.building_area_sqm   = parseFloat(document.getElementById('f-bld-sqm')?.value)     || null;\n"
    "    detData.building_area_tsubo = _toTsubo(detData.building_area_sqm);"
)
if old7 not in text:
    raise RuntimeError('7: save tsubo code not found')
text = text.replace(old7, new7, 1)
print('7. 坪自動計算(save) OK')

# ─────────────────────────────────────────────────────────────
# 8. 【顧客情報】詳細ヘッダーに「顧客情報」ボタンを追加
# ─────────────────────────────────────────────────────────────
old8 = (
    "      <div style=\"display:flex;gap:8px;\">\n"
    "        <button class=\"btn-secondary\" onclick=\"showCost('${id}')\">📊 原価管理</button>\n"
    "        <button class=\"btn-primary\" onclick=\"openEditModal()\">✏️ 編集</button>\n"
    "        <button class=\"btn-danger\"  onclick=\"confirmDelete('${id}')\">🗑 削除</button>\n"
    "      </div>"
)
new8 = (
    "      <div style=\"display:flex;gap:8px;flex-wrap:wrap;\">\n"
    "        ${det.transaction_type === 'broker' ? `<button class=\"btn-secondary\" onclick=\"showSellerInfo('${id}')\">👤 顧客情報</button>` : ''}\n"
    "        <button class=\"btn-secondary\" onclick=\"showCost('${id}')\">📊 原価管理</button>\n"
    "        <button class=\"btn-primary\" onclick=\"openEditModal()\">✏️ 編集</button>\n"
    "        <button class=\"btn-danger\"  onclick=\"confirmDelete('${id}')\">🗑 削除</button>\n"
    "      </div>"
)
if old8 not in text:
    raise RuntimeError('8: detail header buttons not found')
text = text.replace(old8, new8, 1)
print('8. 顧客情報ボタン追加 OK')

# ─────────────────────────────────────────────────────────────
# 9. 【値下げ履歴】renderDetail — Promise.all に price_history を追加
# ─────────────────────────────────────────────────────────────
old9 = (
    "  const [propRes, photosRes, checksRes, logsRes] = await Promise.all([\n"
    "    db.from('properties').select('*, property_details(*)').eq('id', id).single(),\n"
    "    db.from('property_photos').select('*').eq('property_id', id).order('order_index'),\n"
    "    db.from('checklist_checks').select('*').eq('property_id', id),\n"
    "    db.from('task_logs').select('*').eq('property_id', id).order('performed_date', { ascending: false }),\n"
    "  ]);"
)
new9 = (
    "  const [propRes, photosRes, checksRes, logsRes, priceHistRes] = await Promise.all([\n"
    "    db.from('properties').select('*, property_details(*)').eq('id', id).single(),\n"
    "    db.from('property_photos').select('*').eq('property_id', id).order('order_index'),\n"
    "    db.from('checklist_checks').select('*').eq('property_id', id),\n"
    "    db.from('task_logs').select('*').eq('property_id', id).order('performed_date', { ascending: false }),\n"
    "    db.from('price_history').select('*').eq('property_id', id).order('recorded_date', { ascending: false }),\n"
    "  ]);"
)
if old9 not in text:
    raise RuntimeError('9: Promise.all not found')
text = text.replace(old9, new9, 1)
print('9. Promise.all追加 OK')

# ─────────────────────────────────────────────────────────────
# 10. 【値下げ履歴】renderDetail — priceHistory 変数を追加
# ─────────────────────────────────────────────────────────────
old10 = (
    "  const prop   = propRes.data;\n"
    "  const photos = photosRes.data || [];\n"
    "  const checks = checksRes.data || [];\n"
    "  const logs   = logsRes.data   || [];\n"
    "  const det    = prop.property_details || {};"
)
new10 = (
    "  const prop         = propRes.data;\n"
    "  const photos       = photosRes.data   || [];\n"
    "  const checks       = checksRes.data   || [];\n"
    "  const logs         = logsRes.data     || [];\n"
    "  const priceHistory = priceHistRes.data || [];\n"
    "  const det          = prop.property_details || {};"
)
if old10 not in text:
    raise RuntimeError('10: data destructuring not found')
text = text.replace(old10, new10, 1)
print('10. priceHistory変数追加 OK')

# ─────────────────────────────────────────────────────────────
# 11. 【値下げ履歴】詳細ビューに値下げ履歴セクションを追加
#     「<!-- 写真 -->」の直前に挿入
# ─────────────────────────────────────────────────────────────
old11 = "    <!-- 写真 -->\n    <div class=\"section\" style=\"margin-bottom:16px;\">\n      <div class=\"section-title\"><span class=\"icon\">📷</span>物件写真</div>"
new11 = (
    "    <!-- 値下げ履歴 -->\n"
    "    <div class=\"section\" style=\"margin-bottom:16px;\">\n"
    "      <div class=\"section-title\" style=\"display:flex;justify-content:space-between;align-items:center;\">\n"
    "        <span><span class=\"icon\">📉</span>値下げ履歴</span>\n"
    "        <button class=\"btn-sm\" onclick=\"openPriceHistoryModal('${id}',${prop.price||0})\">値下げを記録</button>\n"
    "      </div>\n"
    "      ${priceHistory.length === 0\n"
    "        ? '<div style=\"font-size:12px;color:var(--text-muted);padding:8px 0;\">履歴がありません</div>'\n"
    "        : `<div style=\"overflow-x:auto;\"><table class=\"data-table\">\n"
    "            <thead><tr><th>日付</th><th>変更前</th><th>変更後</th><th>メモ</th><th></th></tr></thead>\n"
    "            <tbody>\n"
    "              ${priceHistory.map(h => `<tr>\n"
    "                <td style=\"white-space:nowrap;\">${h.recorded_date||'—'}</td>\n"
    "                <td style=\"white-space:nowrap;\">${h.old_price!=null?h.old_price.toLocaleString()+'万円':'—'}</td>\n"
    "                <td style=\"white-space:nowrap;font-weight:600;\">${h.new_price!=null?h.new_price.toLocaleString()+'万円':'—'}</td>\n"
    "                <td>${esc(h.memo||'')}</td>\n"
    "                <td><button class=\"btn-sm btn-danger\" onclick=\"deletePriceHistory('${h.id}','${id}')\">削除</button></td>\n"
    "              </tr>`).join('')}\n"
    "            </tbody>\n"
    "           </table></div>`\n"
    "      }\n"
    "    </div>\n\n"
    "    <!-- 写真 -->\n"
    "    <div class=\"section\" style=\"margin-bottom:16px;\">\n"
    "      <div class=\"section-title\"><span class=\"icon\">📷</span>物件写真</div>"
)
if old11 not in text:
    raise RuntimeError('11: photo section not found')
text = text.replace(old11, new11, 1)
print('11. 値下げ履歴セクション追加 OK')

# ─────────────────────────────────────────────────────────────
# 12. 【物件マップ】ナビに「物件マップ」を追加
# ─────────────────────────────────────────────────────────────
old12 = (
    "    <a class=\"nav-item\" id=\"nav-repair\" onclick=\"showRepairLog()\" href=\"#\">\n"
    "      <span class=\"icon\">🔧</span>修繕台帳\n"
    "    </a>"
)
new12 = (
    "    <a class=\"nav-item\" id=\"nav-repair\" onclick=\"showRepairLog()\" href=\"#\">\n"
    "      <span class=\"icon\">🔧</span>修繕台帳\n"
    "    </a>\n"
    "    <a class=\"nav-item\" id=\"nav-map\" onclick=\"showPropertyMap()\" href=\"#\">\n"
    "      <span class=\"icon\">🗺</span>物件マップ\n"
    "    </a>"
)
if old12 not in text:
    raise RuntimeError('12: repair nav not found')
text = text.replace(old12, new12, 1)
print('12. 物件マップナビ追加 OK')

# ─────────────────────────────────────────────────────────────
# 13. feature_v15.js を最後の </script> の直前に挿入
# ─────────────────────────────────────────────────────────────
last_script = text.rfind('</script>')
if last_script == -1:
    raise RuntimeError('13: </script> not found')
text = text[:last_script] + feature_js.rstrip('\n') + '\n\n' + text[last_script:]
print('13. feature_v15.js 挿入 OK')

# ── 書き戻し ──────────────────────────────────────────────────
if crlf:
    text = text.replace('\n', '\r\n')
with open(html_path, 'wb') as f:
    f.write(text.encode('utf-8'))

print('\npatch_v15 完了')
