"""
patch_v26.py
  ① テナント件数を賃貸条件に追加（詳細表示・フォーム・保存）
  ② 賃貸を物件一覧に統合（賃貸タブ追加・all に含める）
  ③ サイドバー整理（nav-rental削除・nav-list→物件一覧・並び順）
実行: cd fudosan_kanri && python patch_v26.py
"""
import sys

SRC = 'index.html'
with open(SRC, 'rb') as f:
    raw = f.read()
text = raw.replace(b'\r\n', b'\n').decode('utf-8')
original = text

# ════════════════════════════════════════════
# Step 1: ③ サイドバー整理
# ════════════════════════════════════════════
find1 = (
    '  <nav>\n'
    '    <div class="nav-group-label">メニュー</div>\n'
    '    <a class="nav-item" id="nav-list" onclick="showList()" href="#">\n'
    '      <span class="icon">🏠</span>売買\n'
    '    </a>\n'
    '    <a class="nav-item" id="nav-logs" onclick="showLogs()" href="#">\n'
    '      <span class="icon">📋</span>敷地整備台帳\n'
    '    </a>\n'
    '    <a class="nav-item" id="nav-rental" onclick="showRentalList()" href="#">\n'
    '      <span class="icon">🏢</span>賃貸\n'
    '    </a>\n'
    '    <a class="nav-item" id="nav-repair" onclick="showRepairLog()" href="#">\n'
    '      <span class="icon">🔧</span>修繕台帳\n'
    '    </a>\n'
    '    <a class="nav-item" id="nav-map" onclick="showPropertyMap()" href="#">\n'
    '      <span class="icon">🗺</span>物件マップ\n'
    '    </a>\n'
    '  </nav>'
)
repl1 = (
    '  <nav>\n'
    '    <div class="nav-group-label">メニュー</div>\n'
    '    <a class="nav-item" id="nav-list" onclick="showList()" href="#">\n'
    '      <span class="icon">🏠</span>物件一覧\n'
    '    </a>\n'
    '    <a class="nav-item" id="nav-logs" onclick="showLogs()" href="#">\n'
    '      <span class="icon">📋</span>敷地整備台帳\n'
    '    </a>\n'
    '    <a class="nav-item" id="nav-repair" onclick="showRepairLog()" href="#">\n'
    '      <span class="icon">🔧</span>修繕台帳\n'
    '    </a>\n'
    '    <a class="nav-item" id="nav-map" onclick="showPropertyMap()" href="#">\n'
    '      <span class="icon">🗺</span>物件マップ\n'
    '    </a>\n'
    '  </nav>'
)
if find1 not in text:
    print('Step 1 FAILED'); sys.exit(1)
text = text.replace(find1, repl1, 1)
print('Step 1 OK: サイドバー整理')

# ════════════════════════════════════════════
# Step 2: ② rental_properties フェッチを allProps の直後に追加
# ════════════════════════════════════════════
find2 = (
    "  const { data: allProps, error } = await q;\n"
    "  if (error) { toast('データ取得失敗: ' + error.message, 'error'); return; }\n"
    "\n"
    "  const all       = allProps || [];"
)
repl2 = (
    "  const { data: allProps, error } = await q;\n"
    "  if (error) { toast('データ取得失敗: ' + error.message, 'error'); return; }\n"
    "\n"
    "  const { data: rentalData } = await db\n"
    "    .from('rental_properties')\n"
    "    .select('*, rental_details(*)')\n"
    "    .order('created_at', { ascending: false });\n"
    "  const rentals = (rentalData || []).map(p => ({ ...p, _isRental: true }));\n"
    "\n"
    "  const all       = allProps || [];"
)
if find2 not in text:
    print('Step 2 FAILED'); sys.exit(1)
text = text.replace(find2, repl2, 1)
print('Step 2 OK: rental_properties フェッチ追加')

# ════════════════════════════════════════════
# Step 3: ② displayed フィルター更新（rental タブ追加・all に賃貸を含める）
# ════════════════════════════════════════════
find3 = (
    "  let displayed;\n"
    "  if      (state.filterType === 'land')    displayed = codeSort(lands);\n"
    "  else if (state.filterType === 'house')   displayed = codeSort(houses);\n"
    "  else if (state.filterType === 'managed') displayed = codeSort(managed);\n"
    "  else if (state.filterType === 'sold')    displayed = codeSort(soldProps);\n"
    "  else                                     displayed = codeSort(all);"
)
repl3 = (
    "  let displayed;\n"
    "  if      (state.filterType === 'land')    displayed = codeSort(lands);\n"
    "  else if (state.filterType === 'house')   displayed = codeSort(houses);\n"
    "  else if (state.filterType === 'rental')  displayed = rentals;\n"
    "  else if (state.filterType === 'managed') displayed = codeSort(managed);\n"
    "  else if (state.filterType === 'sold')    displayed = codeSort(soldProps);\n"
    "  else                                     displayed = [...codeSort(all), ...rentals];"
)
if find3 not in text:
    print('Step 3 FAILED'); sys.exit(1)
