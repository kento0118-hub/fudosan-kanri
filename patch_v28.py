#!/usr/bin/env python3
# patch_v28.py
# 6-point modification:
# 1. Name changes: 整地整備台帳→物件管理台帳, 敷地整備台帳→物件管理台帳, チェック項目管理→チェック項目設定
# 2. Remove 管理チェックリスト section from showDetail(), keep 実施記録 only
# 3. Add 訪問記録 + 修繕記録 sections to showDetail()
# 4. Add showVisitFormForProp() / showRepairFormForProp() helpers
# 5. Replace _checkAlert/要確認 badge with _taskAlert/タスク未対応 in renderList()
# 6. Rewrite 修繕台帳: renderRepairList + detail/form/crud functions

import sys

SRC = r'C:\Users\abenote-PC\RenovationAI\fudosan_kanri\index.html'

with open(SRC, 'rb') as f:
    raw = f.read()

text = raw.decode('utf-8').replace('\r\n', '\n').replace('\r', '\n')

errors = []

def replace_one(t, old, new, label):
    if old not in t:
        errors.append(f'STEP {label}: find string not found')
        return t
    n = t.count(old)
    if n > 1:
        errors.append(f'STEP {label}: find string found {n} times (ambiguous)')
        return t
    return t.replace(old, new)

def replace_all(t, old, new, label):
    if old not in t:
        errors.append(f'STEP {label}: find string not found')
        return t
    return t.replace(old, new)

# ────────────────────────────────────────────────────────────
# STEP 1: Name changes (replace_all)
# ────────────────────────────────────────────────────────────
text = replace_all(text, '整地整備台帳', '物件管理台帳', '1a')
text = replace_all(text, '敷地整備台帳', '物件管理台帳', '1b')
text = replace_all(text, 'チェック項目管理', 'チェック項目設定', '1c')

# ────────────────────────────────────────────────────────────
# STEP 2: renderList - replace チェックアラート with タスクアラート
# ────────────────────────────────────────────────────────────
OLD_CHECKALERT = """  // 今の季節のチェックリスト未完了チェック
  const _currentSeason = getCurrentSeason();
  const _seasonItems = state.checklistItems.filter(i =>
    i.season === _currentSeason &&
    (i.property_type === 'both' || displayed.some(p => p.type === i.property_type))
  );

  if (displayed.length && _seasonItems.length) {
    const { data: _chkd } = await db.from('checklist_checks')
      .select('property_id,item_id,is_checked')
      .in('property_id', displayed.map(p => p.id));

    displayed.forEach(p => {
      if (p._isRental) { p._checkAlert = false; return; }
      const myItems = _seasonItems.filter(i => i.property_type === 'both' || i.property_type === p.type);
      if (!myItems.length) { p._checkAlert = false; return; }
      const myChecks = (_chkd || []).filter(c => c.property_id === p.id);
      const allDone = myItems.every(item =>
        myChecks.some(c => c.item_id === item.id && c.is_checked)
      );
      p._checkAlert = !allDone;
    });
  }"""

NEW_CHECKALERT = """  // 未対応タスクチェック
  if (displayed.length) {
    const _nonRental = displayed.filter(p => !p._isRental);
    if (_nonRental.length) {
      const { data: _openVisits } = await db.from('site_visits')
        .select('id, property_id')
        .in('property_id', _nonRental.map(p => p.id));

      if (_openVisits?.length) {
        const { data: _openTasks } = await db.from('site_tasks')
          .select('visit_id, is_done')
          .in('visit_id', _openVisits.map(v => v.id))
          .eq('is_done', false);

        const _propHasUndone = new Set();
        (_openTasks || []).forEach(t => {
          const _v = _openVisits.find(v => v.id === t.visit_id);
          if (_v) _propHasUndone.add(_v.property_id);
        });
        displayed.forEach(p => { p._taskAlert = _propHasUndone.has(p.id); });
      }
    }
  }"""

