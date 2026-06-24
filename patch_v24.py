"""
patch_v24.py  — 5点同時修正
  ① チェックリスト未実施アラートバッジ（一覧）
  ② 社員確認・管理者承認バッジ＋ボタン（一覧＋詳細）
  ③ 埋蔵「なし」選択肢削除
  ④ 築年入力を和暦タブ式に変更
  ⑤ コードなし物件を一覧最後尾へ
実行: python patch_v24.py
"""
import sys

SRC = 'index.html'
with open(SRC, 'rb') as f:
    raw = f.read()
text = raw.replace(b'\r\n', b'\n').decode('utf-8')
original = text

# ════════════════════════════════════════════
# ⑤ codeSort: コードなしを最後尾
# ════════════════════════════════════════════
find5 = (
    "    const key = p => {\n"
    "      const kk = getKukaku(p);\n"
    "      if (kk !== null) {\n"
    "        const bn = baseName(p);\n"
    "        const g  = groups[bn];\n"
    "        return [g.l, g.n, bn, kk];\n"
    "      }\n"
    "      return [ORDER[letter(p)] ?? 3, codeNum(p), p?.property_name || '', 0];\n"
    "    };"
)
repl5 = (
    "    const key = p => {\n"
    "      const kk = getKukaku(p);\n"
    "      if (kk !== null) {\n"
    "        const bn = baseName(p);\n"
    "        const g  = groups[bn];\n"
    "        return [g.l, g.n, bn, kk];\n"
    "      }\n"
    "      const hasCode = (p?.code || '').trim().length > 0;\n"
    "      if (!hasCode) return [99, 0, p?.property_name || '', 0];\n"
    "      return [ORDER[letter(p)] ?? 3, codeNum(p), p?.property_name || '', 0];\n"
    "    };"
)
if find5 not in text:
    print('Step ⑤ FAILED'); sys.exit(1)
text = text.replace(find5, repl5, 1)
print('Step ⑤ OK: codeSort コードなし最後尾')

# ════════════════════════════════════════════
# ① checklist alert fetch in renderList
# ════════════════════════════════════════════
find1a = (
    "      displayed.forEach(p => { p._iq = _cm[p.id] || {}; });\n"
    "    }\n"
    "  }\n"
    "\n"
    "  el.innerHTML = `"
)
repl1a = (
    "      displayed.forEach(p => { p._iq = _cm[p.id] || {}; });\n"
    "    }\n"
    "  }\n"
    "\n"
    "  // チェックリストアラートを付加\n"
    "  if (displayed.length) {\n"
    "    const curYear  = new Date().getFullYear();\n"
    "    const curMonth = new Date().getMonth() + 1;\n"
    "    const { data: _ckd } = await db.from('checklist_checks')\n"
    "      .select('property_id,item_id,year,is_checked')\n"
    "      .in('property_id', displayed.map(p => p.id))\n"
    "      .eq('year', curYear);\n"
    "    const _ckMap = {};\n"
    "    if (_ckd) _ckd.forEach(c => {\n"
    "      if (!_ckMap[c.property_id]) _ckMap[c.property_id] = [];\n"
    "      _ckMap[c.property_id].push(c);\n"
    "    });\n"
    "    const passedSeasons = [];\n"
    "    if (curMonth > 2)  passedSeasons.push({ key:'winter', label:'冬' });\n"
    "    if (curMonth > 5)  passedSeasons.push({ key:'spring', label:'春' });\n"
    "    if (curMonth > 8)  passedSeasons.push({ key:'summer', label:'夏' });\n"
    "    if (curMonth > 11) passedSeasons.push({ key:'fall',   label:'秋' });\n"
    "    const clItems = state.checklistItems || [];\n"
    "    displayed.forEach(p => {\n"
    "      const propChecks = _ckMap[p.id] || [];\n"
    "      const alerts = [];\n"
    "      for (const { key, label } of passedSeasons) {\n"
    "        const items = clItems.filter(i => i.season === key);\n"
    "        if (!items.length) continue;\n"
    "        const allDone = items.every(item =>\n"
    "          propChecks.some(c => c.item_id === item.id && c.is_checked)\n"
    "        );\n"
    "        if (!allDone) alerts.push(label);\n"
    "      }\n"
    "      p._checkAlert = alerts;\n"
    "    });\n"
    "  }\n"
    "\n"
    "  el.innerHTML = `"
)
if find1a not in text:
    print('Step ① FAILED'); sys.exit(1)
