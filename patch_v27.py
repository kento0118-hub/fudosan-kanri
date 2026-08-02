"""
patch_v27.py
  整地整備台帳リニューアル
  ① グローバル変数追加
  ② CSS 追加
  ③ showLogs() 置き換え
  ④ ヘルパー関数追加
  ⑤ 新規関数群をファイル末尾に追加
実行: cd fudosan_kanri && python patch_v27.py
"""
import sys

SRC = 'index.html'
with open(SRC, 'rb') as f:
    raw = f.read()
text = raw.replace(b'\r\n', b'\n').decode('utf-8')
original = text

# ════════════════════════════════════════════
# Step 1: グローバル変数追加
# ════════════════════════════════════════════
find1 = "// ── アプリ状態 ──\nlet state = {"
repl1 = (
    "// ── アプリ状態 ──\n"
    "let _visitSeason = 'normal';\n"
    "let _visitCheckItemAdminTab = 'land-normal';\n"
    "\n"
    "let state = {"
)
if find1 not in text:
    print('Step 1 FAILED'); sys.exit(1)
text = text.replace(find1, repl1, 1)
print('Step 1 OK: グローバル変数追加')

# ════════════════════════════════════════════
# Step 2: CSS 追加（.btn-back:hover の直後）
# ════════════════════════════════════════════
find2 = "    .btn-back:hover { background: var(--bg-card-hover); }\n\n    /* ── バッジ ── */"
repl2 = (
    "    .btn-back:hover { background: var(--bg-card-hover); }\n"
    "\n"
    "    /* ── 整地整備台帳 ── */\n"
    "    .task-item {\n"
    "      display: flex; align-items: center; gap: 10px;\n"
    "      padding: 10px 14px;\n"
    "      border-bottom: 1px solid var(--border);\n"
    "    }\n"
    "    .task-item:last-child { border-bottom: none; }\n"
    "    .task-item.done > span { text-decoration: line-through; color: var(--text-muted); }\n"
    "    .check-grid {\n"
    "      display: grid; grid-template-columns: 1fr 1fr; gap: 10px;\n"
    "      padding: 4px 0;\n"
    "    }\n"
    "    .check-grid-item {\n"
    "      display: flex; align-items: center; gap: 8px;\n"
    "      font-size: 13px;\n"
    "    }\n"
    "    .visit-badge-winter {\n"
    "      display: inline-block; padding: 2px 8px; border-radius: 10px;\n"
    "      font-size: 11px; font-weight: 600;\n"
    "      background: #e8f0fe; color: #2a7ae2;\n"
    "    }\n"
    "    .visit-badge-normal {\n"
    "      display: inline-block; padding: 2px 8px; border-radius: 10px;\n"
    "      font-size: 11px; font-weight: 600;\n"
    "      background: #d4f0e3; color: #2e9e68;\n"
    "    }\n"
    "\n"
    "    /* ── バッジ ── */"
)
if find2 not in text:
    print('Step 2 FAILED'); sys.exit(1)
text = text.replace(find2, repl2, 1)
print('Step 2 OK: CSS 追加')

# ════════════════════════════════════════════
# Step 3: showLogs() 置き換え
# ════════════════════════════════════════════
find3 = (
    "async function showLogs(filterPropId) {\n"
    "  state.view       = 'logs';\n"
    "  state.logsFilter = filterPropId || '';\n"
    "  setActiveNav('nav-logs');\n"
    "  await renderLogs(state.logsFilter);\n"
    "}"
)
repl3 = (
    "async function showLogs() {\n"
    "  state.view = 'logs';\n"
    "  setActiveNav('nav-logs');\n"
    "  await renderSiteVisitList();\n"
    "}"
)
if find3 not in text:
    print('Step 3 FAILED'); sys.exit(1)
text = text.replace(find3, repl3, 1)
print('Step 3 OK: showLogs() 置き換え')