text = replace_one(text, OLD_CHECKALERT, NEW_CHECKALERT, '2')

# ────────────────────────────────────────────────────────────
# STEP 3: alertBadge - _checkAlert → _taskAlert, 要確認 → タスク未対応
# ────────────────────────────────────────────────────────────
OLD_BADGE = """  const alertBadge = p => p._checkAlert
    ? '<span style="font-size:10px;background:#fde8e8;color:#c94040;padding:2px 6px;border-radius:4px;font-weight:700;margin-left:4px;">⚠️ 要確認</span>' : '';"""

NEW_BADGE = """  const alertBadge = p => p._taskAlert
    ? '<span style="font-size:10px;background:#fde8e8;color:#c94040;padding:2px 6px;border-radius:4px;font-weight:700;margin-left:4px;">⚠️ タスク未対応</span>' : '';"""

text = replace_one(text, OLD_BADGE, NEW_BADGE, '3')

# ────────────────────────────────────────────────────────────
# STEP 4: renderDetail - add site_visits + repair_logs fetch after isLand
# ────────────────────────────────────────────────────────────
OLD_ISLAND = """  const inquiries    = inqRes.data        || [];
  const det          = prop.property_details || {};
  const isLand = prop.type === 'land';"""

NEW_ISLAND = """  const inquiries    = inqRes.data        || [];
  const det          = prop.property_details || {};
  const isLand = prop.type === 'land';

  // ── 訪問記録 ──
  const { data: _visitsData } = await db.from('site_visits')
    .select('id, visit_date, visitor_name, season, admin_approved_at')
    .eq('property_id', id)
    .order('visit_date', { ascending: false });
  const visits = _visitsData || [];
  let visitTaskMap = {};
  if (visits.length) {
    const { data: _vtasks } = await db.from('site_tasks')
      .select('visit_id, is_done, content')
      .in('visit_id', visits.map(v => v.id));
    (_vtasks || []).forEach(t => {
      if (!visitTaskMap[t.visit_id]) visitTaskMap[t.visit_id] = { total:0, done:0, undone:[] };
      visitTaskMap[t.visit_id].total++;
      if (t.is_done) visitTaskMap[t.visit_id].done++;
      else visitTaskMap[t.visit_id].undone.push(t.content);
    });
  }

  // ── 修繕記録（建物のみ） ──
  let repairsForProp = [];
  let repairTaskMap = {};
  if (!isLand) {
    const { data: _rdata } = await db.from('repair_logs')
      .select('id, repair_date, visitor_name, season, admin_approved_at')
      .eq('property_id', id)
      .order('repair_date', { ascending: false });
    repairsForProp = _rdata || [];
    if (repairsForProp.length) {
      const { data: _rtasks } = await db.from('repair_tasks')
        .select('repair_id, is_done, content')
        .in('repair_id', repairsForProp.map(r => r.id));
      (_rtasks || []).forEach(t => {
        if (!repairTaskMap[t.repair_id]) repairTaskMap[t.repair_id] = { total:0, done:0, undone:[] };
        repairTaskMap[t.repair_id].total++;
        if (t.is_done) repairTaskMap[t.repair_id].done++;
        else repairTaskMap[t.repair_id].undone.push(t.content);
      });
    }
  }"""

text = replace_one(text, OLD_ISLAND, NEW_ISLAND, '4')

# ────────────────────────────────────────────────────────────
# STEP 5: Add visitsSection + repairsSection variables before el.innerHTML
# ────────────────────────────────────────────────────────────
OLD_BUILT = """  // ── 築年月表示（中古住宅） ──
  const builtDisplay = !isLand && det.built_date ? displayBuiltDate(det.built_date) : null;

  el.innerHTML = `"""

