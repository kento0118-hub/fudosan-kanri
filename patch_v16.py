import os

base      = os.path.dirname(os.path.abspath(__file__))
html_path = os.path.join(base, 'index.html')
js_path   = os.path.join(base, 'inquiry_v1.js')

with open(html_path, 'rb') as f:
    raw = f.read()
crlf = b'\r\n' in raw
text = raw.decode('utf-8').replace('\r\n', '\n')

with open(js_path, 'rb') as f:
    inquiry_js = f.read().decode('utf-8').replace('\r\n', '\n')

# ─────────────────────────────────────────────────────────────
# 1. フォーム：販売開始日・掲載開始日3件を追加
#    （売看板あり チェックボックスの直後、<!-- 価格・取引 --> の直前）
# ─────────────────────────────────────────────────────────────
old1 = (
    "            \U0001faa7 売看板あり\n"
    "          </label>\n"
    "        </div>\n"
    "      </div>\n"
    "\n"
    "      <!-- 価格・取引 -->"
)
new1 = (
    "            \U0001faa7 売看板あり\n"
    "          </label>\n"
    "        </div>\n"
    "      </div>\n"
    "      <div class=\"form-row\">\n"
    "        <div class=\"form-group\">\n"
    "          <label>販売開始日</label>\n"
    "          <input id=\"f-sale-start\" type=\"date\" class=\"qs-control\" value=\"${d.sale_start_date||''}\">\n"
    "        </div>\n"
    "        <div class=\"form-group\">\n"
    "          <label>SUUMO掲載開始日</label>\n"
    "          <input id=\"f-suumo-start\" type=\"date\" class=\"qs-control\" value=\"${d.suumo_start_date||''}\">\n"
    "        </div>\n"
    "      </div>\n"
    "      <div class=\"form-row\">\n"
    "        <div class=\"form-group\">\n"
    "          <label>HP掲載開始日</label>\n"
    "          <input id=\"f-hp-start\" type=\"date\" class=\"qs-control\" value=\"${d.hp_start_date||''}\">\n"
    "        </div>\n"
    "        <div class=\"form-group\">\n"
    "          <label>売看板設置日</label>\n"
    "          <input id=\"f-sign-start\" type=\"date\" class=\"qs-control\" value=\"${d.sign_start_date||''}\">\n"
    "        </div>\n"
    "      </div>\n"
    "\n"
    "      <!-- 価格・取引 -->"
)
if old1 not in text:
    raise RuntimeError('1: form checkboxes marker not found')
text = text.replace(old1, new1, 1)
print('1. フォーム掲載日フィールド追加 OK')

# ─────────────────────────────────────────────────────────────
# 2. saveProperty detData：新しい日付フィールドを追加
# ─────────────────────────────────────────────────────────────
old2 = "    publish_date:      document.getElementById('f-publish-date').value      || null,\n  };"
new2 = (
    "    publish_date:      document.getElementById('f-publish-date').value      || null,\n"
    "    sale_start_date:  document.getElementById('f-sale-start')?.value        || null,\n"
    "    suumo_start_date: document.getElementById('f-suumo-start')?.value       || null,\n"
    "    hp_start_date:    document.getElementById('f-hp-start')?.value          || null,\n"
    "    sign_start_date:  document.getElementById('f-sign-start')?.value        || null,\n"
    "  };"
)
if old2 not in text:
    raise RuntimeError('2: detData publish_date not found')
text = text.replace(old2, new2, 1)
print('2. detData 日付フィールド追加 OK')

# ─────────────────────────────────────────────────────────────
# 3. 詳細ビュー：情報公開日の後に販売開始日・掲載開始日を表示
# ─────────────────────────────────────────────────────────────
old3 = "          <tr><th>情報公開日</th><td>${det.publish_date || '—'}</td></tr>\n          <tr><th>取引態様</th>"
new3 = (
    "          <tr><th>情報公開日</th><td>${det.publish_date || '—'}</td></tr>\n"
    "          ${det.sale_start_date ? `<tr><th>販売開始日</th><td>${det.sale_start_date}</td></tr>` : ''}\n"
    "          ${(det.suumo_start_date||det.hp_start_date||det.sign_start_date) ? `<tr><th>掲載開始日</th><td style=\"font-size:12px;\">${det.suumo_start_date?'SUUMO: '+det.suumo_start_date+'\\u3000':''}${det.hp_start_date?'HP: '+det.hp_start_date+'\\u3000':''}${det.sign_start_date?'売看板: '+det.sign_start_date:''}</td></tr>` : ''}\n"
    "          <tr><th>取引態様</th>"
)
if old3 not in text:
    raise RuntimeError('3: 情報公開日 row not found')
text = text.replace(old3, new3, 1)
print('3. 詳細ビュー掲載日表示追加 OK')