# ════════════════════════════════════════════
# Step 4: ヘルパー関数を getCurrentSeason() の直後に追加
# ════════════════════════════════════════════
find4 = (
    "function getCurrentSeason() {\n"
    "  const m = new Date().getMonth() + 1;\n"
    "  if (m >= 3 && m <= 5)  return 'spring';\n"
    "  if (m >= 6 && m <= 8)  return 'summer';\n"
    "  if (m >= 9 && m <= 11) return 'fall';\n"
    "  return 'winter';\n"
    "}"
)
repl4 = (
    "function getCurrentSeason() {\n"
    "  const m = new Date().getMonth() + 1;\n"
    "  if (m >= 3 && m <= 5)  return 'spring';\n"
    "  if (m >= 6 && m <= 8)  return 'summer';\n"
    "  if (m >= 9 && m <= 11) return 'fall';\n"
    "  return 'winter';\n"
    "}\n"
    "\n"
    "function selectVisitSeason(season, btn) {\n"
    "  _visitSeason = season;\n"
    "  document.querySelectorAll('[id^=\"vf-season-\"]').forEach(b => b.classList.remove('active'));\n"
    "  btn.classList.add('active');\n"
    "}\n"
    "\n"
    "function seasonLabel(s) {\n"
    "  return s === 'winter' ? '❄️ 冬季' : '🌿 通常期';\n"
    "}\n"
    "\n"
    "function seasonBadge(s) {\n"
    "  return s === 'winter'\n"
    "    ? '<span class=\"visit-badge-winter\">❄️ 冬季</span>'\n"
    "    : '<span class=\"visit-badge-normal\">🌿 通常期</span>';\n"
    "}"
)
if find4 not in text:
    print('Step 4 FAILED'); sys.exit(1)
text = text.replace(find4, repl4, 1)
print('Step 4 OK: ヘルパー関数追加')

# ════════════════════════════════════════════
# Step 5: 新規関数群をファイル末尾（</script>の直前）に追加
# ════════════════════════════════════════════
find5 = "</script>\n</body>"