text = text.replace(find1a, repl1a, 1)
print('Step ① OK: checklist alert fetch 追加')

# ════════════════════════════════════════════
# ①② buildListTable: alertBadge/checkStatBadge helpers
# ════════════════════════════════════════════
find_helpers = (
    "  const transBadge = (t) => t === 'owner'   ? '<span class=\"badge-owner\">売主</span>'\n"
    "                           : t === 'broker'  ? '<span class=\"badge-broker\">仲介</span>'\n"
    "                           : t === 'managed' ? '<span class=\"badge-managed\">管理物件</span>' : '—';"
)
repl_helpers = (
    "  const transBadge = (t) => t === 'owner'   ? '<span class=\"badge-owner\">売主</span>'\n"
    "                           : t === 'broker'  ? '<span class=\"badge-broker\">仲介</span>'\n"
    "                           : t === 'managed' ? '<span class=\"badge-managed\">管理物件</span>' : '—';\n"
    "  const alertBadge     = p => (p._checkAlert||[]).length\n"
    "    ? '<span style=\"font-size:10px;background:#fde8e8;color:#c94040;padding:2px 6px;border-radius:4px;font-weight:700;\">⚠️ 未点検</span>' : '';\n"
    "  const checkStatBadge = p => !p.staff_checked_at\n"
    "    ? '<span style=\"font-size:10px;background:#fdf0d4;color:#d4920a;padding:2px 6px;border-radius:4px;font-weight:700;\">📝 未確認</span>'\n"
    "    : !p.admin_checked_at\n"
    "    ? '<span style=\"font-size:10px;background:#deeafc;color:#2a7ae2;padding:2px 6px;border-radius:4px;font-weight:700;\">👁️ 要承認</span>'\n"
    "    : '<span style=\"font-size:10px;background:#d4f0e3;color:#2e9e68;padding:2px 6px;border-radius:4px;font-weight:700;\">✅ 承認済</span>';"
)
if find_helpers not in text:
    print('Step ①② helpers FAILED'); sys.exit(1)
text = text.replace(find_helpers, repl_helpers, 1)
print('Step ①② OK: alertBadge/checkStatBadge helpers 追加')

# ════════════════════════════════════════════
# ①② buildListTable: 詳細ボタンセルにバッジ追加（3箇所共通）
# ════════════════════════════════════════════
old_btn = "        <td onclick=\"event.stopPropagation()\"><button class=\"btn-sm\" onclick=\"showDetail('${p.id}')\">詳細</button></td>"
new_btn = "        <td onclick=\"event.stopPropagation()\"><div style=\"display:flex;gap:4px;align-items:center;flex-wrap:wrap;\"><button class=\"btn-sm\" onclick=\"showDetail('${p.id}')\">詳細</button>${alertBadge(p)}${checkStatBadge(p)}</div></td>"
cnt = text.count(old_btn)
if cnt == 0:
    print('Step ①② detail button FAILED'); sys.exit(1)
text = text.replace(old_btn, new_btn)
print(f'Step ①② OK: 詳細ボタンセル更新 ({cnt}箇所)')