# ─────────────────────────────────────────────────────────────
# 4. renderDetail Promise.all に inquiry_logs を追加
# ─────────────────────────────────────────────────────────────
old4 = (
    "  const [propRes, photosRes, checksRes, logsRes, priceHistRes] = await Promise.all([\n"
    "    db.from('properties').select('*, property_details(*)').eq('id', id).single(),\n"
    "    db.from('property_photos').select('*').eq('property_id', id).order('order_index'),\n"
    "    db.from('checklist_checks').select('*').eq('property_id', id),\n"
    "    db.from('task_logs').select('*').eq('property_id', id).order('performed_date', { ascending: false }),\n"
    "    db.from('price_history').select('*').eq('property_id', id).order('recorded_date', { ascending: false }),\n"
    "  ]);"
)
new4 = (
    "  const [propRes, photosRes, checksRes, logsRes, priceHistRes, inqRes] = await Promise.all([\n"
    "    db.from('properties').select('*, property_details(*)').eq('id', id).single(),\n"
    "    db.from('property_photos').select('*').eq('property_id', id).order('order_index'),\n"
    "    db.from('checklist_checks').select('*').eq('property_id', id),\n"
    "    db.from('task_logs').select('*').eq('property_id', id).order('performed_date', { ascending: false }),\n"
    "    db.from('price_history').select('*').eq('property_id', id).order('recorded_date', { ascending: false }),\n"
    "    db.from('inquiry_logs').select('*').eq('property_id', id).eq('property_type', 'sale').order('date', { ascending: false }),\n"
    "  ]);"
)
if old4 not in text:
    raise RuntimeError('4: renderDetail Promise.all not found')
text = text.replace(old4, new4, 1)
print('4. renderDetail Promise.all追加 OK')

# ─────────────────────────────────────────────────────────────
# 5. renderDetail：inquiries 変数を追加
# ─────────────────────────────────────────────────────────────
old5 = (
    "  const priceHistory = priceHistRes.data || [];\n"
    "  const det          = prop.property_details || {};"
)
new5 = (
    "  const priceHistory = priceHistRes.data || [];\n"
    "  const inquiries    = inqRes.data        || [];\n"
    "  const det          = prop.property_details || {};"
)
if old5 not in text:
    raise RuntimeError('5: priceHistory variable not found')
text = text.replace(old5, new5, 1)
print('5. inquiries変数追加 OK')

# ─────────────────────────────────────────────────────────────
# 6. 売買詳細HTML：チェックリストの直前に内見・問い合わせセクションを追加
# ─────────────────────────────────────────────────────────────
old6 = "    <!-- チェックリスト ＋ 実施記録 -->"
new6 = "    ${buildInquirySection(inquiries, id, 'sale')}\n\n    <!-- チェックリスト ＋ 実施記録 -->"
if old6 not in text:
    raise RuntimeError('6: チェックリスト marker not found')
text = text.replace(old6, new6, 1)
print('6. 売買詳細 inquiryセクション追加 OK')

# ─────────────────────────────────────────────────────────────
# 7. renderRentalDetail Promise.all に inquiry_logs を追加
# ─────────────────────────────────────────────────────────────
old7 = (
    "  const [propRes, detRes, tenantRes, histRes, unitsRes] = await Promise.all([\n"
    "    db.from('rental_properties').select('*').eq('id', id).single(),\n"
    "    db.from('rental_details').select('*').eq('rental_id', id).maybeSingle(),\n"
    "    db.from('rental_tenants').select('*').eq('rental_id', id).maybeSingle(),\n"
    "    db.from('rental_tenant_history').select('*').eq('rental_id', id).order('contract_end', { ascending: false }),\n"
    "    db.from('rental_units').select('*').eq('rental_id', id).order('unit_number'),\n"
    "  ]);"
)
new7 = (
    "  const [propRes, detRes, tenantRes, histRes, unitsRes, inqRes] = await Promise.all([\n"
    "    db.from('rental_properties').select('*').eq('id', id).single(),\n"
    "    db.from('rental_details').select('*').eq('rental_id', id).maybeSingle(),\n"
    "    db.from('rental_tenants').select('*').eq('rental_id', id).maybeSingle(),\n"
    "    db.from('rental_tenant_history').select('*').eq('rental_id', id).order('contract_end', { ascending: false }),\n"
    "    db.from('rental_units').select('*').eq('rental_id', id).order('unit_number'),\n"
    "    db.from('inquiry_logs').select('*').eq('property_id', id).eq('property_type', 'rental').order('date', { ascending: false }),\n"
    "  ]);"
)
if old7 not in text:
    raise RuntimeError('7: renderRentalDetail Promise.all not found')
text = text.replace(old7, new7, 1)
print('7. renderRentalDetail Promise.all追加 OK')

# ─────────────────────────────────────────────────────────────
# 8. renderRentalDetail：inquiries 変数を追加
# ─────────────────────────────────────────────────────────────
old8 = (
    "  const units   = unitsRes.data || [];\n"
    "\n"
    "  const isBuilding = prop.type === 'building';"
)
new8 = (
    "  const units     = unitsRes.data || [];\n"
    "  const inquiries = inqRes.data   || [];\n"
    "\n"
    "  const isBuilding = prop.type === 'building';"
)
if old8 not in text:
    raise RuntimeError('8: units variable not found')