NEW_FUNCTIONS = """
// ════════════════════════════════════════════════════════════
// 整地整備台帳
// ════════════════════════════════════════════════════════════

// ── 台帳トップ（訪問記録一覧）──
async function renderSiteVisitList() {
  const el = document.getElementById('content');
  el.innerHTML = '<div style="padding:40px;text-align:center;color:var(--text-muted);">読み込み中…</div>';

  const [visitsRes, tasksRes] = await Promise.all([
    db.from('site_visits')
      .select('*, properties(id, property_name, address, type, code)')
      .order('visit_date', { ascending: false }),
    db.from('site_tasks').select('visit_id, is_done'),
  ]);

  const visits = visitsRes.data || [];
  const tasks  = tasksRes.data  || [];

  const taskMap = {};
  tasks.forEach(t => {
    if (!taskMap[t.visit_id]) taskMap[t.visit_id] = { total: 0, done: 0 };
    taskMap[t.visit_id].total++;
    if (t.is_done) taskMap[t.visit_id].done++;
  });

  const rows = visits.map(v => {
    const prop = v.properties || {};
    const tm   = taskMap[v.id] || { total: 0, done: 0 };
    const taskBadge = tm.total === 0
      ? '<span style="color:var(--text-muted);font-size:12px;">なし</span>'
      : tm.done < tm.total
        ? `<span style="color:#c94040;font-size:12px;font-weight:600;">${tm.done}/${tm.total}件</span>`
        : `<span style="color:#2e9e68;font-size:12px;font-weight:600;">✅ ${tm.total}件完了</span>`;
    const approvedBadge = v.admin_approved_at
      ? '<span style="font-size:11px;background:#d4f0e3;color:#2e9e68;padding:2px 8px;border-radius:10px;font-weight:600;">✅ 承認済</span>'
      : '<span style="color:var(--text-muted);font-size:12px;">—</span>';
    const typeBadge = prop.type === 'land'
      ? '<span class="badge-land">土地</span>'
      : prop.type === 'house'
        ? '<span class="badge-house">建物</span>'
        : '';
    return `
      <tr onclick="showVisitDetail('${v.id}')" style="cursor:pointer;">
        <td style="white-space:nowrap;">${v.visit_date || '—'}</td>
        <td style="max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
          ${esc(prop.property_name || prop.address || '（名称未入力）')}
        </td>
        <td>${typeBadge}</td>
        <td>${seasonBadge(v.season)}</td>
        <td>${esc(v.visitor_name || '—')}</td>
        <td>${taskBadge}</td>
        <td>${approvedBadge}</td>
        <td onclick="event.stopPropagation()">
          <button class="btn-sm" onclick="showVisitDetail('${v.id}')">詳細</button>
        </td>
      </tr>`;
  }).join('');

  el.innerHTML = `
    <div class="page-header">
      <div>
        <div class="page-title">📋 整地整備台帳</div>
        <div class="page-sub">現地訪問記録 ${visits.length}件</div>
      </div>
      <div style="display:flex;gap:8px;">
        <button class="btn-secondary" onclick="showCheckItemAdmin()" style="font-size:12px;">⚙️ チェック項目管理</button>
        <button class="btn-primary" onclick="showVisitForm()">＋ 訪問記録を追加</button>
      </div>
    </div>

    ${visits.length === 0
      ? '<div class="section" style="text-align:center;padding:40px;color:var(--text-muted);">訪問記録がありません。「＋ 訪問記録を追加」から登録してください。</div>'
      : `<div class="section" style="padding:0;overflow:hidden;">
           <div style="overflow-x:auto;">
             <table class="data-table">
               <thead><tr>
                 <th>訪問日</th><th>物件名</th><th>種別</th><th>季節</th>
                 <th>担当者</th><th>対応タスク</th><th>上長承認</th><th></th>
               </tr></thead>
               <tbody>${rows}</tbody>
             </table>
           </div>
         </div>`
    }
  `;
}

// ── 訪問記録詳細 ──
async function showVisitDetail(visitId) {
  state.view = 'visit-detail';
  const el = document.getElementById('content');
  el.innerHTML = '<div style="padding:40px;text-align:center;color:var(--text-muted);">読み込み中…</div>';

  const [visitRes, checksRes, tasksRes, itemsRes] = await Promise.all([
    db.from('site_visits')
      .select('*, properties(id, property_name, address, type, code)')
      .eq('id', visitId).single(),
    db.from('site_visit_checks').select('*').eq('visit_id', visitId),
    db.from('site_tasks').select('*').eq('visit_id', visitId).order('created_at'),
    db.from('site_check_items').select('*').eq('is_active', true).order('order_index'),
  ]);

  if (visitRes.error) { toast('取得失敗: ' + visitRes.error.message, 'error'); return; }
  const visit  = visitRes.data;
  const checks = checksRes.data || [];
  const tasks  = tasksRes.data  || [];
  const prop   = visit.properties || {};

  const myItems = (itemsRes.data || []).filter(i =>
    i.property_type === prop.type && i.season === visit.season
  );

  const checkMap = {};
  checks.forEach(c => { checkMap[c.check_item_id] = c; });

  let photos = [];
  try { photos = JSON.parse(visit.photo_urls || '[]'); } catch(e) {}

  const photosHtml = photos.length
    ? `<div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:8px;">
        ${photos.map((url, i) => `
          <div style="position:relative;">
            <img src="${esc(url)}" style="width:120px;height:90px;object-fit:cover;border-radius:6px;border:1px solid var(--border);">
            <button onclick="deleteVisitPhoto('${visitId}',${i})"
              style="position:absolute;top:2px;right:2px;background:rgba(0,0,0,0.5);color:#fff;border:none;border-radius:50%;width:20px;height:20px;font-size:10px;cursor:pointer;line-height:20px;text-align:center;">✕</button>
          </div>`).join('')}
       </div>`
    : '<div style="color:var(--text-muted);font-size:12px;margin-top:6px;">写真なし</div>';

  const tasksHtml = tasks.map(t => `
    <div class="task-item ${t.is_done ? 'done' : ''}" id="task-${t.id}">
      <input type="checkbox" ${t.is_done ? 'checked' : ''}
        onchange="toggleSiteTask('${t.id}','${visitId}',this.checked)"
        style="width:16px;height:16px;cursor:pointer;flex-shrink:0;">
      <span style="flex:1;font-size:13px;">${esc(t.content)}</span>
      ${t.done_at ? `<span style="font-size:11px;color:var(--text-muted);">${t.done_at.slice(0,10)}</span>` : ''}
      <button class="btn-sm btn-danger" onclick="deleteSiteTask('${t.id}','${visitId}')">削除</button>
    </div>`).join('');

  el.innerHTML = `
    <div class="page-header">
      <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;">
        <button class="btn-back" onclick="showLogs()">← 台帳へ</button>
        <div>
          <div class="page-title">📋 ${esc(prop.property_name || prop.address || '（名称未入力）')}</div>
          <div style="display:flex;gap:6px;margin-top:4px;flex-wrap:wrap;align-items:center;">
            ${seasonBadge(visit.season)}
            <span style="font-size:13px;color:var(--text-secondary);">訪問日: ${visit.visit_date}</span>
            ${visit.visitor_name ? `<span style="font-size:13px;color:var(--text-secondary);">担当: ${esc(visit.visitor_name)}</span>` : ''}
          </div>
        </div>
      </div>
      <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
        ${visit.admin_approved_at
          ? `<span style="font-size:12px;background:#d4f0e3;color:#2e9e68;padding:6px 14px;border-radius:6px;font-weight:600;">
               ✅ 承認済　${visit.admin_approved_at.slice(0,10)}
             </span>
             <button class="btn-sm" onclick="clearVisitApproval('${visitId}')">取消</button>`
          : `<button class="btn-primary" onclick="approveVisit('${visitId}')">✅ 上長承認する</button>`
        }
        <button class="btn-danger btn-sm" onclick="deleteVisit('${visitId}')">🗑 削除</button>
      </div>
    </div>

    <div class="two-col">
      <div class="section">
        <div class="section-title"><span class="icon">✅</span>現地チェック項目</div>
        ${myItems.length === 0
          ? '<div style="color:var(--text-muted);font-size:13px;">この物件種別・季節のチェック項目がありません</div>'
          : `<div class="check-grid">
              ${myItems.map(item => {
                const chk = checkMap[item.id];
                const checked = chk?.is_checked || false;
                return `<div class="check-grid-item">
                  <input type="checkbox" ${checked ? 'checked' : ''}
                    onchange="toggleVisitCheck('${visitId}','${item.id}',this.checked)"
                    style="width:15px;height:15px;cursor:pointer;flex-shrink:0;">
                  <span style="${checked ? 'color:var(--text-muted);text-decoration:line-through;' : ''}">${esc(item.label)}</span>
                </div>`;
              }).join('')}
             </div>`
        }
      </div>

      <div class="section">
        <div class="section-title"><span class="icon">📝</span>気づき・メモ</div>
        <textarea id="visit-notes-${visitId}" rows="6"
          style="width:100%;padding:10px;border:1px solid var(--border);border-radius:6px;font-size:13px;font-family:inherit;resize:vertical;"
          placeholder="現地で気づいたことを入力...">${esc(visit.notes || '')}</textarea>
        <button class="btn-primary" style="margin-top:8px;" onclick="saveVisitNotes('${visitId}')">メモを保存</button>
      </div>
    </div>

    <div class="section">
      <div class="section-title"><span class="icon">📷</span>現地写真</div>
      ${photosHtml}
      <div style="margin-top:10px;">
        <label class="btn-secondary" style="cursor:pointer;display:inline-block;padding:6px 14px;">
          📷 写真を追加
          <input type="file" accept="image/*" multiple style="display:none;"
            onchange="uploadVisitPhotos('${visitId}',this)">
        </label>
      </div>
    </div>

    <div class="section">
      <div class="section-title"><span class="icon">🔧</span>対応タスク</div>
      <div id="task-list-${visitId}">
        ${tasks.length === 0
          ? '<div style="color:var(--text-muted);font-size:13px;padding:8px 0;">タスクなし</div>'
          : tasksHtml}
      </div>
      <div style="display:flex;gap:8px;margin-top:12px;">
        <input type="text" id="new-task-input-${visitId}"
          style="flex:1;padding:8px 12px;border:1px solid var(--border);border-radius:6px;font-size:13px;font-family:inherit;"
          placeholder="対応内容を入力..."
          onkeydown="if(event.key==='Enter')addSiteTask('${visitId}')">
        <button class="btn-primary" onclick="addSiteTask('${visitId}')">＋ 追加</button>
      </div>
    </div>
  `;
}

// ── 訪問記録追加フォーム ──
async function showVisitForm() {
  state.view = 'visit-form';
  const el = document.getElementById('content');
  el.innerHTML = '<div style="padding:40px;text-align:center;color:var(--text-muted);">読み込み中…</div>';

  const { data: props } = await db.from('properties')
    .select('id, property_name, address, type, code')
    .order('code');

  const today = new Date().toISOString().slice(0, 10);
  const m = new Date().getMonth() + 1;
  const autoSeason = (m === 12 || m <= 3) ? 'winter' : 'normal';
  _visitSeason = autoSeason;

  const propOptions = (props || []).map(p =>
    `<option value="${p.id}">${esc(p.code ? p.code + ' ' : '')}${esc(p.property_name || p.address || '（名称未入力）')}</option>`
  ).join('');

  el.innerHTML = `
    <div class="page-header">
      <div><div class="page-title">📋 現地訪問記録を追加</div></div>
      <button class="btn-back" onclick="showLogs()">← 台帳へ</button>
    </div>

    <div class="section" style="max-width:600px;">
      <div class="form-group" style="margin-bottom:16px;">
        <label style="font-size:12px;font-weight:600;color:var(--text-secondary);display:block;margin-bottom:6px;">物件</label>
        <select id="vf-property" class="qs-control">
          <option value="">物件を選択...</option>
          ${propOptions}
        </select>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label style="font-size:12px;font-weight:600;color:var(--text-secondary);display:block;margin-bottom:6px;">訪問日</label>
          <input type="date" id="vf-date" class="qs-control" value="${today}">
        </div>
        <div class="form-group">
          <label style="font-size:12px;font-weight:600;color:var(--text-secondary);display:block;margin-bottom:6px;">担当者</label>
          <input type="text" id="vf-visitor" class="qs-control" placeholder="例：安部">
        </div>
      </div>

      <div class="form-group" style="margin-bottom:16px;">
        <label style="font-size:12px;font-weight:600;color:var(--text-secondary);display:block;margin-bottom:6px;">季節区分</label>
        <div style="display:flex;gap:6px;">
          <button type="button" id="vf-season-normal" class="filter-tab ${autoSeason==='normal'?'active':''}"
            onclick="selectVisitSeason('normal',this)">🌿 通常期</button>
          <button type="button" id="vf-season-winter" class="filter-tab ${autoSeason==='winter'?'active':''}"
            onclick="selectVisitSeason('winter',this)">❄️ 冬季</button>
        </div>
      </div>

      <div class="form-group" style="margin-bottom:24px;">
        <label style="font-size:12px;font-weight:600;color:var(--text-secondary);display:block;margin-bottom:6px;">気づき・メモ</label>
        <textarea id="vf-notes" rows="5" class="qs-control"
          style="resize:vertical;" placeholder="現地で気づいたことを入力..."></textarea>
      </div>

      <button class="btn-primary" style="min-width:140px;" onclick="saveVisitForm()">💾 記録を保存して詳細へ</button>
    </div>
  `;
}

async function saveVisitForm() {
  const propId = document.getElementById('vf-property')?.value;
  const date   = document.getElementById('vf-date')?.value;
  if (!propId) { toast('物件を選択してください', 'error'); return; }
  if (!date)   { toast('訪問日を入力してください', 'error'); return; }

  const { data: newVisit, error } = await db.from('site_visits').insert({
    property_id:  propId,
    visit_date:   date,
    visitor_name: document.getElementById('vf-visitor')?.value.trim() || null,
    season:       _visitSeason,
    notes:        document.getElementById('vf-notes')?.value.trim() || null,
  }).select().single();

  if (error) { toast('保存失敗: ' + error.message, 'error'); return; }
  toast('訪問記録を保存しました', 'success');
  await showVisitDetail(newVisit.id);
}

// ── チェック・タスク操作 ──
async function toggleVisitCheck(visitId, itemId, checked) {
  const { error } = await db.from('site_visit_checks').upsert({
    visit_id: visitId, check_item_id: itemId, is_checked: checked
  }, { onConflict: 'visit_id,check_item_id' });
  if (error) toast('保存失敗: ' + error.message, 'error');
}

async function saveVisitNotes(visitId) {
  const notes = document.getElementById(`visit-notes-${visitId}`)?.value || '';
  const { error } = await db.from('site_visits').update({ notes }).eq('id', visitId);
  if (error) { toast('保存失敗: ' + error.message, 'error'); return; }
  toast('メモを保存しました', 'success');
}

async function addSiteTask(visitId) {
  const input = document.getElementById(`new-task-input-${visitId}`);
  const content = input?.value.trim();
  if (!content) return;
  const { error } = await db.from('site_tasks').insert({ visit_id: visitId, content });
  if (error) { toast('追加失敗: ' + error.message, 'error'); return; }
  input.value = '';
  toast('タスクを追加しました', 'success');
  await showVisitDetail(visitId);
}

async function toggleSiteTask(taskId, visitId, done) {
  const { error } = await db.from('site_tasks').update({
    is_done: done, done_at: done ? new Date().toISOString() : null
  }).eq('id', taskId);
  if (error) { toast('更新失敗: ' + error.message, 'error'); return; }
  await showVisitDetail(visitId);
}

async function deleteSiteTask(taskId, visitId) {
  if (!confirm('このタスクを削除しますか？')) return;
  await db.from('site_tasks').delete().eq('id', taskId);
  await showVisitDetail(visitId);
}

async function approveVisit(visitId) {
  const { error } = await db.from('site_visits').update({
    admin_approved_at: new Date().toISOString()
  }).eq('id', visitId);
  if (error) { toast('承認失敗: ' + error.message, 'error'); return; }
  toast('承認しました', 'success');
  await showVisitDetail(visitId);
}

async function clearVisitApproval(visitId) {
  await db.from('site_visits').update({ admin_approved_at: null }).eq('id', visitId);
  await showVisitDetail(visitId);
}

async function deleteVisit(visitId) {
  if (!confirm('この訪問記録を削除しますか？（タスク・チェックも削除されます）')) return;
  await db.from('site_visits').delete().eq('id', visitId);
  toast('削除しました', 'success');
  await showLogs();
}

// ── 写真アップロード ──
async function uploadVisitPhotos(visitId, input) {
  const files = Array.from(input.files);
  if (!files.length) return;
  toast('アップロード中…', 'success');

  const { data: visit } = await db.from('site_visits').select('photo_urls').eq('id', visitId).single();
  let urls = [];
  try { urls = JSON.parse(visit?.photo_urls || '[]'); } catch(e) {}

  for (const file of files) {
    const ext  = file.name.split('.').pop();
    const path = `site-visits/${visitId}/${Date.now()}.${ext}`;
    const { error: upErr } = await db.storage.from('property-photos').upload(path, file);
    if (upErr) { toast('アップロード失敗: ' + upErr.message, 'error'); continue; }
    const { data: urlData } = db.storage.from('property-photos').getPublicUrl(path);
    if (urlData?.publicUrl) urls.push(urlData.publicUrl);
  }

  await db.from('site_visits').update({ photo_urls: JSON.stringify(urls) }).eq('id', visitId);
  toast('写真を追加しました', 'success');
  await showVisitDetail(visitId);
}

async function deleteVisitPhoto(visitId, index) {
  if (!confirm('この写真を削除しますか？')) return;
  const { data: visit } = await db.from('site_visits').select('photo_urls').eq('id', visitId).single();
  let urls = [];
  try { urls = JSON.parse(visit?.photo_urls || '[]'); } catch(e) {}
  urls.splice(index, 1);
  await db.from('site_visits').update({ photo_urls: JSON.stringify(urls) }).eq('id', visitId);
  await showVisitDetail(visitId);
}

// ── チェック項目管理 ──
async function showCheckItemAdmin() {
  state.view = 'check-item-admin';
  await renderCheckItemAdmin();
}

async function renderCheckItemAdmin() {
  const el = document.getElementById('content');
  const { data: items } = await db.from('site_check_items')
    .select('*').eq('is_active', true).order('order_index');

  const tabs = [
    { key: 'land-normal',  pt: 'land',  s: 'normal', label: '🌐 土地（通常期）' },
    { key: 'land-winter',  pt: 'land',  s: 'winter', label: '🌐 土地（冬季）' },
    { key: 'house-normal', pt: 'house', s: 'normal', label: '🏡 建物（通常期）' },
    { key: 'house-winter', pt: 'house', s: 'winter', label: '🏡 建物（冬季）' },
  ];

  const currentTab = tabs.find(t => t.key === _visitCheckItemAdminTab) || tabs[0];
  const myItems = (items || []).filter(i =>
    i.property_type === currentTab.pt && i.season === currentTab.s
  );

  el.innerHTML = `
    <div class="page-header">
      <div><div class="page-title">⚙️ チェック項目管理</div></div>
      <button class="btn-back" onclick="showLogs()">← 台帳へ</button>
    </div>

    <div class="filter-tabs" style="margin-bottom:16px;">
      ${tabs.map(t => `
        <button class="filter-tab ${t.key===_visitCheckItemAdminTab?'active':''}"
          onclick="_visitCheckItemAdminTab='${t.key}';renderCheckItemAdmin()">${t.label}</button>
      `).join('')}
    </div>

    <div class="section" style="max-width:560px;">
      <div>
        ${myItems.map(item => `
          <div style="display:flex;align-items:center;gap:10px;padding:10px 0;border-bottom:1px solid var(--border);">
            <span style="flex:1;font-size:13px;">${esc(item.label)}</span>
            <button class="btn-sm btn-danger" onclick="deactivateCheckItem('${item.id}')">削除</button>
          </div>`).join('')}
        ${myItems.length === 0 ? '<div style="color:var(--text-muted);font-size:13px;padding:12px 0;">項目がありません</div>' : ''}
      </div>

      <div style="display:flex;gap:8px;margin-top:16px;">
        <input type="text" id="new-check-item-input"
          style="flex:1;padding:8px 12px;border:1px solid var(--border);border-radius:6px;font-size:13px;font-family:inherit;"
          placeholder="新しい項目を入力..."
          onkeydown="if(event.key==='Enter')addCheckItem('${currentTab.pt}','${currentTab.s}',${myItems.length+1})">
        <button class="btn-primary"
          onclick="addCheckItem('${currentTab.pt}','${currentTab.s}',${myItems.length+1})">＋ 追加</button>
      </div>
    </div>
  `;
}

async function addCheckItem(propertyType, season, orderIndex) {
  const input = document.getElementById('new-check-item-input');
  const label = input?.value.trim();
  if (!label) return;
  const { error } = await db.from('site_check_items').insert({
    property_type: propertyType, season, label, order_index: orderIndex
  });
  if (error) { toast('追加失敗: ' + error.message, 'error'); return; }
  input.value = '';
  toast('追加しました', 'success');
  await renderCheckItemAdmin();
}

async function deactivateCheckItem(itemId) {
  if (!confirm('この項目を削除しますか？')) return;
  await db.from('site_check_items').update({ is_active: false }).eq('id', itemId);
  toast('削除しました', 'success');
  await renderCheckItemAdmin();
}
"""

repl5 = NEW_FUNCTIONS + "</script>\n</body>"
if find5 not in text:
    print('Step 5 FAILED'); sys.exit(1)
text = text.replace(find5, repl5, 1)
print('Step 5 OK: 新規関数群追加')

# ════════════════════════════════════════════
# 書き出し
# ════════════════════════════════════════════
if text == original:
    print('ERROR: no changes made'); sys.exit(1)

out = text.replace('\n', '\r\n').encode('utf-8')
with open(SRC, 'wb') as f:
    f.write(out)
print('\n=== All 5 steps OK ===')