# ════════════════════════════════════════════
# ② renderDetail: 社員/管理者確認UIを追加
# ════════════════════════════════════════════
find2 = (
    "        <button class=\"btn-danger\"  onclick=\"confirmDelete('${id}')\">🗑 削除</button>\n"
    "      </div>\n"
    "    </div>\n"
    "\n"
    "    <!-- 基本情報 ＋ 詳細情報 -->"
)
repl2 = (
    "        <button class=\"btn-danger\"  onclick=\"confirmDelete('${id}')\">🗑 削除</button>\n"
    "      </div>\n"
    "    </div>\n"
    "\n"
    "    <!-- 社員・管理者確認 -->\n"
    "    <div style=\"display:flex;gap:10px;margin-top:6px;margin-bottom:8px;flex-wrap:wrap;align-items:center;\">\n"
    "      <button onclick=\"markStaffChecked('${id}')\" style=\"background:#e8f0fe;color:#2a7ae2;border:1px solid #a8c4f5;padding:6px 14px;border-radius:6px;font-size:12px;font-weight:600;cursor:pointer;\">\n"
    "        📝 社員確認済にする\n"
    "      </button>\n"
    "      <span style=\"font-size:11px;color:var(--text-muted);\">\n"
    "        ${prop.staff_checked_at ? '社員確認: ' + prop.staff_checked_at.slice(0,10) : 'まだ未確認'}\n"
    "      </span>\n"
    "      <button onclick=\"markAdminChecked('${id}')\" style=\"background:#d4f0e3;color:#2e9e68;border:1px solid #8ecfa8;padding:6px 14px;border-radius:6px;font-size:12px;font-weight:600;cursor:pointer;\">\n"
    "        ✅ 管理者承認\n"
    "      </button>\n"
    "      <span style=\"font-size:11px;color:var(--text-muted);\">\n"
    "        ${prop.admin_checked_at ? '管理者承認: ' + prop.admin_checked_at.slice(0,10) : '未承認'}\n"
    "      </span>\n"
    "    </div>\n"
    "\n"
    "    <!-- 基本情報 ＋ 詳細情報 -->"
)
if find2 not in text:
    print('Step ② renderDetail FAILED'); sys.exit(1)
text = text.replace(find2, repl2, 1)
print('Step ② OK: renderDetail 社員/管理者確認UI追加')

# ════════════════════════════════════════════
# ② markStaffChecked / markAdminChecked 関数追加
# ════════════════════════════════════════════
find2b = "function calcCommission(priceManen) {"
repl2b = (
    "async function markStaffChecked(id) {\n"
    "  const now = new Date().toISOString();\n"
    "  const { error } = await db.from('properties').update({ staff_checked_at: now }).eq('id', id);\n"
    "  if (error) { toast('確認記録失敗: ' + error.message, 'error'); return; }\n"
    "  toast('社員確認を記録しました', 'success');\n"
    "  await showDetail(id);\n"
    "}\n"
    "async function markAdminChecked(id) {\n"
    "  const now = new Date().toISOString();\n"
    "  const { error } = await db.from('properties').update({ admin_checked_at: now }).eq('id', id);\n"
    "  if (error) { toast('承認記録失敗: ' + error.message, 'error'); return; }\n"
    "  toast('管理者承認を記録しました', 'success');\n"
    "  await showDetail(id);\n"
    "}\n"
    "\n"
    "function calcCommission(priceManen) {"
)
if find2b not in text:
    print('Step ② functions FAILED'); sys.exit(1)
text = text.replace(find2b, repl2b, 1)
print('Step ② OK: markStaffChecked/markAdminChecked 追加')

# ════════════════════════════════════════════
# ③ buriedOpts から「なし」削除
# ════════════════════════════════════════════
find3 = "  const buriedOpts    = [['','（未選択）'],['あり','あり'],['なし','なし'],['不明','不明']];"
repl3 = "  const buriedOpts    = [['','（未選択）'],['あり','あり'],['不明','不明']];"
if find3 not in text:
    print('Step ③ FAILED'); sys.exit(1)
text = text.replace(find3, repl3, 1)
print('Step ③ OK: buriedOpts から「なし」削除')