NEW_BUILT = """  // ── 築年月表示（中古住宅） ──
  const builtDisplay = !isLand && det.built_date ? displayBuiltDate(det.built_date) : null;

  // ── 訪問記録テーブル行 ──
  const _vRows = visits.map(v => {
    const tm = visitTaskMap[v.id] || { total:0, done:0, undone:[] };
    const tb = tm.total === 0
      ? '<span style="color:var(--text-muted);font-size:11px;">なし</span>'
      : tm.done < tm.total
        ? '<span style="color:#c94040;font-size:11px;font-weight:600;">⚠️ ' + tm.undone.length + '件未対応</span>'
        : '<span style="color:#2e9e68;font-size:11px;">✅ 完了</span>';
    return `<tr onclick="showVisitDetail('${v.id}')" style="cursor:pointer;">
      <td>${v.visit_date}</td>
      <td>${v.season === 'winter' ? '❄️ 冬季' : '🌿 通常期'}</td>
      <td>${esc(v.visitor_name || '—')}</td>
      <td>${tb}</td>
      <td>${v.admin_approved_at ? '✅' : '—'}</td>
      <td><button class="btn-sm" onclick="event.stopPropagation();showVisitDetail('${v.id}')">詳細</button></td>
    </tr>`;
  }).join('');
  const visitsSection = `
    <div class="section" style="margin-top:16px;">
      <div class="section-title" style="justify-content:space-between;">
        <span><span class="icon">📋</span>訪問記録</span>
        <button class="btn-sm" style="background:var(--accent);color:#fff;border-color:var(--accent);"
          onclick="showVisitFormForProp('${id}')">＋ 訪問記録を追加</button>
      </div>
      ${visits.length === 0
        ? '<div style="color:var(--text-muted);font-size:13px;padding:8px 0;">訪問記録がありません</div>'
        : '<div style="overflow-x:auto;"><table class="data-table"><thead><tr><th>訪問日</th><th>季節</th><th>担当者</th><th>未対応タスク</th><th>承認</th><th></th></tr></thead><tbody>' + _vRows + '</tbody></table></div>'
      }
    </div>
  `;

  // ── 修繕記録テーブル行 ──
  const _rRows = repairsForProp.map(r => {
    const tm = repairTaskMap[r.id] || { total:0, done:0, undone:[] };
    const tb = tm.total === 0
      ? '<span style="color:var(--text-muted);font-size:11px;">なし</span>'
      : tm.done < tm.total
        ? '<span style="color:#c94040;font-size:11px;font-weight:600;">⚠️ ' + tm.undone.length + '件未対応</span>'
        : '<span style="color:#2e9e68;font-size:11px;">✅ 完了</span>';
    return `<tr onclick="showRepairDetail('${r.id}')" style="cursor:pointer;">
      <td>${r.repair_date || '—'}</td>
      <td>${r.season === 'winter' ? '❄️ 冬季' : '🌿 通常期'}</td>
      <td>${esc(r.visitor_name || '—')}</td>
      <td>${tb}</td>
      <td>${r.admin_approved_at ? '✅' : '—'}</td>
      <td><button class="btn-sm" onclick="event.stopPropagation();showRepairDetail('${r.id}')">詳細</button></td>
    </tr>`;
  }).join('');
  const repairsSection = !isLand ? `
    <div class="section" style="margin-top:16px;">
      <div class="section-title" style="justify-content:space-between;">
        <span><span class="icon">🔧</span>修繕記録</span>
        <button class="btn-sm" style="background:var(--accent);color:#fff;border-color:var(--accent);"
          onclick="showRepairFormForProp('${id}')">＋ 修繕記録を追加</button>
      </div>
      ${repairsForProp.length === 0
        ? '<div style="color:var(--text-muted);font-size:13px;padding:8px 0;">修繕記録がありません</div>'
        : '<div style="overflow-x:auto;"><table class="data-table"><thead><tr><th>修繕日</th><th>季節</th><th>担当者</th><th>未対応タスク</th><th>承認</th><th></th></tr></thead><tbody>' + _rRows + '</tbody></table></div>'
      }
    </div>
  ` : '';

  el.innerHTML = `"""

