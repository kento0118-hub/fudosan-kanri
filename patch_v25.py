"""
patch_v25.py
  ① チェックリスト未完了アラート（getCurrentSeason()ベースに刷新）
  ② 管理者承認バッジ（一覧）＋ 承認/取消UI（詳細）に刷新
実行: python patch_v25.py
"""
import sys

SRC = 'index.html'
with open(SRC, 'rb') as f:
    raw = f.read()
text = raw.replace(b'\r\n', b'\n').decode('utf-8')
original = text

# ════════════════════════════════════════════
# Step 1: getCurrentSeason() を markStaffChecked の直前に追加
# ════════════════════════════════════════════
find1 = "async function markStaffChecked(id) {"
repl1 = (
    "function getCurrentSeason() {\n"
    "  const m = new Date().getMonth() + 1;\n"
    "  if (m >= 3 && m <= 5)  return 'spring';\n"
    "  if (m >= 6 && m <= 8)  return 'summer';\n"
    "  if (m >= 9 && m <= 11) return 'fall';\n"
    "  return 'winter';\n"
    "}\n"
    "\n"
    "async function markStaffChecked(id) {"
)
if find1 not in text:
    print('Step 1 FAILED'); sys.exit(1)
text = text.replace(find1, repl1, 1)
print('Step 1 OK: getCurrentSeason() 追加')

# ════════════════════════════════════════════
# Step 2: renderList のチェックリストアラートブロックを刷新
# ════════════════════════════════════════════
find2 = (
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
    "  }"
)
repl2 = (
    "  // 今の季節のチェックリスト未完了チェック\n"
    "  const _currentSeason = getCurrentSeason();\n"
    "  const _seasonItems = state.checklistItems.filter(i =>\n"
    "    i.season === _currentSeason &&\n"
    "    (i.property_type === 'both' || displayed.some(p => p.type === i.property_type))\n"
    "  );\n"
    "\n"
    "  if (displayed.length && _seasonItems.length) {\n"
    "    const { data: _chkd } = await db.from('checklist_checks')\n"
    "      .select('property_id,item_id,is_checked')\n"
    "      .in('property_id', displayed.map(p => p.id));\n"
    "\n"
    "    displayed.forEach(p => {\n"
    "      const myItems = _seasonItems.filter(i => i.property_type === 'both' || i.property_type === p.type);\n"
    "      if (!myItems.length) { p._checkAlert = false; return; }\n"
    "      const myChecks = (_chkd || []).filter(c => c.property_id === p.id);\n"
    "      const allDone = myItems.every(item =>\n"
    "        myChecks.some(c => c.item_id === item.id && c.is_checked)\n"
    "      );\n"
    "      p._checkAlert = !allDone;\n"
    "    });\n"
    "  }"
)
if find2 not in text:
    print('Step 2 FAILED'); sys.exit(1)
text = text.replace(find2, repl2, 1)
print('Step 2 OK: チェックリストアラートブロック刷新')

# ════════════════════════════════════════════
# Step 3: buildListTable ヘルパー関数を刷新（checkStatBadge → adminBadge）
# ════════════════════════════════════════════
find3 = (
    "  const alertBadge     = p => (p._checkAlert||[]).length\n"
    "    ? '<span style=\"font-size:10px;background:#fde8e8;color:#c94040;padding:2px 6px;border-radius:4px;font-weight:700;\">⚠️ 未点検</span>' : '';\n"
    "  const checkStatBadge = p => !p.staff_checked_at\n"
    "    ? '<span style=\"font-size:10px;background:#fdf0d4;color:#d4920a;padding:2px 6px;border-radius:4px;font-weight:700;\">📝 未確認</span>'\n"
    "    : !p.admin_checked_at\n"
    "    ? '<span style=\"font-size:10px;background:#deeafc;color:#2a7ae2;padding:2px 6px;border-radius:4px;font-weight:700;\">👁️ 要承認</span>'\n"
    "    : '<span style=\"font-size:10px;background:#d4f0e3;color:#2e9e68;padding:2px 6px;border-radius:4px;font-weight:700;\">✅ 承認済</span>';"
)
repl3 = (
    "  const alertBadge = p => p._checkAlert\n"
    "    ? '<span style=\"font-size:10px;background:#fde8e8;color:#c94040;padding:2px 6px;border-radius:4px;font-weight:700;margin-left:4px;\">⚠️ 要確認</span>' : '';\n"
    "  const adminBadge  = p => p.admin_checked_at\n"
    "    ? '<span style=\"font-size:10px;background:#d4f0e3;color:#2e9e68;padding:2px 6px;border-radius:4px;font-weight:700;margin-left:4px;\">✅ 管理者確認済</span>' : '';"
)
if find3 not in text:
    print('Step 3 FAILED'); sys.exit(1)