# ════════════════════════════════════════════
# ④-a showPropertyModal: built date 初期値計算を和暦に変更
# ════════════════════════════════════════════
find4a = (
    "  let builtYear = '', builtMonth = '';\n"
    "  if (!isLand && d.built_date) {\n"
    "    const ym = d.built_date.match(/(\\d{4})/);\n"
    "    const mm = d.built_date.match(/(\\d{1,2})月/);\n"
    "    if (ym) builtYear  = ym[1];\n"
    "    if (mm) builtMonth = mm[1];\n"
    "  }"
)
repl4a = (
    "  let _warekiEra = '昭和', _warekiYear = '', builtMonth = '';\n"
    "  if (!isLand && d.built_date) {\n"
    "    const ym = d.built_date.match(/(\\d{4})/);\n"
    "    const mm = d.built_date.match(/(\\d{1,2})月/);\n"
    "    if (ym) {\n"
    "      const yr = parseInt(ym[1]);\n"
    "      if (yr >= 2019) { _warekiEra = '令和'; _warekiYear = yr - 2018; }\n"
    "      else if (yr >= 1989) { _warekiEra = '平成'; _warekiYear = yr - 1988; }\n"
    "      else { _warekiEra = '昭和'; _warekiYear = yr - 1925; }\n"
    "    }\n"
    "    if (mm) builtMonth = mm[1];\n"
    "  }\n"
    "  _selectedEra = _warekiEra;"
)
if find4a not in text:
    print('Step ④-a FAILED'); sys.exit(1)
text = text.replace(find4a, repl4a, 1)
print('Step ④-a OK: showPropertyModal built date 初期値を和暦に変更')

# ════════════════════════════════════════════
# ④-b showPropertyModal: 築年HTMLを和暦タブ式に変更
# ════════════════════════════════════════════
find4b = (
    "      <div class=\"form-row\">\n"
    "        <div class=\"form-group\">\n"
    "          <label>築年（西暦）</label>\n"
    "          <input id=\"f-built-year\" type=\"number\" min=\"1900\" max=\"2026\" class=\"qs-control\"\n"
    "                 value=\"${builtYear}\" placeholder=\"例：1998\" oninput=\"updateBuiltDisplay()\">\n"
    "        </div>\n"
    "        <div class=\"form-group\">\n"
    "          <label>築月</label>\n"
    "          ${monthSel}\n"
    "        </div>\n"
    "      </div>\n"
    "      <div class=\"built-display\" id=\"built-display\"></div>"
)
repl4b = (
    "      <div class=\"form-group\">\n"
    "        <label>築年（和暦）</label>\n"
    "        <div style=\"display:flex;gap:4px;margin-bottom:6px;\" id=\"era-tabs\">\n"
    "          <button type=\"button\" class=\"filter-tab ${_selectedEra==='昭和'?'active':''}\" onclick=\"selectEra('昭和',this)\" id=\"era-s\">昭和</button>\n"
    "          <button type=\"button\" class=\"filter-tab ${_selectedEra==='平成'?'active':''}\" onclick=\"selectEra('平成',this)\" id=\"era-h\">平成</button>\n"
    "          <button type=\"button\" class=\"filter-tab ${_selectedEra==='令和'?'active':''}\" onclick=\"selectEra('令和',this)\" id=\"era-r\">令和</button>\n"
    "        </div>\n"
    "        <div style=\"display:flex;align-items:center;gap:6px;\">\n"
    "          <span id=\"era-label\" style=\"font-size:13px;font-weight:600;min-width:2em;\">${_selectedEra}</span>\n"
    "          <input id=\"f-built-wareki-year\" type=\"number\" min=\"1\" max=\"99\" class=\"qs-control\"\n"
    "                 style=\"width:80px;\" placeholder=\"年\" value=\"${_warekiYear}\" oninput=\"updateBuiltDisplay()\">\n"
    "          <span>年</span>\n"
    "          ${monthSel}\n"
    "        </div>\n"
    "        <div class=\"built-display\" id=\"built-display\" style=\"margin-top:6px;\"></div>\n"
    "      </div>"
)
if find4b not in text:
    print('Step ④-b FAILED'); sys.exit(1)
text = text.replace(find4b, repl4b, 1)
print('Step ④-b OK: 築年HTML を和暦タブ式に変更')