text = text.replace(find3, repl3, 1)
print('Step 3 OK: displayed フィルター更新')

# ════════════════════════════════════════════
# Step 4: ② チェックリストループで賃貸物件はスキップ
# ════════════════════════════════════════════
find4 = (
    "    displayed.forEach(p => {\n"
    "      const myItems = _seasonItems.filter(i => i.property_type === 'both' || i.property_type === p.type);\n"
    "      if (!myItems.length) { p._checkAlert = false; return; }"
)
repl4 = (
    "    displayed.forEach(p => {\n"
    "      if (p._isRental) { p._checkAlert = false; return; }\n"
    "      const myItems = _seasonItems.filter(i => i.property_type === 'both' || i.property_type === p.type);\n"
    "      if (!myItems.length) { p._checkAlert = false; return; }"
)
if find4 not in text:
    print('Step 4 FAILED'); sys.exit(1)
text = text.replace(find4, repl4, 1)
print('Step 4 OK: チェックリストで賃貸スキップ')

# ════════════════════════════════════════════
# Step 5: ② page-sub に賃貸件数を追加
# ════════════════════════════════════════════
find5 = (
    '        <div class="page-sub">土地 ${lands.length}件 ／ 中古住宅 ${houses.length}件 ／ 管理物件 ${managed.length}件 ／ 成約済み ${soldProps.length}件</div>'
)
repl5 = (
    '        <div class="page-sub">土地 ${lands.length}件 ／ 中古住宅 ${houses.length}件 ／ 賃貸 ${rentals.length}件 ／ 管理物件 ${managed.length}件 ／ 成約済み ${soldProps.length}件</div>'
)
if find5 not in text:
    print('Step 5 FAILED'); sys.exit(1)
text = text.replace(find5, repl5, 1)
print('Step 5 OK: page-sub 賃貸件数追加')

# ════════════════════════════════════════════
# Step 6: ② filter-tabs に賃貸タブ追加・全て件数更新
# ════════════════════════════════════════════
find6 = (
    "    <div class=\"filter-tabs\">\n"
    "      <button class=\"filter-tab ${state.filterType==='land'    ?'active':''}\" onclick=\"state.filterType='land';renderList()\">🌐 土地（${lands.length}）</button>\n"
    "      <button class=\"filter-tab ${state.filterType==='house'   ?'active':''}\" onclick=\"state.filterType='house';renderList()\">🏡 中古住宅（${houses.length}）</button>\n"
    "      <button class=\"filter-tab ${state.filterType==='managed' ?'active':''}\" onclick=\"state.filterType='managed';renderList()\">🔧 管理物件（${managed.length}）</button>\n"
    "      <button class=\"filter-tab ${state.filterType==='sold'    ?'active':''}\" onclick=\"state.filterType='sold';renderList()\" style=\"${state.filterType==='sold' ? '' : 'color:#cc0000;'}\">🔴 成約済み（${soldProps.length}）</button>\n"
    "      <button class=\"filter-tab ${state.filterType==='all'     ?'active':''}\" onclick=\"state.filterType='all';renderList()\">全て（${all.length}）</button>\n"
    "    </div>"
)
repl6 = (
    "    <div class=\"filter-tabs\">\n"
    "      <button class=\"filter-tab ${state.filterType==='land'    ?'active':''}\" onclick=\"state.filterType='land';renderList()\">🌐 土地（${lands.length}）</button>\n"
    "      <button class=\"filter-tab ${state.filterType==='house'   ?'active':''}\" onclick=\"state.filterType='house';renderList()\">🏡 中古住宅（${houses.length}）</button>\n"
    "      <button class=\"filter-tab ${state.filterType==='rental'  ?'active':''}\" onclick=\"state.filterType='rental';renderList()\">🏢 賃貸（${rentals.length}）</button>\n"
    "      <button class=\"filter-tab ${state.filterType==='managed' ?'active':''}\" onclick=\"state.filterType='managed';renderList()\">🔧 管理物件（${managed.length}）</button>\n"
    "      <button class=\"filter-tab ${state.filterType==='sold'    ?'active':''}\" onclick=\"state.filterType='sold';renderList()\" style=\"${state.filterType==='sold' ? '' : 'color:#cc0000;'}\">🔴 成約済み（${soldProps.length}）</button>\n"
    "      <button class=\"filter-tab ${state.filterType==='all'     ?'active':''}\" onclick=\"state.filterType='all';renderList()\">全て（${all.length + rentals.length}）</button>\n"
    "    </div>"
)
if find6 not in text:
    print('Step 6 FAILED'); sys.exit(1)