text = text.replace(find3, repl3, 1)
print('Step 3 OK: alertBadge/adminBadge ヘルパー刷新')

# ════════════════════════════════════════════
# Step 4: 詳細ボタンセル3箇所を刷新（checkStatBadge → adminBadge）
# ════════════════════════════════════════════
old_btn = "        <td onclick=\"event.stopPropagation()\"><div style=\"display:flex;gap:4px;align-items:center;flex-wrap:wrap;\"><button class=\"btn-sm\" onclick=\"showDetail('${p.id}')\">詳細</button>${alertBadge(p)}${checkStatBadge(p)}</div></td>"
new_btn = "        <td onclick=\"event.stopPropagation()\" style=\"white-space:nowrap;\"><button class=\"btn-sm\" onclick=\"showDetail('${p.id}')\">詳細</button>${alertBadge(p)}${adminBadge(p)}</td>"
cnt = text.count(old_btn)
if cnt == 0:
    print('Step 4 FAILED'); sys.exit(1)
text = text.replace(old_btn, new_btn)
print(f'Step 4 OK: 詳細ボタンセル刷新 ({cnt}箇所)')

# ════════════════════════════════════════════
# Step 5: renderDetail の管理者確認UIを刷新
# ════════════════════════════════════════════
find5 = (
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
    "    </div>"
)
repl5 = (
    "    <!-- 管理者承認 -->\n"
    "    <div style=\"margin-top:10px;display:flex;align-items:center;gap:10px;flex-wrap:wrap;\">\n"
    "      ${prop.admin_checked_at\n"
    "        ? `<span style=\"font-size:12px;background:#d4f0e3;color:#2e9e68;padding:4px 12px;border-radius:6px;font-weight:600;\">✅ 管理者確認済　${new Date(prop.admin_checked_at).toLocaleDateString('ja-JP')}</span>\n"
    "           <button onclick=\"clearAdminCheck('${id}')\" style=\"font-size:11px;background:none;border:1px solid #ccc;border-radius:4px;padding:3px 8px;cursor:pointer;color:var(--text-muted);\">取消</button>`\n"
    "        : `<button onclick=\"markAdminChecked('${id}')\" style=\"font-size:13px;background:#d4f0e3;color:#2e9e68;border:1px solid #b8dfc8;border-radius:6px;padding:6px 16px;cursor:pointer;font-weight:600;\">✅ 管理者承認する</button>`\n"
    "      }\n"
    "    </div>"
)
if find5 not in text:
    print('Step 5 FAILED'); sys.exit(1)
text = text.replace(find5, repl5, 1)
print('Step 5 OK: renderDetail 管理者承認UI刷新')

# ════════════════════════════════════════════
# Step 6: clearAdminCheck を markAdminChecked の直後に追加
# ════════════════════════════════════════════
find6 = (
    "async function markAdminChecked(id) {\n"
    "  const now = new Date().toISOString();\n"
    "  const { error } = await db.from('properties').update({ admin_checked_at: now }).eq('id', id);\n"
    "  if (error) { toast('承認記録失敗: ' + error.message, 'error'); return; }\n"
    "  toast('管理者承認を記録しました', 'success');\n"
    "  await showDetail(id);\n"
    "}"
)
repl6 = (
    "async function markAdminChecked(id) {\n"
    "  const { error } = await db.from('properties')\n"
    "    .update({ admin_checked_at: new Date().toISOString() }).eq('id', id);\n"
    "  if (error) { toast('承認失敗: ' + error.message, 'error'); return; }\n"
    "  toast('管理者承認しました', 'success');\n"
    "  await showDetail(id);\n"
    "}\n"
    "\n"
    "async function clearAdminCheck(id) {\n"
    "  const { error } = await db.from('properties')\n"
    "    .update({ admin_checked_at: null }).eq('id', id);\n"
    "  if (error) { toast('取消失敗: ' + error.message, 'error'); return; }\n"
    "  toast('承認を取り消しました', 'success');\n"
    "  await showDetail(id);\n"
    "}"
)
if find6 not in text:
    print('Step 6 FAILED'); sys.exit(1)
text = text.replace(find6, repl6, 1)
print('Step 6 OK: markAdminChecked 更新 + clearAdminCheck 追加')

# ════════════════════════════════════════════
# 書き出し
# ════════════════════════════════════════════
if text == original:
    print('ERROR: no changes'); sys.exit(1)

out = text.replace('\n', '\r\n').encode('utf-8')
with open(SRC, 'wb') as f:
    f.write(out)
print('\n=== All steps OK ===')