text = text.replace(old8, new8, 1)
print('8. rental inquiries変数追加 OK')

# ─────────────────────────────────────────────────────────────
# 9. 賃貸詳細HTML：入居履歴の直前に内見・問い合わせセクションを追加
# ─────────────────────────────────────────────────────────────
old9 = "    ${tenantSection}\n    ${unitsSection}\n    ${historySection}"
new9 = "    ${tenantSection}\n    ${unitsSection}\n    ${buildInquirySection(inquiries, id, 'rental')}\n    ${historySection}"
if old9 not in text:
    raise RuntimeError('9: rental detail sections not found')
text = text.replace(old9, new9, 1)
print('9. 賃貸詳細 inquiryセクション追加 OK')

# ─────────────────────────────────────────────────────────────
# 10. buildListTable statusCell：内見・問い合わせ件数バッジを追加
# ─────────────────────────────────────────────────────────────
old10 = (
    "  const statusCell = (p) => {\n"
    "    const d = p.property_details || {};\n"
    "    return `<div style=\"display:flex;flex-direction:column;gap:3px;\">\n"
    "      ${statusBadge(p.status)}\n"
    "      ${d.suumo_listed   ? '<span class=\"badge-suumo\">SUUMO掲載</span>' : ''}\n"
    "      ${d.hp_listed      ? '<span class=\"badge-hp\">🌐 HP掲載</span>' : ''}\n"
    "      ${d.for_sale_sign  ? '<span class=\"badge-sign\">🪧 売看板あり</span>' : ''}\n"
    "    </div>`;\n"
    "  };"
)
new10 = (
    "  const statusCell = (p) => {\n"
    "    const d  = p.property_details || {};\n"
    "    const iq = p._iq || {};\n"
    "    const iqBadge = (iq.v || iq.i)\n"
    "      ? `<div style=\"font-size:10px;color:var(--text-secondary);margin-top:1px;\">"
    "${iq.v ? '内見 '+iq.v : ''}${iq.v && iq.i ? ' / ' : ''}${iq.i ? '問 '+iq.i : ''}</div>` : '';\n"
    "    return `<div style=\"display:flex;flex-direction:column;gap:3px;\">\n"
    "      ${statusBadge(p.status)}\n"
    "      ${d.suumo_listed   ? '<span class=\"badge-suumo\">SUUMO掲載</span>' : ''}\n"
    "      ${d.hp_listed      ? '<span class=\"badge-hp\">🌐 HP掲載</span>' : ''}\n"
    "      ${d.for_sale_sign  ? '<span class=\"badge-sign\">🪧 売看板あり</span>' : ''}\n"
    "      ${iqBadge}\n"
    "    </div>`;\n"
    "  };"
)
if old10 not in text:
    raise RuntimeError('10: statusCell not found')
text = text.replace(old10, new10, 1)
print('10. statusCell 件数バッジ追加 OK')

# ─────────────────────────────────────────────────────────────
# 11. renderList：並び替え後に inquiry_logs カウントを付加
# ─────────────────────────────────────────────────────────────
old11 = (
    "  else                                     displayed = codeSort(all);\n"
    "\n"
    "  el.innerHTML = `"
)
new11 = (
    "  else                                     displayed = codeSort(all);\n"
    "\n"
    "  // 内見・問い合わせカウントを付加\n"
    "  if (displayed.length) {\n"
    "    const { data: _iqd } = await db.from('inquiry_logs')\n"
    "      .select('property_id,type').eq('property_type','sale')\n"
    "      .in('property_id', displayed.map(p => p.id));\n"
    "    if (_iqd) {\n"
    "      const _cm = {};\n"
    "      _iqd.forEach(r => {\n"
    "        if (!_cm[r.property_id]) _cm[r.property_id] = { v:0, i:0 };\n"
    "        if (r.type === 'viewing') _cm[r.property_id].v++; else _cm[r.property_id].i++;\n"
    "      });\n"
    "      displayed.forEach(p => { p._iq = _cm[p.id] || {}; });\n"
    "    }\n"
    "  }\n"
    "\n"
    "  el.innerHTML = `"
)
if old11 not in text:
    raise RuntimeError('11: codeSort + el.innerHTML not found')
text = text.replace(old11, new11, 1)
print('11. renderList 件数取得追加 OK')

# ─────────────────────────────────────────────────────────────
# 12. inquiry_v1.js を最後の </script> の直前に挿入
# ─────────────────────────────────────────────────────────────
last_script = text.rfind('</script>')
if last_script == -1:
    raise RuntimeError('12: </script> not found')
text = text[:last_script] + inquiry_js.rstrip('\n') + '\n\n' + text[last_script:]
print('12. inquiry_v1.js 挿入 OK')

# ── 書き戻し ──────────────────────────────────────────────────
if crlf:
    text = text.replace('\n', '\r\n')
with open(html_path, 'wb') as f:
    f.write(text.encode('utf-8'))

print('\npatch_v16 完了')