# ════════════════════════════════════════════
# ④-c saveProperty: built_date 生成を和暦ベースに変更
# ════════════════════════════════════════════
find4c = (
    "    const builtYear  = document.getElementById('f-built-year')?.value;\n"
    "    const builtMonth = document.getElementById('f-built-month')?.value;\n"
    "    if (builtYear) {\n"
    "      detData.built_date = `${builtYear}年${builtMonth ? builtMonth+'月' : ''}`;\n"
    "    } else {\n"
    "      detData.built_date = null;\n"
    "    }"
)
repl4c = (
    "    const warekiN    = document.getElementById('f-built-wareki-year')?.value;\n"
    "    const builtMonth = document.getElementById('f-built-month')?.value;\n"
    "    if (warekiN && _selectedEra) {\n"
    "      const seireki = eraToSeireki(_selectedEra, warekiN);\n"
    "      detData.built_date = seireki ? `${seireki}年${builtMonth ? builtMonth+'月' : ''}` : null;\n"
    "    } else {\n"
    "      detData.built_date = null;\n"
    "    }"
)
if find4c not in text:
    print('Step ④-c FAILED'); sys.exit(1)
text = text.replace(find4c, repl4c, 1)
print('Step ④-c OK: saveProperty built_date 生成を和暦ベースに変更')

# ════════════════════════════════════════════
# ④-d _selectedEra / selectEra / eraToSeireki 追加 + updateBuiltDisplay 書き換え
# ════════════════════════════════════════════
find4d = (
    "function updateBuiltDisplay() {\n"
    "  const yearEl  = document.getElementById('f-built-year');\n"
    "  const monthEl = document.getElementById('f-built-month');\n"
    "  const dispEl  = document.getElementById('built-display');\n"
    "  if (!dispEl) return;\n"
    "  const year  = yearEl?.value;\n"
    "  const month = monthEl?.value;\n"
    "  if (!year) { dispEl.textContent = ''; return; }\n"
    "  const wareki  = toWareki(year, month);\n"
    "  const age     = new Date().getFullYear() - parseInt(year);\n"
    "  const monthStr = month ? `${month}月` : '';\n"
    "  dispEl.textContent = `${year}年${monthStr}　→　${wareki}${monthStr}　（築${age >= 0 ? age : '?'}年）`;\n"
    "}"
)
repl4d = (
    "let _selectedEra = '昭和';\n"
    "function selectEra(era, btn) {\n"
    "  _selectedEra = era;\n"
    "  document.querySelectorAll('#era-tabs .filter-tab').forEach(b => b.classList.remove('active'));\n"
    "  btn.classList.add('active');\n"
    "  document.getElementById('era-label').textContent = era;\n"
    "  updateBuiltDisplay();\n"
    "}\n"
    "function eraToSeireki(era, n) {\n"
    "  const base = { '昭和': 1925, '平成': 1988, '令和': 2018 };\n"
    "  return base[era] ? base[era] + parseInt(n) : null;\n"
    "}\n"
    "function updateBuiltDisplay() {\n"
    "  const dispEl = document.getElementById('built-display');\n"
    "  if (!dispEl) return;\n"
    "  const n     = document.getElementById('f-built-wareki-year')?.value;\n"
    "  const month = document.getElementById('f-built-month')?.value;\n"
    "  if (!n) { dispEl.textContent = ''; return; }\n"
    "  const year = eraToSeireki(_selectedEra, n);\n"
    "  if (!year) { dispEl.textContent = ''; return; }\n"
    "  const age = new Date().getFullYear() - year;\n"
    "  const monthStr = month ? `${month}月` : '';\n"
    "  dispEl.textContent = `${_selectedEra}${n}年${monthStr}　西暦 ${year}年${monthStr}　（築${age >= 0 ? age : '?'}年）`;\n"
    "}"
)
if find4d not in text:
    print('Step ④-d FAILED'); sys.exit(1)
text = text.replace(find4d, repl4d, 1)
print('Step ④-d OK: _selectedEra/selectEra/eraToSeireki 追加 + updateBuiltDisplay 更新')

# ════════════════════════════════════════════
# 書き出し
# ════════════════════════════════════════════
if text == original:
    print('ERROR: no changes made'); sys.exit(1)

out = text.replace('\n', '\r\n').encode('utf-8')
with open(SRC, 'wb') as f:
    f.write(out)
print('\n=== All steps OK ===')