text = text.replace(find6, repl6, 1)
print('Step 6 OK: filter-tabs 賃貸タブ追加')

# ════════════════════════════════════════════
# Step 7: ② buildListTable else 節に _isRental ハンドリング追加
# ════════════════════════════════════════════
find7 = (
    "  } else {\n"
    "    heads = ['種別', '掲載 / SUUMO', 'コード', '物件名', '販売価格', '面積(坪)', '取引態様', '販売形態', '学区（小）', '売買完了', ''];\n"
    "    rowFn = p => {\n"
    "      const d    = p.property_details || {};\n"
    "      const tsubo = p.type === 'land'\n"
    "        ? (d.area_tsubo ? d.area_tsubo+'坪' : '—')\n"
    "        : (d.building_area_tsubo ? d.building_area_tsubo+'坪' : '—');\n"
    "      return `<tr onclick=\"showDetail('${p.id}')\" style=\"cursor:pointer;\">\n"
    "        <td>${p.type==='land' ? '<span class=\"badge-land\">土地</span>' : '<span class=\"badge-house\">中古住宅</span>'}</td>\n"
    "        <td>${statusCell(p)}</td>\n"
    "        <td>${esc(p.code||'')}</td>\n"
    "        <td style=\"max-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;\" title=\"${esc(p.property_name||p.address||'')}\">${esc(p.property_name||p.address||'—')}</td>\n"
    "        <td style=\"white-space:nowrap;\">${p.price ? p.price.toLocaleString()+'万円' : '—'}</td>\n"
    "        <td>${tsubo}</td>\n"
    "        <td>${transBadge(d.transaction_type)}</td>\n"
    "        <td style=\"font-size:12px;white-space:nowrap;\">${saleTypeLabel(d.sale_type)}</td>\n"
    "        <td>${esc(d.school_elementary||'—')}</td>\n"
    "        <td>${p.is_sold ? '<span class=\"badge-done\">完了</span>' : '—'}</td>\n"
    "        <td onclick=\"event.stopPropagation()\" style=\"white-space:nowrap;\"><button class=\"btn-sm\" onclick=\"showDetail('${p.id}')\">詳細</button>${alertBadge(p)}${adminBadge(p)}</td>\n"
    "      </tr>`;\n"
    "    };\n"
    "  }"
)
repl7 = (
    "  } else {\n"
    "    heads = ['種別', '掲載 / SUUMO', 'コード', '物件名', '販売価格', '面積(坪)', '取引態様', '販売形態', '学区（小）', '売買完了', ''];\n"
    "    rowFn = p => {\n"
    "      if (p._isRental) {\n"
    "        const rd = Array.isArray(p.rental_details) ? (p.rental_details[0] || {}) : (p.rental_details || {});\n"
    "        const rent = rd.rent ? Number(rd.rent).toLocaleString('ja-JP') + '円/月' : '—';\n"
    "        const tcBadge = rd.tenant_count != null ? `<br><span style=\"font-size:10px;color:var(--text-muted);\">テナント ${rd.tenant_count}件</span>` : '';\n"
    "        return `<tr onclick=\"showRentalDetail('${p.id}')\" style=\"cursor:pointer;\">\n"
    "          <td><span style=\"font-size:10px;background:#e8f0fe;color:#1a73e8;padding:2px 8px;border-radius:6px;font-weight:600;white-space:nowrap;\">🏢 賃貸</span></td>\n"
    "          <td>—</td>\n"
    "          <td>${esc(p.code || '')}</td>\n"
    "          <td style=\"max-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;\" title=\"${esc(p.property_name || p.address || '')}\">${esc(p.property_name || p.address || '—')}</td>\n"
    "          <td style=\"white-space:nowrap;\">${rent}${tcBadge}</td>\n"
    "          <td>—</td>\n"
    "          <td>—</td>\n"
    "          <td>—</td>\n"
    "          <td>—</td>\n"
    "          <td>—</td>\n"
    "          <td onclick=\"event.stopPropagation()\" style=\"white-space:nowrap;\"><button class=\"btn-sm\" onclick=\"showRentalDetail('${p.id}')\">詳細</button></td>\n"
    "        </tr>`;\n"
    "      }\n"
    "      const d    = p.property_details || {};\n"
    "      const tsubo = p.type === 'land'\n"
    "        ? (d.area_tsubo ? d.area_tsubo+'坪' : '—')\n"
    "        : (d.building_area_tsubo ? d.building_area_tsubo+'坪' : '—');\n"
    "      return `<tr onclick=\"showDetail('${p.id}')\" style=\"cursor:pointer;\">\n"
    "        <td>${p.type==='land' ? '<span class=\"badge-land\">土地</span>' : '<span class=\"badge-house\">中古住宅</span>'}</td>\n"
    "        <td>${statusCell(p)}</td>\n"
    "        <td>${esc(p.code||'')}</td>\n"
    "        <td style=\"max-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;\" title=\"${esc(p.property_name||p.address||'')}\">${esc(p.property_name||p.address||'—')}</td>\n"
    "        <td style=\"white-space:nowrap;\">${p.price ? p.price.toLocaleString()+'万円' : '—'}</td>\n"
    "        <td>${tsubo}</td>\n"
    "        <td>${transBadge(d.transaction_type)}</td>\n"
    "        <td style=\"font-size:12px;white-space:nowrap;\">${saleTypeLabel(d.sale_type)}</td>\n"
    "        <td>${esc(d.school_elementary||'—')}</td>\n"
    "        <td>${p.is_sold ? '<span class=\"badge-done\">完了</span>' : '—'}</td>\n"
    "        <td onclick=\"event.stopPropagation()\" style=\"white-space:nowrap;\"><button class=\"btn-sm\" onclick=\"showDetail('${p.id}')\">詳細</button>${alertBadge(p)}${adminBadge(p)}</td>\n"
    "      </tr>`;\n"
    "    };\n"
    "  }"
)
if find7 not in text:
    print('Step 7 FAILED'); sys.exit(1)