text = replace_one(text, OLD_BUILT, NEW_BUILT, '5')

# ────────────────────────────────────────────────────────────
# STEP 6: Replace チェックリスト+実施記録 section with 訪問記録+修繕記録+実施記録
# ────────────────────────────────────────────────────────────
OLD_CHECKLIST_SECTION = """    <!-- チェックリスト ＋ 実施記録 -->
    <div class="two-col" style="margin-top:16px;">
      <div class="section">
        <div class="section-title" style="justify-content:space-between;">
          <span><span class="icon">✅</span>管理チェックリスト</span>
          <span style="font-size:11px;color:var(--text-muted);font-weight:400;">${state.detailYear}年度</span>
        </div>
        ${yearSwitcherHtml}
        ${checklistHtml || '<div style="font-size:12px;color:var(--text-muted);">項目がありません</div>'}
      </div>
      <div class="section">
        <div class="section-title" style="justify-content:space-between;">
          <span><span class="icon">📝</span>実施記録</span>
          <button class="btn-sm" onclick="openLogModal('${id}')">＋ 記録を追加</button>
        </div>
        ${logsHtml}
      </div>
    </div>
  `;"""

NEW_CHECKLIST_SECTION = """    ${visitsSection}

    ${repairsSection}

    <!-- 実施記録 -->
    <div class="section" style="margin-top:16px;">
      <div class="section-title" style="justify-content:space-between;">
        <span><span class="icon">📝</span>実施記録</span>
        <button class="btn-sm" onclick="openLogModal('${id}')">＋ 記録を追加</button>
      </div>
      ${logsHtml}
    </div>
  `;"""

text = replace_one(text, OLD_CHECKLIST_SECTION, NEW_CHECKLIST_SECTION, '6')

# ────────────────────────────────────────────────────────────
# STEP 7: showRepairLog - update state.view and call renderRepairList
# ────────────────────────────────────────────────────────────
OLD_SHOW_REPAIR = """async function showRepairLog() {
  state.view = 'repair-log';
  setActiveNav('nav-repair');
  await renderRepairLog();
}"""

NEW_SHOW_REPAIR = """async function showRepairLog() {
  state.view = 'repair';
  setActiveNav('nav-repair');
  await renderRepairList();
}"""

text = replace_one(text, OLD_SHOW_REPAIR, NEW_SHOW_REPAIR, '7')

# ────────────────────────────────────────────────────────────
# STEP 8: deleteRepair - call showRepairLog instead of renderRepairLog
# ────────────────────────────────────────────────────────────
OLD_DELETE_REPAIR = """async function deleteRepair(id) {
  if (!confirm('この修繕記録を削除しますか？')) return;
  const { error } = await db.from('repair_logs').delete().eq('id', id);
  if (error) { toast('削除失敗: ' + error.message, 'error'); return; }
  toast('削除しました', 'success');
  await renderRepairLog();
}"""

NEW_DELETE_REPAIR = """async function deleteRepair(id) {
  if (!confirm('この修繕記録を削除しますか？')) return;
  const { error } = await db.from('repair_logs').delete().eq('id', id);
  if (error) { toast('削除失敗: ' + error.message, 'error'); return; }
  toast('削除しました', 'success');
  await showRepairLog();
}"""

text = replace_one(text, OLD_DELETE_REPAIR, NEW_DELETE_REPAIR, '8')

# ────────────────────────────────────────────────────────────
# STEP 9: saveRepair (old modal) - update call from renderRepairLog→showRepairLog
# ────────────────────────────────────────────────────────────
OLD_SAVE_REPAIR_CALL = """  toast('保存しました', 'success');
  closeModal();
  await renderRepairLog();
}

async function deleteRepair"""

NEW_SAVE_REPAIR_CALL = """  toast('保存しました', 'success');
  closeModal();
  await showRepairLog();
}

async function deleteRepair"""

text = replace_one(text, OLD_SAVE_REPAIR_CALL, NEW_SAVE_REPAIR_CALL, '9')

# ────────────────────────────────────────────────────────────
# STEP 10: Append new functions before </script>
# ────────────────────────────────────────────────────────────
ANCHOR = '</script>\n</body>'
if ANCHOR not in text:
    ANCHOR = '</script>\r\n</body>'
    if ANCHOR not in text:
        errors.append('STEP 10: </script></body> anchor not found')

NEW_FUNCTIONS = """
// ════════════════════════════════════════════════════════════
// 物件管理台帳 ヘルパー：物件プリセット
// ════════════════════════════════════════════════════════════

function showVisitFormForProp(propId) {
  showLogs();
  setTimeout(() => showVisitForm(propId), 600);
}

function showRepairFormForProp(propId) {
  showRepairLog();
  setTimeout(() => showRepairForm(propId), 600);
}

// ════════════════════════════════════════════════════════════
// 修繕台帳 — 新実装（renderRepairList / showRepairDetail / showRepairForm）
// ════════════════════════════════════════════════════════════

async function renderRepairList() {
  const el = document.getElementById('content');
  el.innerHTML = '<div style="padding:40px;text-align:center;color:var(--text-muted);">読み込み中…</div>';

  const { data: repairs, error } = await db.from('repair_logs')
    .select('id, repair_date, visitor_name, season, admin_approved_at, property_id, properties(id, property_name, address, code, type)')
    .order('repair_date', { ascending: false });

  if (error) { toast('取得失敗: ' + error.message, 'error'); return; }
  const list = (repairs || []);

  let taskMap = {};
  if (list.length) {
    const { data: allTasks } = await db.from('repair_tasks')
      .select('repair_id, is_done')
      .in('repair_id', list.map(r => r.id));
    (allTasks || []).forEach(t => {
      if (!taskMap[t.repair_id]) taskMap[t.repair_id] = { total:0, done:0 };
      taskMap[t.repair_id].total++;
      if (t.is_done) taskMap[t.repair_id].done++;
    });
  }

  const rows = list.map(r => {
    const p  = r.properties;
    const pn = p ? (p.property_name || p.address || p.code || '（名称未入力）') : '—';
    const tm = taskMap[r.id] || { total:0, done:0 };
    const tb = tm.total === 0
      ? '<span style="color:var(--text-muted);font-size:11px;">なし</span>'
      : tm.done < tm.total
        ? '<span style="color:#c94040;font-size:11px;font-weight:600;">⚠️ ' + (tm.total - tm.done) + '件未対応</span>'
        : '<span style="color:#2e9e68;font-size:11px;">✅ 完了</span>';
    return `<tr onclick="showRepairDetail('${r.id}')" style="cursor:pointer;">
      <td>${esc(pn)}</td>
      <td>${r.repair_date || '—'}</td>
      <td>${r.season === 'winter' ? '❄️ 冬季' : '🌿 通常期'}</td>
      <td>${esc(r.visitor_name || '—')}</td>
      <td>${tb}</td>
      <td>${r.admin_approved_at ? '✅ 承認済' : '—'}</td>
      <td><button class="btn-sm" onclick="event.stopPropagation();showRepairDetail('${r.id}')">詳細</button></td>
    </tr>`;
  }).join('');

  el.innerHTML = `
    <div class="page-header">
      <div>
        <div class="page-title">🔧 修繕台帳</div>
        <div class="page-sub">全 ${list.length} 件</div>
      </div>
      <button class="btn-primary" onclick="showRepairForm()">＋ 修繕記録を追加</button>
    </div>

    ${list.length === 0
      ? '<div class="section" style="text-align:center;padding:40px;color:var(--text-muted);">修繕記録がありません</div>'
      : `<div class="section" style="padding:0;overflow:hidden;">
           <div style="overflow-x:auto;">
             <table class="data-table">
               <thead><tr>
                 <th>物件名</th><th>修繕日</th><th>季節</th><th>担当者</th>
                 <th>タスク</th><th>承認</th><th></th>
               </tr></thead>
               <tbody>${rows}</tbody>
             </table>
           </div>
         </div>`
    }
  `;
}

async function showRepairDetail(repairId) {
  const el = document.getElementById('content');
  el.innerHTML = '<div style="padding:40px;text-align:center;color:var(--text-muted);">読み込み中…</div>';

  const { data: r, error } = await db.from('repair_logs')
    .select('*, properties(id, property_name, address, code)')
    .eq('id', repairId)
    .single();
  if (error || !r) { toast('取得失敗', 'error'); return; }

  const { data: tasks } = await db.from('repair_tasks')
    .select('*')
    .eq('repair_id', repairId)
    .order('created_at');
  const taskList = tasks || [];

  const pName = r.properties
    ? (r.properties.property_name || r.properties.address || r.properties.code || '（名称未入力）')
    : '（物件未設定）';

  let photos = [];
  try { photos = JSON.parse(r.photo_urls || '[]'); } catch(e) {}

  const photoHtml = photos.length
    ? photos.map(u => `<img src="${esc(u)}" style="height:80px;border-radius:6px;cursor:pointer;object-fit:cover;" onclick="window.open('${esc(u)}','_blank')">`).join('')
    : '<span style="color:var(--text-muted);font-size:12px;">写真なし</span>';

  const taskHtml = taskList.length
    ? taskList.map(t => `
        <div class="log-row" style="align-items:flex-start;">
          <div style="flex:1;">
            <label style="display:flex;align-items:center;gap:8px;cursor:pointer;">
              <input type="checkbox" ${t.is_done ? 'checked' : ''}
                     onchange="toggleRepairTask('${t.id}','${repairId}',this.checked)"
                     style="width:16px;height:16px;">
              <span style="${t.is_done ? 'text-decoration:line-through;color:var(--text-muted);' : ''}">${esc(t.content)}</span>
            </label>
            ${t.done_at ? `<div style="font-size:11px;color:var(--text-muted);margin-left:24px;">完了: ${new Date(t.done_at).toLocaleDateString('ja-JP')}</div>` : ''}
          </div>
          <button class="btn-sm btn-danger" onclick="deleteRepairTask('${t.id}','${repairId}')">削除</button>
        </div>`).join('')
    : '<div style="font-size:12px;color:var(--text-muted);">タスクがありません</div>';

  el.innerHTML = `
    <div class="page-header">
      <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;">
        <button class="btn-back" onclick="showRepairLog()">← 一覧へ</button>
        <div>
          <div class="page-title">🔧 修繕記録詳細</div>
          <div style="font-size:13px;color:var(--text-muted);margin-top:4px;">${esc(pName)}</div>
        </div>
      </div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;">
        <button class="btn-secondary" onclick="showRepairForm('${repairId}')">✏️ 編集</button>
        <button class="btn-danger" onclick="deleteRepair('${repairId}')">🗑 削除</button>
      </div>
    </div>

    <div style="margin-top:10px;display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
      ${r.admin_approved_at
        ? `<span style="font-size:12px;background:#d4f0e3;color:#2e9e68;padding:4px 12px;border-radius:6px;font-weight:600;">✅ 管理者承認済　${new Date(r.admin_approved_at).toLocaleDateString('ja-JP')}</span>
           <button onclick="clearRepairApproval('${repairId}')" style="font-size:11px;background:none;border:1px solid #ccc;border-radius:4px;padding:3px 8px;cursor:pointer;color:var(--text-muted);">取消</button>`
        : `<button onclick="approveRepair('${repairId}')" style="font-size:13px;background:#d4f0e3;color:#2e9e68;border:1px solid #b8dfc8;border-radius:6px;padding:6px 16px;cursor:pointer;font-weight:600;">✅ 管理者承認する</button>`
      }
    </div>

    <div class="two-col" style="margin-top:16px;">
      <div class="section">
        <div class="section-title"><span class="icon">📋</span>基本情報</div>
        <table class="info-table">
          <tr><th>物件</th><td>${esc(pName)}</td></tr>
          <tr><th>修繕日</th><td>${r.repair_date || '—'}</td></tr>
          <tr><th>季節</th><td>${r.season === 'winter' ? '❄️ 冬季' : '🌿 通常期'}</td></tr>
          <tr><th>担当者</th><td>${esc(r.visitor_name || '—')}</td></tr>
          ${r.notes ? `<tr><th>備考</th><td style="white-space:pre-wrap;">${esc(r.notes)}</td></tr>` : ''}
        </table>
      </div>
      <div class="section">
        <div class="section-title"><span class="icon">📷</span>写真</div>
        <div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:8px;">${photoHtml}</div>
      </div>
    </div>

    <div class="section" style="margin-top:16px;">
      <div class="section-title" style="justify-content:space-between;">
        <span><span class="icon">✅</span>タスク</span>
        <button class="btn-sm" onclick="addRepairTask('${repairId}')">＋ タスクを追加</button>
      </div>
      <div id="repair-task-list">${taskHtml}</div>
    </div>
  `;
}

async function showRepairForm(repairId, presetPropId) {
  const el = document.getElementById('content');
  el.innerHTML = '<div style="padding:40px;text-align:center;color:var(--text-muted);">読み込み中…</div>';

  const { data: props } = await db.from('properties')
    .select('id, property_name, address, code, type')
    .eq('type', 'house')
    .order('created_at', { ascending: false });
  const propList = props || [];

  let d = {};
  if (repairId) {
    const { data } = await db.from('repair_logs').select('*').eq('id', repairId).single();
    d = data || {};
  }

  const propOpts = propList.map(p =>
    `<option value="${p.id}" ${(presetPropId === p.id || d.property_id === p.id) ? 'selected' : ''}>
      ${esc(p.property_name || p.address || p.code || '（名称未入力）')}
    </option>`
  ).join('');

  el.innerHTML = `
    <div class="page-header">
      <div style="display:flex;align-items:center;gap:14px;">
        <button class="btn-back" onclick="${repairId ? "showRepairDetail('" + repairId + "')" : 'showRepairLog()'}">← 戻る</button>
        <div class="page-title">🔧 ${repairId ? '修繕記録を編集' : '修繕記録を追加'}</div>
      </div>
    </div>

    <div class="section" style="margin-top:16px;">
      <input type="hidden" id="rf-id" value="${repairId || ''}">

      <div class="form-row">
        <div class="form-group" style="grid-column:span 2;">
          <label>物件 *（建物のみ）</label>
          <select id="rf-prop">${propOpts}</select>
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label>修繕日 *</label>
          <input type="date" id="rf-date" value="${d.repair_date || new Date().toISOString().slice(0,10)}">
        </div>
        <div class="form-group">
          <label>季節</label>
          <select id="rf-season">
            <option value="normal" ${d.season !== 'winter' ? 'selected' : ''}>🌿 通常期</option>
            <option value="winter" ${d.season === 'winter' ? 'selected' : ''}>❄️ 冬季</option>
          </select>
        </div>
      </div>

      <div class="form-row">
        <div class="form-group" style="grid-column:span 2;">
          <label>担当者</label>
          <input type="text" id="rf-visitor" placeholder="担当者名" value="${esc(d.visitor_name || '')}">
        </div>
      </div>

      <div class="form-row">
        <div class="form-group" style="grid-column:span 2;">
          <label>備考</label>
          <textarea id="rf-notes" rows="4" placeholder="修繕内容・特記事項など">${esc(d.notes || '')}</textarea>
        </div>
      </div>

      <div style="display:flex;gap:8px;margin-top:16px;">
        <button class="btn-primary" onclick="saveRepairForm()">💾 保存</button>
        <button class="btn-secondary" onclick="${repairId ? "showRepairDetail('" + repairId + "')" : 'showRepairLog()'}">キャンセル</button>
      </div>
    </div>
  `;
}

async function saveRepairForm() {
  const repairId   = document.getElementById('rf-id')?.value || null;
  const property_id = document.getElementById('rf-prop')?.value || null;
  const repair_date = document.getElementById('rf-date')?.value || null;
  const season      = document.getElementById('rf-season')?.value || 'normal';
  const visitor_name = document.getElementById('rf-visitor')?.value.trim() || null;
  const notes       = document.getElementById('rf-notes')?.value.trim() || null;

  if (!property_id) { toast('物件を選択してください', 'error'); return; }
  if (!repair_date)  { toast('修繕日を入力してください', 'error'); return; }

  const data = { property_id, repair_date, season, visitor_name, notes, updated_at: new Date().toISOString() };

  let err;
  if (repairId) {
    ({ error: err } = await db.from('repair_logs').update(data).eq('id', repairId));
  } else {
    ({ error: err } = await db.from('repair_logs').insert(data));
  }
  if (err) { toast('保存失敗: ' + err.message, 'error'); return; }
  toast('保存しました', 'success');
  if (repairId) { await showRepairDetail(repairId); } else { await showRepairLog(); }
}

async function addRepairTask(repairId) {
  const content = prompt('タスク内容を入力してください');
  if (!content?.trim()) return;
  const { error } = await db.from('repair_tasks').insert({ repair_id: repairId, content: content.trim() });
  if (error) { toast('追加失敗: ' + error.message, 'error'); return; }
  toast('タスクを追加しました', 'success');
  await showRepairDetail(repairId);
}

async function toggleRepairTask(taskId, repairId, isDone) {
  const data = isDone
    ? { is_done: true,  done_at: new Date().toISOString() }
    : { is_done: false, done_at: null };
  const { error } = await db.from('repair_tasks').update(data).eq('id', taskId);
  if (error) { toast('更新失敗: ' + error.message, 'error'); return; }
  await showRepairDetail(repairId);
}

async function deleteRepairTask(taskId, repairId) {
  if (!confirm('このタスクを削除しますか？')) return;
  const { error } = await db.from('repair_tasks').delete().eq('id', taskId);
  if (error) { toast('削除失敗: ' + error.message, 'error'); return; }
  toast('削除しました', 'success');
  await showRepairDetail(repairId);
}

async function approveRepair(repairId) {
  const { error } = await db.from('repair_logs')
    .update({ admin_approved_at: new Date().toISOString() })
    .eq('id', repairId);
  if (error) { toast('承認失敗: ' + error.message, 'error'); return; }
  toast('承認しました', 'success');
  await showRepairDetail(repairId);
}

async function clearRepairApproval(repairId) {
  if (!confirm('承認を取り消しますか？')) return;
  const { error } = await db.from('repair_logs')
    .update({ admin_approved_at: null })
    .eq('id', repairId);
  if (error) { toast('取消失敗: ' + error.message, 'error'); return; }
  toast('承認を取り消しました', 'success');
  await showRepairDetail(repairId);
}

"""

if ANCHOR in text:
    text = text.replace(ANCHOR, NEW_FUNCTIONS + ANCHOR, 1)
else:
    errors.append('STEP 10: replacement failed (anchor missing)')

# ────────────────────────────────────────────────────────────
# Write back
# ────────────────────────────────────────────────────────────
output = text.replace('\n', '\r\n')
with open(SRC, 'wb') as f:
    f.write(output.encode('utf-8'))

if errors:
    print('=== ERRORS ===')
    for e in errors:
        print(' ', e)
    sys.exit(1)
else:
    print('patch_v28: all 10 steps OK')
    print(f'Written: {SRC}')