text = text.replace(find7, repl7, 1)
print('Step 7 OK: buildListTable 賃貸行ハンドリング追加')

# ════════════════════════════════════════════
# Step 8: ① renderRentalDetail にテナント件数行追加（駐車場の前）
# ════════════════════════════════════════════
find8 = (
    "          <tr><th>駐車場</th><td>${det.parking_available\n"
    "            ? `あり${det.parking_count ? ' (' + det.parking_count + '台)' : ''}${det.parking_fee ? ' / ' + Number(det.parking_fee).toLocaleString('ja-JP') + '円/月' : ''}`\n"
    "            : 'なし'}</td></tr>"
)
repl8 = (
    "          <tr><th>テナント件数</th><td>${det.tenant_count != null ? det.tenant_count + '件' : '—'}</td></tr>\n"
    "          <tr><th>駐車場</th><td>${det.parking_available\n"
    "            ? `あり${det.parking_count ? ' (' + det.parking_count + '台)' : ''}${det.parking_fee ? ' / ' + Number(det.parking_fee).toLocaleString('ja-JP') + '円/月' : ''}`\n"
    "            : 'なし'}</td></tr>"
)
if find8 not in text:
    print('Step 8 FAILED'); sys.exit(1)
text = text.replace(find8, repl8, 1)
print('Step 8 OK: renderRentalDetail テナント件数行追加')

# ════════════════════════════════════════════
# Step 9: ① renderRentalForm にテナント件数フォーム追加（駐車場の前）
# ════════════════════════════════════════════
find9 = (
    '          <div class="form-row">\n'
    '            <div class="form-group">\n'
    '              <label>駐車場</label>\n'
    '              <select id="rf-parking" class="qs-control">'
)
repl9 = (
    '          <div class="form-row">\n'
    '            <div class="form-group">\n'
    '              <label>テナント件数</label>\n'
    '              <input type="number" id="rf-tenant-count" class="qs-control" min="0" step="1" value="${det.tenant_count ?? \'\'}"> \n'
    '            </div>\n'
    '          </div>\n'
    '          <div class="form-row">\n'
    '            <div class="form-group">\n'
    '              <label>駐車場</label>\n'
    '              <select id="rf-parking" class="qs-control">'
)
if find9 not in text:
    print('Step 9 FAILED'); sys.exit(1)
text = text.replace(find9, repl9, 1)
print('Step 9 OK: renderRentalForm テナント件数フォーム追加')

# ════════════════════════════════════════════
# Step 10: ① saveRentalProperty に tenant_count 追加
# ════════════════════════════════════════════
find10 = (
    "    parking_fee:        parseFloatOrNull(document.getElementById('rf-parking-fee')?.value),\n"
    "  };"
)
repl10 = (
    "    parking_fee:        parseFloatOrNull(document.getElementById('rf-parking-fee')?.value),\n"
    "    tenant_count:       parseIntOrNull(document.getElementById('rf-tenant-count')?.value),\n"
    "  };"
)
if find10 not in text:
    print('Step 10 FAILED'); sys.exit(1)
text = text.replace(find10, repl10, 1)
print('Step 10 OK: saveRentalProperty tenant_count 追加')

# ════════════════════════════════════════════
# 書き出し
# ════════════════════════════════════════════
if text == original:
    print('ERROR: no changes made'); sys.exit(1)

out = text.replace('\n', '\r\n').encode('utf-8')
with open(SRC, 'wb') as f:
    f.write(out)
print('\n=== All 10 steps OK ===')
