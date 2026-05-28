// ════════════════════════════════════════════════════════════
// 賃貸管理システム v1
// ════════════════════════════════════════════════════════════

// ── 定数・ヘルパー ──
const RENTAL_DOC_OPTIONS = ['登記','公図','案内図','上水道配管図','下水道配管図','地積測量図','道路台帳写し','固定資産税課税明細'];

const rentalTypeLabel   = t => ({land:'土地', house:'住宅', building:'ビル'}[t] || t || '—');
const rentalStatusLabel = s => ({recruiting:'募集中', occupied:'入居中', vacant:'空室', leaving:'退去予定', closed:'管理終了'}[s] || s || '—');
const rentalTransLabel  = t => ({managed:'管理', broker:'仲介'}[t] || '—');

function rentalStatusBadge(s) {
  const map = {
    recruiting: '<span class="badge-recruiting">募集中</span>',
    occupied:   '<span class="badge-occupied">入居中</span>',
    vacant:     '<span class="badge-vacant">空室</span>',
    leaving:    '<span class="badge-leaving">退去予定</span>',
    closed:     '<span class="badge-r-closed">管理終了</span>',
  };
  return map[s] || `<span>${esc(s||'')}</span>`;
}

function rentalTypeBadge(t) {
  const map = {
    land:     '<span class="badge-land">土地</span>',
    house:    '<span class="badge-house">住宅</span>',
    building: '<span class="badge-building">ビル</span>',
  };
  return map[t] || '';
}

function calcBuildingAge(year, month) {
  if (!year) return '';
  const now = new Date();
  let age = now.getFullYear() - parseInt(year);
  if (parseInt(month || 1) > now.getMonth() + 1) age--;
  return age >= 0 ? `築${age}年` : '';
}

function parseFloatOrNull(v) {
  if (v === '' || v == null) return null;
  const n = parseFloat(v);
  return isNaN(n) ? null : n;
}

function parseIntOrNull(v) {
  if (v === '' || v == null) return null;
  const n = parseInt(v);
  return isNaN(n) ? null : n;
}

// ════════════════════════════════════════════════════════════
// ナビゲーション
// ════════════════════════════════════════════════════════════

async function showRentalList() {
  state.view = 'rental-list';
  if (!state.rentalFilterType) state.rentalFilterType = 'all';
  setActiveNav('nav-rental');
  await renderRentalList();
}

async function showRentalDetail(id) {
  state.view     = 'rental-detail';
  state.rentalId = id;
  setActiveNav('');
  await renderRentalDetail(id);
}

async function showRentalForm(id) {
  state.view     = 'rental-form';
  state.rentalId = id || null;
  setActiveNav('');
  await renderRentalForm(id);
}

async function showRentalCost(rentalId) {
  if (!sessionStorage.getItem('costAuth')) {
    const pw = prompt('パスワードを入力してください');
    if (pw !== 'ajiro2775') { toast('パスワードが違います', 'error'); return; }
    sessionStorage.setItem('costAuth', '1');
  }
  state.view     = 'rental-cost';
  state.rentalId = rentalId;
  setActiveNav('');
  await renderRentalCost(rentalId);
}

async function showRepairLog() {
  state.view = 'repair-log';
  setActiveNav('nav-repair');
  await renderRepairLog();
}

// ════════════════════════════════════════════════════════════
// 賃貸物件一覧
// ════════════════════════════════════════════════════════════

async function renderRentalList() {
  const el = document.getElementById('content');
  el.innerHTML = '<div style="padding:40px;text-align:center;color:var(--text-muted);">読み込み中…</div>';

  const { data, error } = await db
    .from('rental_properties')
    .select('*, rental_details(*)')
    .order('created_at', { ascending: false });
  if (error) { toast('データ取得失敗: ' + error.message, 'error'); return; }

  const all       = data || [];
  const lands     = all.filter(p => p.type === 'land');
  const houses    = all.filter(p => p.type === 'house');
  const buildings = all.filter(p => p.type === 'building');

  const ft = state.rentalFilterType;
  const displayed = ft === 'land' ? lands : ft === 'house' ? houses : ft === 'building' ? buildings : all;

  const fmtRent = p => {
    const d = Array.isArray(p.rental_details) ? p.rental_details[0] : p.rental_details;
    if (!d?.rent) return '—';
    return Number(d.rent).toLocaleString('ja-JP') + '円';
  };

  const rows = displayed.map(p => `
    <tr onclick="showRentalDetail('${p.id}')" style="cursor:pointer;">
      <td>${esc(p.code || '')}</td>
      <td style="max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;"
          title="${esc(p.property_name || p.address || '')}">
        ${esc(p.property_name || p.address || '（名称未入力）')}
      </td>
      <td>${rentalTypeBadge(p.type)}</td>
      <td>${rentalStatusBadge(p.status)}</td>
      <td style="white-space:nowrap;">${fmtRent(p)}</td>
      <td style="font-size:12px;">${rentalTransLabel(p.transaction_type)}</td>
      <td style="max-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
        ${esc(p.address || '—')}
      </td>
      <td onclick="event.stopPropagation()">
        <button class="btn-sm" onclick="showRentalDetail('${p.id}')">詳細</button>
      </td>
    </tr>`).join('');

  el.innerHTML = `
    <div class="page-header">
      <div>
        <div class="page-title">🏢 賃貸物件一覧</div>
        <div class="page-sub">土地 ${lands.length}件 ／ 住宅 ${houses.length}件 ／ ビル ${buildings.length}件</div>
      </div>
      <button class="btn-primary" onclick="showRentalForm()">＋ 物件を追加</button>
    </div>

    <div class="filter-tabs">
      <button class="filter-tab ${ft==='all'     ?'active':''}" onclick="setRentalFilter('all')">全て（${all.length}）</button>
      <button class="filter-tab ${ft==='land'    ?'active':''}" onclick="setRentalFilter('land')">🌐 土地（${lands.length}）</button>
      <button class="filter-tab ${ft==='house'   ?'active':''}" onclick="setRentalFilter('house')">🏡 住宅（${houses.length}）</button>
      <button class="filter-tab ${ft==='building'?'active':''}" onclick="setRentalFilter('building')">🏢 ビル（${buildings.length}）</button>
    </div>

    ${displayed.length === 0
      ? `<div class="section" style="text-align:center;padding:40px;color:var(--text-muted);">
           該当する物件がありません。
         </div>`
      : `<div class="section" style="padding:0;overflow:hidden;">
           <div style="overflow-x:auto;">
             <table class="data-table">
               <thead><tr>
                 <th>コード</th><th>物件名</th><th>種別</th><th>状態</th>
                 <th>賃料</th><th>取引形態</th><th>住所</th><th></th>
               </tr></thead>
               <tbody>${rows}</tbody>
             </table>
           </div>
         </div>`
    }
  `;
}

function setRentalFilter(type) {
  state.rentalFilterType = type;
  renderRentalList();
}

// ════════════════════════════════════════════════════════════
// 賃貸物件詳細
// ════════════════════════════════════════════════════════════

async function renderRentalDetail(id) {
  const el = document.getElementById('content');
  el.innerHTML = '<div style="padding:40px;text-align:center;color:var(--text-muted);">読み込み中…</div>';

  const [propRes, detRes, tenantRes, histRes, unitsRes] = await Promise.all([
    db.from('rental_properties').select('*').eq('id', id).single(),
    db.from('rental_details').select('*').eq('rental_id', id).maybeSingle(),
    db.from('rental_tenants').select('*').eq('rental_id', id).maybeSingle(),
    db.from('rental_tenant_history').select('*').eq('rental_id', id).order('contract_end', { ascending: false }),
    db.from('rental_units').select('*').eq('rental_id', id).order('unit_number'),
  ]);

  if (propRes.error) { toast('物件取得失敗: ' + propRes.error.message, 'error'); return; }
  const prop    = propRes.data;
  const det     = detRes.data  || {};
  const tenant  = tenantRes.data || null;
  const history = histRes.data  || [];
  const units   = unitsRes.data || [];

  const isBuilding = prop.type === 'building';
  const isLand     = prop.type === 'land';

  const docsArr = (() => { try { return JSON.parse(det.docs || '[]'); } catch(e) { return []; } })();
  const fmtYen  = v => v != null ? Number(v).toLocaleString('ja-JP') + ' 円' : '—';
  const builtAge = det.built_year
    ? `${det.built_year}年${det.built_month ? det.built_month + '月' : ''} / ${toWareki(det.built_year, det.built_month)} / ${calcBuildingAge(det.built_year, det.built_month)}`
    : '—';

  // ── 入居者セクション ──
  const tenantSection = !isBuilding ? `
    <div class="section" style="margin-bottom:16px;">
      <div class="section-title" style="display:flex;justify-content:space-between;align-items:center;">
        <span><span class="icon">👤</span>入居者情報</span>
        <div style="display:flex;gap:6px;">
          <button class="btn-sm" onclick="openEditTenantModal('${id}')">
            ${tenant ? '✏️ 編集' : '＋ 入居者登録'}
          </button>
          ${tenant ? `<button class="btn-sm btn-danger" onclick="openMoveOutModal('${id}')">退去処理</button>` : ''}
        </div>
      </div>
      ${tenant ? `
        <table class="info-table">
          <tr><th>氏名</th><td>${esc(tenant.tenant_name || '—')}</td></tr>
          <tr><th>会社名</th><td>${esc(tenant.company_name || '—')}</td></tr>
          <tr><th>電話番号</th><td>${esc(tenant.phone || '—')}</td></tr>
          <tr><th>緊急連絡先</th><td>${esc(tenant.emergency_phone || '—')}</td></tr>
          <tr><th>保証人</th><td>${esc(tenant.guarantor_name || '—')}${tenant.guarantor_phone ? '　' + esc(tenant.guarantor_phone) : ''}</td></tr>
          <tr><th>契約期間</th><td>${tenant.contract_start || '—'} ～ ${tenant.contract_end || '—'}</td></tr>
          <tr><th>火災保険</th><td>${esc(tenant.insurance_status || '—')}${tenant.insurance_company ? '　' + esc(tenant.insurance_company) : ''}${tenant.insurance_expiry ? '（満期: ' + tenant.insurance_expiry + '）' : ''}</td></tr>
          <tr><th>鍵</th><td>${tenant.key_count != null ? tenant.key_count + '本' : '—'}${tenant.key_location ? '　保管場所: ' + esc(tenant.key_location) : ''}</td></tr>
          ${tenant.notes ? `<tr><th>備考</th><td style="white-space:pre-wrap;">${esc(tenant.notes)}</td></tr>` : ''}
        </table>
      ` : '<div style="padding:20px;text-align:center;color:var(--text-muted);">入居者情報が登録されていません</div>'}
    </div>
  ` : '';

  // ── 区画管理セクション ──
  const unitsSection = isBuilding ? `
    <div class="section" style="margin-bottom:16px;">
      <div class="section-title" style="display:flex;justify-content:space-between;align-items:center;">
        <span><span class="icon">🏗</span>区画管理</span>
        <button class="btn-sm" onclick="openUnitModal('${id}')">＋ 区画追加</button>
      </div>
      ${units.length === 0
        ? '<div style="padding:20px;text-align:center;color:var(--text-muted);">区画が登録されていません</div>'
        : `<div style="overflow-x:auto;">
             <table class="data-table">
               <thead><tr>
                 <th>区画番号</th><th>階</th><th>用途</th><th>面積(㎡)</th>
                 <th>賃料</th><th>テナント</th><th>契約期間</th><th>状態</th><th></th>
               </tr></thead>
               <tbody>
                 ${units.map(u => `
                   <tr>
                     <td>${esc(u.unit_number || '—')}</td>
                     <td>${esc(u.floor || '—')}</td>
                     <td>${esc(u.usage || '—')}</td>
                     <td>${u.area_sqm != null ? u.area_sqm : '—'}</td>
                     <td style="white-space:nowrap;">${u.rent != null ? Number(u.rent).toLocaleString('ja-JP') + '円' : '—'}</td>
                     <td>${esc(u.tenant_name || '—')}</td>
                     <td style="font-size:11px;white-space:nowrap;">${u.contract_start || '—'} ～ ${u.contract_end || '—'}</td>
                     <td>${rentalStatusBadge(u.unit_status)}</td>
                     <td>
                       <button class="btn-sm" onclick="openUnitModal('${id}','${u.id}')">編集</button>
                       <button class="btn-sm btn-danger" onclick="deleteUnit('${u.id}','${id}')">削除</button>
                     </td>
                   </tr>`).join('')}
               </tbody>
             </table>
           </div>`
      }
    </div>
  ` : '';

  // ── 入居履歴セクション ──
  const historySection = `
    <div class="section" style="margin-bottom:16px;">
      <div class="section-title"><span class="icon">📜</span>入居履歴</div>
      ${history.length === 0
        ? '<div style="padding:20px;text-align:center;color:var(--text-muted);">履歴がありません</div>'
        : `<div style="overflow-x:auto;">
             <table class="data-table">
               <thead><tr>
                 <th>氏名 / 会社名</th><th>契約開始</th><th>契約終了</th><th>退去事由</th><th>賃料</th>
               </tr></thead>
               <tbody>
                 ${history.map(h => `
                   <tr>
                     <td>${esc(h.tenant_name || '')}${h.company_name ? '<br><small style="color:var(--text-muted);">' + esc(h.company_name) + '</small>' : ''}</td>
                     <td>${h.contract_start || '—'}</td>
                     <td>${h.contract_end   || '—'}</td>
                     <td>${esc(h.move_out_reason || '—')}</td>
                     <td style="white-space:nowrap;">${h.rent != null ? Number(h.rent).toLocaleString('ja-JP') + '円' : '—'}</td>
                   </tr>`).join('')}
               </tbody>
             </table>
           </div>`
      }
    </div>
  `;

  el.innerHTML = `
    <div class="page-header">
      <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;">
        <button class="btn-back" onclick="showRentalList()">← 一覧へ</button>
        <div>
          <div class="page-title">🏢 ${esc(prop.property_name || prop.address || prop.code || '（名称未入力）')}</div>
          <div style="display:flex;gap:6px;margin-top:4px;flex-wrap:wrap;align-items:center;">
            ${rentalStatusBadge(prop.status)}
            ${rentalTypeBadge(prop.type)}
            ${prop.transaction_type === 'managed' ? '<span class="badge-managed">管理</span>' : ''}
            ${prop.transaction_type === 'broker'  ? '<span class="badge-broker">仲介</span>'  : ''}
            ${det.suumo_listed ? '<span class="badge-suumo">SUUMO</span>' : ''}
            ${det.hp_listed    ? '<span class="badge-hp">🌐 HP</span>'   : ''}
          </div>
        </div>
      </div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;">
        <button class="btn-secondary" onclick="showRentalCost('${id}')">📊 原価管理</button>
        <button class="btn-secondary" onclick="openRepairModal('${id}')">🔧 修繕追加</button>
        <button class="btn-primary"   onclick="showRentalForm('${id}')">✏️ 編集</button>
        <button class="btn-danger"    onclick="deleteRentalProperty('${id}')">🗑 削除</button>
      </div>
    </div>

    <div class="two-col" style="margin-bottom:16px;">
      <div class="section">
        <div class="section-title"><span class="icon">📋</span>基本情報</div>
        <table class="info-table">
          ${prop.property_name ? `<tr><th>物件名</th><td>${esc(prop.property_name)}</td></tr>` : ''}
          <tr><th>コード</th><td>${esc(prop.code || '—')}</td></tr>
          <tr><th>種別</th><td>${rentalTypeLabel(prop.type)}</td></tr>
          <tr><th>状態</th><td>${rentalStatusLabel(prop.status)}</td></tr>
          <tr><th>取引形態</th><td>${rentalTransLabel(prop.transaction_type)}</td></tr>
          <tr><th>住所</th><td>${esc(prop.address || '—')}${prop.map_url ? ` <a class="map-link" href="${esc(prop.map_url)}" target="_blank">📍 地図</a>` : ''}</td></tr>
          ${prop.notes ? `<tr><th>備考</th><td style="white-space:pre-wrap;">${esc(prop.notes)}</td></tr>` : ''}
        </table>
      </div>

      <div class="section">
        <div class="section-title"><span class="icon">📐</span>物件概要</div>
        <table class="info-table">
          <tr><th>土地面積(㎡)</th><td>${det.land_area_sqm ?? '—'}</td></tr>
          <tr><th>用途地域</th><td>${esc(det.zoning || '—')}</td></tr>
          <tr><th>他の法令</th><td>${esc(det.other_laws || '—')}</td></tr>
          <tr><th>上水道</th><td>${esc(det.water_supply || '—')}</td></tr>
          <tr><th>下水道</th><td>${esc(det.sewage || '—')}</td></tr>
          <tr><th>権利</th><td>${esc(det.rights || '—')}</td></tr>
          <tr><th>情報公開日</th><td>${det.publish_date || '—'}</td></tr>
          <tr><th>SUUMO掲載</th><td>${det.suumo_listed ? '✅ 掲載中' : '非掲載'}</td></tr>
          <tr><th>HP掲載</th><td>${det.hp_listed ? '✅ 掲載中' : '非掲載'}</td></tr>
          <tr><th>取得書類</th><td>${docsArr.length ? docsArr.join('、') : '—'}</td></tr>
        </table>
      </div>
    </div>

    ${!isLand ? `
    <div class="two-col" style="margin-bottom:16px;">
      <div class="section">
        <div class="section-title"><span class="icon">🏗</span>建物情報</div>
        <table class="info-table">
          <tr><th>建物面積(㎡)</th><td>${det.building_area_sqm ?? '—'}</td></tr>
          <tr><th>築年月</th><td>${builtAge}</td></tr>
          <tr><th>構造</th><td>${esc(det.structure || '—')}</td></tr>
          <tr><th>間取</th><td>${esc(det.layout || '—')}</td></tr>
          <tr><th>階数</th><td>${esc(det.floors || '—')}</td></tr>
          <tr><th>リフォーム歴</th><td style="white-space:pre-wrap;">${esc(det.renovation_history || '—')}</td></tr>
        </table>
      </div>
      <div class="section">
        <div class="section-title"><span class="icon">🔑</span>賃貸条件</div>
        <table class="info-table">
          <tr><th>月額賃料</th><td>${fmtYen(det.rent)}</td></tr>
          <tr><th>管理費</th><td>${fmtYen(det.management_fee)}</td></tr>
          <tr><th>共益費</th><td>${fmtYen(det.common_fee)}</td></tr>
          <tr><th>敷金</th><td>${det.deposit_months != null ? det.deposit_months + 'ヶ月' : '—'}</td></tr>
          <tr><th>礼金</th><td>${det.key_money_months != null ? det.key_money_months + 'ヶ月' : '—'}</td></tr>
          <tr><th>契約種別</th><td>${esc(det.contract_type || '—')}</td></tr>
          <tr><th>契約期間</th><td>${esc(det.contract_period || '—')}</td></tr>
          <tr><th>更新料</th><td>${esc(det.renewal_fee || '—')}</td></tr>
          <tr><th>駐車場</th><td>${det.parking_available
            ? `あり${det.parking_count ? ' (' + det.parking_count + '台)' : ''}${det.parking_fee ? ' / ' + Number(det.parking_fee).toLocaleString('ja-JP') + '円/月' : ''}`
            : 'なし'}</td></tr>
        </table>
      </div>
    </div>
    ` : ''}

    ${tenantSection}
    ${unitsSection}
    ${historySection}
  `;

  window._repairProps = null;
}

// ════════════════════════════════════════════════════════════
// 賃貸物件フォーム（新規・編集）
// ════════════════════════════════════════════════════════════

async function renderRentalForm(id) {
  const el = document.getElementById('content');
  el.innerHTML = '<div style="padding:40px;text-align:center;color:var(--text-muted);">読み込み中…</div>';

  let prop = {}, det = {};
  if (id) {
    const [pr, dr] = await Promise.all([
      db.from('rental_properties').select('*').eq('id', id).single(),
      db.from('rental_details').select('*').eq('rental_id', id).maybeSingle(),
    ]);
    if (pr.error) { toast('取得失敗: ' + pr.error.message, 'error'); return; }
    prop = pr.data || {};
    det  = dr.data || {};
  }

  const savedDocs = (() => { try { return JSON.parse(det.docs || '[]'); } catch(e) { return []; } })();
  const docChecks = RENTAL_DOC_OPTIONS.map(d =>
    `<label class="doc-check-label${savedDocs.includes(d) ? ' checked' : ''}">
      <input type="checkbox" name="f-rdoc" value="${esc(d)}" ${savedDocs.includes(d) ? 'checked' : ''}
             onchange="this.closest('.doc-check-label').classList.toggle('checked',this.checked)">
      ${esc(d)}
    </label>`).join('');

  const typeOpts  = [['land','土地'],['house','住宅'],['building','ビル']];
  const statOpts  = [['recruiting','募集中'],['occupied','入居中'],['vacant','空室'],['leaving','退去予定'],['closed','管理終了']];
  const transOpts = [['','（未選択）'],['managed','管理'],['broker','仲介']];
  const selR = (id, val, opts) =>
    `<select id="${id}" class="qs-control">${opts.map(([v,l]) =>
      `<option value="${v}" ${val===v?'selected':''}>${l}</option>`).join('')}</select>`;

  const curType = prop.type || 'house';

  el.innerHTML = `
    <div class="page-header">
      <div style="display:flex;align-items:center;gap:14px;">
        <button class="btn-back" onclick="${id ? `showRentalDetail('${id}')` : 'showRentalList()'}">← 戻る</button>
        <div class="page-title">${id ? '🏢 賃貸物件を編集' : '🏢 賃貸物件を新規登録'}</div>
      </div>
      <button class="btn-primary" onclick="saveRentalProperty()">💾 保存</button>
    </div>

    <input type="hidden" id="rf-id" value="${esc(id || '')}">

    <div class="two-col" style="margin-bottom:16px;">
      <div class="section">
        <div class="section-title">基本情報</div>
        <div class="form-section">管理情報</div>
        <div class="form-row">
          <div class="form-group" style="grid-column:span 2;">
            <label>物件名</label>
            <input type="text" id="rf-name" class="qs-control" value="${esc(prop.property_name || '')}">
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>コード</label>
            <input type="text" id="rf-code" class="qs-control" value="${esc(prop.code || '')}">
          </div>
          <div class="form-group">
            <label>種別 *</label>
            ${selR('rf-type', curType, typeOpts)}
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>状態 *</label>
            ${selR('rf-status', prop.status || 'vacant', statOpts)}
          </div>
          <div class="form-group">
            <label>取引形態</label>
            ${selR('rf-trans', prop.transaction_type || '', transOpts)}
          </div>
        </div>
        <div class="form-section">所在地</div>
        <div class="form-row">
          <div class="form-group" style="grid-column:span 2;">
            <label>住所</label>
            <input type="text" id="rf-address" class="qs-control" value="${esc(prop.address || '')}">
          </div>
        </div>
        <div class="form-row">
          <div class="form-group" style="grid-column:span 2;">
            <label>地図URL</label>
            <input type="text" id="rf-mapurl" class="qs-control" value="${esc(prop.map_url || '')}">
          </div>
        </div>
        <div class="form-row">
          <div class="form-group" style="grid-column:span 2;">
            <label>備考</label>
            <textarea id="rf-notes" class="qs-control" rows="3">${esc(prop.notes || '')}</textarea>
          </div>
        </div>
      </div>

      <div class="section">
        <div class="section-title">物件概要</div>
        <div class="form-section">土地・掲載情報</div>
        <div class="form-row">
          <div class="form-group">
            <label>土地面積(㎡)</label>
            <input type="number" id="rf-land-area" class="qs-control" step="0.01" value="${det.land_area_sqm ?? ''}">
          </div>
          <div class="form-group">
            <label>用途地域</label>
            <input type="text" id="rf-zoning" class="qs-control" value="${esc(det.zoning || '')}">
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>他の法令</label>
            <input type="text" id="rf-other-laws" class="qs-control" value="${esc(det.other_laws || '')}">
          </div>
          <div class="form-group">
            <label>権利</label>
            <input type="text" id="rf-rights" class="qs-control" value="${esc(det.rights || '')}">
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>上水道</label>
            <input type="text" id="rf-water" class="qs-control" value="${esc(det.water_supply || '')}">
          </div>
          <div class="form-group">
            <label>下水道</label>
            <input type="text" id="rf-sewage" class="qs-control" value="${esc(det.sewage || '')}">
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>情報公開日</label>
            <input type="date" id="rf-publish" class="qs-control" value="${det.publish_date || ''}">
          </div>
          <div class="form-group" style="justify-content:flex-end;padding-top:14px;gap:6px;flex-direction:row;flex-wrap:wrap;">
            <label class="doc-check-label${det.suumo_listed ? ' checked' : ''}" style="white-space:nowrap;">
              <input id="rf-suumo" type="checkbox" ${det.suumo_listed ? 'checked' : ''}
                     onchange="this.closest('.doc-check-label').classList.toggle('checked',this.checked)">
              SUUMO掲載
            </label>
            <label class="doc-check-label${det.hp_listed ? ' checked' : ''}" style="white-space:nowrap;">
              <input id="rf-hp" type="checkbox" ${det.hp_listed ? 'checked' : ''}
                     onchange="this.closest('.doc-check-label').classList.toggle('checked',this.checked)">
              HP掲載
            </label>
          </div>
        </div>
        <div class="form-section">取得書類</div>
        <div class="doc-checkboxes">${docChecks}</div>
      </div>
    </div>

    <div id="rf-building-section" style="${curType === 'land' ? 'display:none' : ''}">
      <div class="two-col" style="margin-bottom:16px;">
        <div class="section">
          <div class="section-title">建物情報</div>
          <div class="form-row">
            <div class="form-group">
              <label>建物面積(㎡)</label>
              <input type="number" id="rf-bld-area" class="qs-control" step="0.01" value="${det.building_area_sqm ?? ''}">
            </div>
            <div class="form-group">
              <label>構造</label>
              <input type="text" id="rf-structure" class="qs-control" value="${esc(det.structure || '')}">
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>築年</label>
              <input type="number" id="rf-built-yr" class="qs-control" min="1900" max="2099" value="${det.built_year || ''}">
            </div>
            <div class="form-group">
              <label>築月</label>
              <input type="number" id="rf-built-mo" class="qs-control" min="1" max="12" value="${det.built_month || ''}">
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>間取</label>
              <input type="text" id="rf-layout" class="qs-control" value="${esc(det.layout || '')}">
            </div>
            <div class="form-group">
              <label>階数</label>
              <input type="text" id="rf-floors" class="qs-control" value="${esc(det.floors || '')}">
            </div>
          </div>
          <div class="form-row">
            <div class="form-group" style="grid-column:span 2;">
              <label>リフォーム・改修歴</label>
              <textarea id="rf-renovation" class="qs-control" rows="3">${esc(det.renovation_history || '')}</textarea>
            </div>
          </div>
        </div>

        <div class="section">
          <div class="section-title">賃貸条件</div>
          <div class="form-row">
            <div class="form-group">
              <label>月額賃料（円）</label>
              <input type="number" id="rf-rent" class="qs-control" step="1" value="${det.rent ?? ''}">
            </div>
            <div class="form-group">
              <label>管理費（円）</label>
              <input type="number" id="rf-mgmt-fee" class="qs-control" step="1" value="${det.management_fee ?? ''}">
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>共益費（円）</label>
              <input type="number" id="rf-common-fee" class="qs-control" step="1" value="${det.common_fee ?? ''}">
            </div>
            <div class="form-group">
              <label>敷金（ヶ月）</label>
              <input type="number" id="rf-deposit" class="qs-control" step="0.5" value="${det.deposit_months ?? ''}">
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>礼金（ヶ月）</label>
              <input type="number" id="rf-keymoney" class="qs-control" step="0.5" value="${det.key_money_months ?? ''}">
            </div>
            <div class="form-group">
              <label>契約種別</label>
              <input type="text" id="rf-contract-type" class="qs-control" placeholder="普通賃貸・定期借家" value="${esc(det.contract_type || '')}">
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>契約期間</label>
              <input type="text" id="rf-contract-period" class="qs-control" value="${esc(det.contract_period || '')}">
            </div>
            <div class="form-group">
              <label>更新料</label>
              <input type="text" id="rf-renewal" class="qs-control" value="${esc(det.renewal_fee || '')}">
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>駐車場</label>
              <select id="rf-parking" class="qs-control">
                <option value="false" ${!det.parking_available ? 'selected' : ''}>なし</option>
                <option value="true"  ${det.parking_available  ? 'selected' : ''}>あり</option>
              </select>
            </div>
            <div class="form-group">
              <label>駐車台数</label>
              <input type="number" id="rf-parking-cnt" class="qs-control" min="0" value="${det.parking_count ?? ''}">
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>駐車場代（円/月）</label>
              <input type="number" id="rf-parking-fee" class="qs-control" step="1" value="${det.parking_fee ?? ''}">
            </div>
          </div>
        </div>
      </div>
    </div>

    <div style="text-align:right;margin-bottom:40px;">
      <button class="btn-primary" onclick="saveRentalProperty()" style="min-width:120px;">💾 保存</button>
    </div>
  `;

  document.getElementById('rf-type').addEventListener('change', () => {
    const t = document.getElementById('rf-type').value;
    document.getElementById('rf-building-section').style.display = t === 'land' ? 'none' : '';
  });
}

async function saveRentalProperty() {
  const id = document.getElementById('rf-id')?.value || null;

  const propData = {
    property_name:    document.getElementById('rf-name')?.value.trim()    || null,
    code:             document.getElementById('rf-code')?.value.trim()     || null,
    type:             document.getElementById('rf-type')?.value,
    status:           document.getElementById('rf-status')?.value,
    transaction_type: document.getElementById('rf-trans')?.value           || null,
    address:          document.getElementById('rf-address')?.value.trim()  || null,
    map_url:          document.getElementById('rf-mapurl')?.value.trim()   || null,
    notes:            document.getElementById('rf-notes')?.value.trim()    || null,
  };

  const selectedDocs = [...document.querySelectorAll('input[name="f-rdoc"]:checked')].map(c => c.value);

  const detData = {
    land_area_sqm:      parseFloatOrNull(document.getElementById('rf-land-area')?.value),
    zoning:             document.getElementById('rf-zoning')?.value.trim()        || null,
    other_laws:         document.getElementById('rf-other-laws')?.value.trim()    || null,
    water_supply:       document.getElementById('rf-water')?.value.trim()         || null,
    sewage:             document.getElementById('rf-sewage')?.value.trim()        || null,
    rights:             document.getElementById('rf-rights')?.value.trim()        || null,
    docs:               JSON.stringify(selectedDocs),
    publish_date:       document.getElementById('rf-publish')?.value             || null,
    suumo_listed:       document.getElementById('rf-suumo')?.checked  ?? false,
    hp_listed:          document.getElementById('rf-hp')?.checked     ?? false,
    building_area_sqm:  parseFloatOrNull(document.getElementById('rf-bld-area')?.value),
    built_year:         parseIntOrNull(document.getElementById('rf-built-yr')?.value),
    built_month:        parseIntOrNull(document.getElementById('rf-built-mo')?.value),
    structure:          document.getElementById('rf-structure')?.value.trim()     || null,
    layout:             document.getElementById('rf-layout')?.value.trim()        || null,
    floors:             document.getElementById('rf-floors')?.value.trim()        || null,
    renovation_history: document.getElementById('rf-renovation')?.value.trim()   || null,
    rent:               parseFloatOrNull(document.getElementById('rf-rent')?.value),
    management_fee:     parseFloatOrNull(document.getElementById('rf-mgmt-fee')?.value),
    common_fee:         parseFloatOrNull(document.getElementById('rf-common-fee')?.value),
    deposit_months:     parseFloatOrNull(document.getElementById('rf-deposit')?.value),
    key_money_months:   parseFloatOrNull(document.getElementById('rf-keymoney')?.value),
    contract_type:      document.getElementById('rf-contract-type')?.value.trim()    || null,
    contract_period:    document.getElementById('rf-contract-period')?.value.trim()  || null,
    renewal_fee:        document.getElementById('rf-renewal')?.value.trim()          || null,
    parking_available:  document.getElementById('rf-parking')?.value === 'true',
    parking_count:      parseIntOrNull(document.getElementById('rf-parking-cnt')?.value),
    parking_fee:        parseFloatOrNull(document.getElementById('rf-parking-fee')?.value),
  };

  let rentalId = id;
  if (id) {
    propData.updated_at = new Date().toISOString();
    const { error } = await db.from('rental_properties').update(propData).eq('id', id);
    if (error) { toast('保存失敗: ' + error.message, 'error'); return; }
  } else {
    const { data, error } = await db.from('rental_properties').insert(propData).select().single();
    if (error) { toast('保存失敗: ' + error.message, 'error'); return; }
    rentalId = data.id;
  }

  detData.rental_id  = rentalId;
  detData.updated_at = new Date().toISOString();
  const { error: detErr } = await db.from('rental_details').upsert(detData, { onConflict: 'rental_id' });
  if (detErr) { toast('詳細保存失敗: ' + detErr.message, 'error'); return; }

  toast('保存しました', 'success');
  await showRentalDetail(rentalId);
}

async function deleteRentalProperty(id) {
  if (!confirm('この物件を削除します。入居者・履歴・コスト記録もすべて削除されます。よろしいですか？')) return;
  const { error } = await db.from('rental_properties').delete().eq('id', id);
  if (error) { toast('削除失敗: ' + error.message, 'error'); return; }
  toast('削除しました', 'success');
  await showRentalList();
}

// ════════════════════════════════════════════════════════════
// 入居者管理
// ════════════════════════════════════════════════════════════

async function openEditTenantModal(rentalId) {
  const { data: t } = await db.from('rental_tenants').select('*').eq('rental_id', rentalId).maybeSingle();
  const d = t || {};

  document.getElementById('modal').innerHTML = `
    <div class="modal-header">
      <div class="modal-title">👤 入居者情報を登録・編集</div>
      <button class="modal-close" onclick="closeModal()">✕</button>
    </div>
    <div class="modal-body">
      <div class="form-section">基本情報</div>
      <div class="form-row">
        <div class="form-group">
          <label>氏名</label>
          <input type="text" id="tm-name" class="qs-control" value="${esc(d.tenant_name || '')}">
        </div>
        <div class="form-group">
          <label>会社名</label>
          <input type="text" id="tm-company" class="qs-control" value="${esc(d.company_name || '')}">
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>電話番号</label>
          <input type="tel" id="tm-phone" class="qs-control" value="${esc(d.phone || '')}">
        </div>
        <div class="form-group">
          <label>緊急連絡先</label>
          <input type="tel" id="tm-emergency" class="qs-control" value="${esc(d.emergency_phone || '')}">
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>保証人氏名</label>
          <input type="text" id="tm-guarantor" class="qs-control" value="${esc(d.guarantor_name || '')}">
        </div>
        <div class="form-group">
          <label>保証人電話</label>
          <input type="tel" id="tm-guarantor-phone" class="qs-control" value="${esc(d.guarantor_phone || '')}">
        </div>
      </div>
      <div class="form-section">契約情報</div>
      <div class="form-row">
        <div class="form-group">
          <label>契約開始</label>
          <input type="date" id="tm-start" class="qs-control" value="${d.contract_start || ''}">
        </div>
        <div class="form-group">
          <label>契約終了</label>
          <input type="date" id="tm-end" class="qs-control" value="${d.contract_end || ''}">
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>火災保険状況</label>
          <input type="text" id="tm-insurance" class="qs-control" placeholder="加入済・未加入・手配中" value="${esc(d.insurance_status || '')}">
        </div>
        <div class="form-group">
          <label>保険会社</label>
          <input type="text" id="tm-ins-company" class="qs-control" value="${esc(d.insurance_company || '')}">
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>保険満期日</label>
          <input type="date" id="tm-ins-expiry" class="qs-control" value="${d.insurance_expiry || ''}">
        </div>
        <div class="form-group">
          <label>鍵本数</label>
          <input type="number" id="tm-keys" class="qs-control" min="0" value="${d.key_count ?? ''}">
        </div>
      </div>
      <div class="form-row">
        <div class="form-group" style="grid-column:span 2;">
          <label>鍵保管場所</label>
          <input type="text" id="tm-key-loc" class="qs-control" value="${esc(d.key_location || '')}">
        </div>
      </div>
      <div class="form-row">
        <div class="form-group" style="grid-column:span 2;">
          <label>備考</label>
          <textarea id="tm-notes" class="qs-control" rows="3">${esc(d.notes || '')}</textarea>
        </div>
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn-cancel" onclick="closeModal()">キャンセル</button>
      <button class="btn-primary" onclick="saveTenant('${rentalId}')">💾 保存</button>
    </div>
  `;
  document.getElementById('modal-bg').classList.remove('hidden');
}

async function saveTenant(rentalId) {
  const data = {
    rental_id:         rentalId,
    tenant_name:       document.getElementById('tm-name')?.value.trim()           || null,
    company_name:      document.getElementById('tm-company')?.value.trim()        || null,
    phone:             document.getElementById('tm-phone')?.value.trim()           || null,
    emergency_phone:   document.getElementById('tm-emergency')?.value.trim()      || null,
    guarantor_name:    document.getElementById('tm-guarantor')?.value.trim()      || null,
    guarantor_phone:   document.getElementById('tm-guarantor-phone')?.value.trim()|| null,
    contract_start:    document.getElementById('tm-start')?.value                 || null,
    contract_end:      document.getElementById('tm-end')?.value                   || null,
    insurance_status:  document.getElementById('tm-insurance')?.value.trim()      || null,
    insurance_company: document.getElementById('tm-ins-company')?.value.trim()    || null,
    insurance_expiry:  document.getElementById('tm-ins-expiry')?.value            || null,
    key_count:         parseIntOrNull(document.getElementById('tm-keys')?.value),
    key_location:      document.getElementById('tm-key-loc')?.value.trim()        || null,
    notes:             document.getElementById('tm-notes')?.value.trim()          || null,
    updated_at:        new Date().toISOString(),
  };

  const { error } = await db.from('rental_tenants').upsert(data, { onConflict: 'rental_id' });
  if (error) { toast('保存失敗: ' + error.message, 'error'); return; }
  toast('入居者情報を保存しました', 'success');
  closeModal();
  await renderRentalDetail(rentalId);
}

async function openMoveOutModal(rentalId) {
  const { data: t } = await db.from('rental_tenants').select('*').eq('rental_id', rentalId).maybeSingle();
  const d = t || {};

  document.getElementById('modal').innerHTML = `
    <div class="modal-header">
      <div class="modal-title">🚪 退去処理</div>
      <button class="modal-close" onclick="closeModal()">✕</button>
    </div>
    <div class="modal-body">
      <div style="background:var(--bg-input);padding:12px;border-radius:8px;margin-bottom:16px;font-size:13px;">
        <strong>${esc(d.tenant_name || '（氏名未入力）')}</strong> を退去として処理します。<br>
        現在の入居者情報は履歴に移動され、物件状態が「空室」に変わります。
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>退去日（契約終了日）</label>
          <input type="date" id="mo-end" class="qs-control" value="${d.contract_end || ''}">
        </div>
        <div class="form-group">
          <label>退去事由</label>
          <input type="text" id="mo-reason" class="qs-control" placeholder="転居・期間満了・解約申入れ など">
        </div>
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn-cancel" onclick="closeModal()">キャンセル</button>
      <button class="btn-danger" onclick="confirmMoveOut('${rentalId}')">退去処理を実行</button>
    </div>
  `;
  document.getElementById('modal-bg').classList.remove('hidden');
}

async function confirmMoveOut(rentalId) {
  const { data: t }  = await db.from('rental_tenants').select('*').eq('rental_id', rentalId).maybeSingle();
  const { data: rd } = await db.from('rental_details').select('rent').eq('rental_id', rentalId).maybeSingle();
  const contractEnd  = document.getElementById('mo-end')?.value    || null;
  const reason       = document.getElementById('mo-reason')?.value.trim() || null;

  if (t) {
    const histData = {
      rental_id:       rentalId,
      tenant_name:     t.tenant_name,
      company_name:    t.company_name,
      contract_start:  t.contract_start,
      contract_end:    contractEnd || t.contract_end,
      move_out_reason: reason,
      rent:            rd?.rent || null,
      notes:           t.notes,
    };
    const { error: hErr } = await db.from('rental_tenant_history').insert(histData);
    if (hErr) { toast('履歴保存失敗: ' + hErr.message, 'error'); return; }
    const { error: dErr } = await db.from('rental_tenants').delete().eq('rental_id', rentalId);
    if (dErr) { toast('入居者削除失敗: ' + dErr.message, 'error'); return; }
  }

  const { error: sErr } = await db.from('rental_properties')
    .update({ status: 'vacant', updated_at: new Date().toISOString() }).eq('id', rentalId);
  if (sErr) { toast('状態更新失敗: ' + sErr.message, 'error'); return; }

  toast('退去処理が完了しました', 'success');
  closeModal();
  await renderRentalDetail(rentalId);
}

// ════════════════════════════════════════════════════════════
// 区画管理（ビル用）
// ════════════════════════════════════════════════════════════

async function openUnitModal(rentalId, unitId) {
  let d = {};
  if (unitId) {
    const { data } = await db.from('rental_units').select('*').eq('id', unitId).single();
    d = data || {};
  }

  const statusOpts = [['vacant','空室'],['occupied','入居中'],['leaving','退去予定']];
  const selU = (id, val, opts) =>
    `<select id="${id}" class="qs-control">${opts.map(([v,l]) =>
      `<option value="${v}" ${val===v?'selected':''}>${l}</option>`).join('')}</select>`;

  document.getElementById('modal').innerHTML = `
    <div class="modal-header">
      <div class="modal-title">🏗 ${unitId ? '区画を編集' : '区画を追加'}</div>
      <button class="modal-close" onclick="closeModal()">✕</button>
    </div>
    <div class="modal-body">
      <div class="form-section">区画情報</div>
      <div class="form-row">
        <div class="form-group">
          <label>区画番号</label>
          <input type="text" id="um-number" class="qs-control" value="${esc(d.unit_number || '')}">
        </div>
        <div class="form-group">
          <label>階</label>
          <input type="text" id="um-floor" class="qs-control" value="${esc(d.floor || '')}">
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>用途</label>
          <input type="text" id="um-usage" class="qs-control" placeholder="事務所・店舗・倉庫・その他" value="${esc(d.usage || '')}">
        </div>
        <div class="form-group">
          <label>面積(㎡)</label>
          <input type="number" id="um-area" class="qs-control" step="0.01" value="${d.area_sqm ?? ''}">
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>賃料（円）</label>
          <input type="number" id="um-rent" class="qs-control" step="1" value="${d.rent ?? ''}">
        </div>
        <div class="form-group">
          <label>管理費（円）</label>
          <input type="number" id="um-mgmt" class="qs-control" step="1" value="${d.management_fee ?? ''}">
        </div>
      </div>
      <div class="form-section">テナント情報</div>
      <div class="form-row">
        <div class="form-group" style="grid-column:span 2;">
          <label>テナント名</label>
          <input type="text" id="um-tenant" class="qs-control" value="${esc(d.tenant_name || '')}">
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>契約開始</label>
          <input type="date" id="um-start" class="qs-control" value="${d.contract_start || ''}">
        </div>
        <div class="form-group">
          <label>契約終了</label>
          <input type="date" id="um-end" class="qs-control" value="${d.contract_end || ''}">
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>状態</label>
          ${selU('um-status', d.unit_status || 'vacant', statusOpts)}
        </div>
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn-cancel" onclick="closeModal()">キャンセル</button>
      <button class="btn-primary" onclick="saveUnit('${rentalId}','${unitId || ''}')">💾 保存</button>
    </div>
  `;
  document.getElementById('modal-bg').classList.remove('hidden');
}

async function saveUnit(rentalId, unitId) {
  const data = {
    rental_id:      rentalId,
    unit_number:    document.getElementById('um-number')?.value.trim() || null,
    floor:          document.getElementById('um-floor')?.value.trim()  || null,
    usage:          document.getElementById('um-usage')?.value.trim()  || null,
    area_sqm:       parseFloatOrNull(document.getElementById('um-area')?.value),
    rent:           parseFloatOrNull(document.getElementById('um-rent')?.value),
    management_fee: parseFloatOrNull(document.getElementById('um-mgmt')?.value),
    tenant_name:    document.getElementById('um-tenant')?.value.trim() || null,
    contract_start: document.getElementById('um-start')?.value         || null,
    contract_end:   document.getElementById('um-end')?.value           || null,
    unit_status:    document.getElementById('um-status')?.value,
    updated_at:     new Date().toISOString(),
  };

  let err;
  if (unitId) {
    ({ error: err } = await db.from('rental_units').update(data).eq('id', unitId));
  } else {
    ({ error: err } = await db.from('rental_units').insert(data));
  }
  if (err) { toast('保存失敗: ' + err.message, 'error'); return; }
  toast('区画情報を保存しました', 'success');
  closeModal();
  await renderRentalDetail(rentalId);
}

async function deleteUnit(unitId, rentalId) {
  if (!confirm('この区画を削除しますか？')) return;
  const { error } = await db.from('rental_units').delete().eq('id', unitId);
  if (error) { toast('削除失敗: ' + error.message, 'error'); return; }
  toast('削除しました', 'success');
  await renderRentalDetail(rentalId);
}

// ════════════════════════════════════════════════════════════
// 賃貸原価管理
// ════════════════════════════════════════════════════════════

async function renderRentalCost(rentalId) {
  const el = document.getElementById('content');
  el.innerHTML = '<div style="padding:40px;text-align:center;color:var(--text-muted);">読み込み中…</div>';

  const [propRes, costsRes, logsRes] = await Promise.all([
    db.from('rental_properties').select('property_name, address, code, type').eq('id', rentalId).single(),
    db.from('rental_costs').select('*').eq('rental_id', rentalId).maybeSingle(),
    db.from('rental_cost_logs').select('*').eq('rental_id', rentalId).order('created_at', { ascending: false }),
  ]);

  if (propRes.error) { toast('物件取得失敗', 'error'); return; }
  const prop  = propRes.data;
  const costs = costsRes.data || {};
  const logs  = logsRes.data  || [];

  const propTitle = prop.property_name || prop.address || prop.code || '（名称未入力）';

  const logsByCat = {};
  logs.forEach(l => { (logsByCat[l.category] = logsByCat[l.category] || []).push(l); });

  const incCats      = [['income_rent','賃料収入'],['income_mgmt','管理費収入'],['income_parking','駐車場収入']];
  const annualCats   = [['tax_annual','固定資産税'],['fire_annual','火災保険料'],['hoa_annual','管理組合費']];
  const monthlyCats  = [['water_monthly','水道代'],['electricity_monthly','電気代'],['gas_monthly','ガス代']];
  const irregCats    = [['repair','修繕費'],['cleaning','清掃費'],['inspection','点検費'],['advertising','広告費'],['personnel','人件費'],['other_expense','その他経費']];

  function makeYearGroupsRC(catLogs, catKey, isIncome) {
    if (!catLogs || catLogs.length === 0)
      return '<div style="padding:8px 0;text-align:center;color:var(--text-muted);font-size:12px;">履歴なし</div>';

    const byYear = {};
    catLogs.forEach(l => {
      const y = l.record_year || (l.record_date ? parseInt(l.record_date.slice(0,4)) : new Date(l.created_at).getFullYear());
      (byYear[y] = byYear[y] || []).push(l);
    });
    const years = Object.keys(byYear).map(Number).sort((a,b) => b - a);

    return years.map(y => {
      const items = byYear[y];
      const total = items.reduce((s,i) => s + Number(i.amount), 0);
      const gid   = 'rcg' + Math.random().toString(36).slice(2,8);

      const rows = items.map((l,i) => {
        const dateStr = l.record_date
          || (l.record_month ? y + '/' + String(l.record_month).padStart(2,'0') : String(y));
        return `<tr class="rcgrow-${gid}" style="${i >= 3 ? 'display:none' : ''}">
          <td style="font-size:11px;color:var(--text-muted);white-space:nowrap;">${dateStr}</td>
          <td style="white-space:nowrap;${isIncome ? 'color:var(--green);' : ''}">
            ${isIncome ? '+' : '-'}${Number(l.amount).toLocaleString('ja-JP')} 円
          </td>
          <td style="font-size:12px;color:var(--text-secondary);">${esc(l.memo || '')}</td>
          <td>
            <button class="btn-sm btn-danger" style="padding:2px 7px;font-size:11px;"
                    onclick="deleteRentalCostLog('${l.id}','${rentalId}')">削除</button>
          </td>
        </tr>`;
      }).join('');

      const hiddenCount = items.length > 3 ? items.length - 3 : 0;
      const moreRow = hiddenCount > 0
        ? `<tr id="rcmore-${gid}">
             <td colspan="4" style="text-align:center;padding:4px 0;">
               <button class="btn-sm" style="font-size:11px;"
                       onclick="toggleRentalYearGroup('${gid}',this)">もっと見る▼ (+${hiddenCount}件)</button>
             </td>
           </tr>` : '';

      return `
        <div style="margin-bottom:8px;">
          <div style="display:flex;justify-content:space-between;align-items:center;
                      padding:4px 8px;background:var(--bg-input);border-radius:4px;font-size:12px;font-weight:600;">
            <span>${y}年</span>
            <span style="${isIncome ? 'color:var(--green)' : 'color:var(--red);'}">
              ${isIncome ? '+' : '-'}${total.toLocaleString('ja-JP')} 円
            </span>
          </div>
          <table style="width:100%;border-collapse:collapse;font-size:12px;">
            <tbody>${rows}${moreRow}</tbody>
          </table>
        </div>`;
    }).join('');
  }

  function makeLogInput(cat, inputType) {
    const yr = new Date().getFullYear(), mo = new Date().getMonth() + 1;
    if (inputType === 'monthly') {
      return `<div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin-bottom:8px;">
        <input type="number" id="rli-yr-${cat}" class="qs-control" style="width:76px;" placeholder="年" value="${yr}">
        <input type="number" id="rli-mo-${cat}" class="qs-control" style="width:56px;" placeholder="月" min="1" max="12" value="${mo}">
        <input type="number" id="rli-amt-${cat}" class="qs-control" style="width:120px;" placeholder="金額（円）" step="1" min="0">
        <input type="text"   id="rli-memo-${cat}" class="qs-control" style="flex:1;min-width:80px;" placeholder="メモ">
        <button class="btn-sm" onclick="addRentalCostLog('${rentalId}','${cat}','monthly')">追加</button>
      </div>`;
    } else if (inputType === 'annual') {
      return `<div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin-bottom:8px;">
        <input type="number" id="rli-yr-${cat}" class="qs-control" style="width:76px;" placeholder="年" value="${yr}">
        <input type="number" id="rli-amt-${cat}" class="qs-control" style="width:120px;" placeholder="金額（円）" step="1" min="0">
        <input type="text"   id="rli-memo-${cat}" class="qs-control" style="flex:1;min-width:80px;" placeholder="メモ">
        <button class="btn-sm" onclick="addRentalCostLog('${rentalId}','${cat}','annual')">追加</button>
      </div>`;
    } else {
      return `<div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin-bottom:8px;">
        <input type="date"   id="rli-dt-${cat}" class="qs-control" style="width:130px;">
        <input type="number" id="rli-amt-${cat}" class="qs-control" style="width:120px;" placeholder="金額（円）" step="1" min="0">
        <input type="text"   id="rli-memo-${cat}" class="qs-control" style="flex:1;min-width:80px;" placeholder="メモ">
        <button class="btn-sm" onclick="addRentalCostLog('${rentalId}','${cat}','irregular')">追加</button>
      </div>`;
    }
  }

  function makeCostLogSec(catPairs, inputType, isIncome) {
    return catPairs.map(([cat, label]) => `
      <div style="margin-bottom:20px;">
        <div style="font-size:13px;font-weight:700;border-bottom:1px solid var(--border);
                    padding-bottom:4px;margin-bottom:8px;">${label}</div>
        ${makeLogInput(cat, inputType)}
        ${makeYearGroupsRC(logsByCat[cat], cat, isIncome)}
      </div>`).join('');
  }

  const totalIncome  = incCats.reduce((s,[c]) => s + (logsByCat[c]||[]).reduce((a,l)=>a+Number(l.amount),0), 0);
  const totalExpense = [...annualCats,...monthlyCats,...irregCats].reduce((s,[c]) => s + (logsByCat[c]||[]).reduce((a,l)=>a+Number(l.amount),0), 0);

  const acqFields = ['acquisition_cost','land_acquisition_cost','building_acquisition_cost','broker_fee',
    'acquisition_tax','transfer_reg','stamp_tax','survey_purchase','other_purchase',
    'reform_cost','equipment_cost','ground_warranty','interior_cost','other_construction',
    'reg_survey','farmland','dev_permit','other_reg'];
  const totalAcq = acqFields.reduce((s,f) => s + (costs[f] ? Number(costs[f]) : 0), 0);
  const netIncome = totalIncome - totalExpense;

  el.innerHTML = `
    <div class="page-header">
      <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;">
        <button class="btn-back" onclick="showRentalDetail('${rentalId}')">← 詳細へ</button>
        <div class="page-title">📊 原価管理 — ${esc(propTitle)}</div>
      </div>
    </div>

    <div class="section" style="margin-bottom:16px;">
      <div class="section-title"><span class="icon">💹</span>収支サマリー</div>
      <div style="display:flex;gap:24px;flex-wrap:wrap;padding:8px 0;">
        <div style="text-align:center;">
          <div style="font-size:11px;color:var(--text-muted);margin-bottom:2px;">取得コスト合計</div>
          <div style="font-size:20px;font-weight:700;color:var(--red);">-${totalAcq.toLocaleString('ja-JP')} 円</div>
        </div>
        <div style="text-align:center;">
          <div style="font-size:11px;color:var(--text-muted);margin-bottom:2px;">収入累計</div>
          <div style="font-size:20px;font-weight:700;color:var(--green);">+${totalIncome.toLocaleString('ja-JP')} 円</div>
        </div>
        <div style="text-align:center;">
          <div style="font-size:11px;color:var(--text-muted);margin-bottom:2px;">経費累計</div>
          <div style="font-size:20px;font-weight:700;color:var(--red);">-${totalExpense.toLocaleString('ja-JP')} 円</div>
        </div>
        <div style="text-align:center;">
          <div style="font-size:11px;color:var(--text-muted);margin-bottom:2px;">純収益</div>
          <div style="font-size:20px;font-weight:700;color:${netIncome >= 0 ? 'var(--green)' : 'var(--red);'};">
            ${netIncome >= 0 ? '+' : ''}${netIncome.toLocaleString('ja-JP')} 円
          </div>
        </div>
      </div>
    </div>

    <div class="section" style="margin-bottom:16px;">
      <div class="section-title" style="display:flex;justify-content:space-between;align-items:center;">
        <span><span class="icon">💴</span>取得コスト</span>
        <button class="btn-sm" onclick="saveRentalCost('${rentalId}')">💾 保存</button>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>取得日</label>
          <input type="date" id="rc-acq-date" class="qs-control" value="${costs.acquisition_date || ''}">
        </div>
        ${prop.type === 'land' ? `
        <div class="form-group">
          <label>取得価格（円）</label>
          <input type="number" id="rc-acq" class="qs-control" step="1" value="${costs.acquisition_cost ?? ''}">
        </div>
        ` : `
        <div class="form-group">
          <label>土地取得価格（円）</label>
          <input type="number" id="rc-land-acq" class="qs-control" step="1" value="${costs.land_acquisition_cost ?? ''}">
        </div>
        `}
      </div>
      ${prop.type !== 'land' ? `
      <div class="form-row">
        <div class="form-group">
          <label>建物取得価格（税込・円）</label>
          <input type="number" id="rc-bld-acq" class="qs-control" step="1" value="${costs.building_acquisition_cost ?? ''}">
        </div>
        <div class="form-group">
          <label>仲介手数料（円）</label>
          <input type="number" id="rc-broker" class="qs-control" step="1" value="${costs.broker_fee ?? ''}">
        </div>
      </div>` : `
      <div class="form-row">
        <div class="form-group">
          <label>仲介手数料（円）</label>
          <input type="number" id="rc-broker" class="qs-control" step="1" value="${costs.broker_fee ?? ''}">
        </div>
      </div>`}
      <div class="form-row">
        <div class="form-group">
          <label>不動産取得税（円）</label>
          <input type="number" id="rc-acq-tax" class="qs-control" step="1" value="${costs.acquisition_tax ?? ''}">
        </div>
        <div class="form-group">
          <label>移転登記費用（円）</label>
          <input type="number" id="rc-transfer-reg" class="qs-control" step="1" value="${costs.transfer_reg ?? ''}">
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>印紙税（円）</label>
          <input type="number" id="rc-stamp" class="qs-control" step="1" value="${costs.stamp_tax ?? ''}">
        </div>
        <div class="form-group">
          <label>測量費（円）</label>
          <input type="number" id="rc-survey" class="qs-control" step="1" value="${costs.survey_purchase ?? ''}">
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>その他購入費用（円）</label>
          <input type="number" id="rc-other-purch" class="qs-control" step="1" value="${costs.other_purchase ?? ''}">
        </div>
        <div class="form-group">
          <label>リフォーム工事費（円）</label>
          <input type="number" id="rc-reform" class="qs-control" step="1" value="${costs.reform_cost ?? ''}">
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>設備交換費（円）</label>
          <input type="number" id="rc-equip" class="qs-control" step="1" value="${costs.equipment_cost ?? ''}">
        </div>
        <div class="form-group">
          <label>地盤保証料（円）</label>
          <input type="number" id="rc-ground" class="qs-control" step="1" value="${costs.ground_warranty ?? ''}">
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>展示内装費（円）</label>
          <input type="number" id="rc-interior" class="qs-control" step="1" value="${costs.interior_cost ?? ''}">
        </div>
        <div class="form-group">
          <label>その他工事費（円）</label>
          <input type="number" id="rc-other-const" class="qs-control" step="1" value="${costs.other_construction ?? ''}">
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>表示登記（円）</label>
          <input type="number" id="rc-reg-survey" class="qs-control" step="1" value="${costs.reg_survey ?? ''}">
        </div>
        <div class="form-group">
          <label>農地転用（円）</label>
          <input type="number" id="rc-farmland" class="qs-control" step="1" value="${costs.farmland ?? ''}">
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>開発許可費（円）</label>
          <input type="number" id="rc-dev-permit" class="qs-control" step="1" value="${costs.dev_permit ?? ''}">
        </div>
        <div class="form-group">
          <label>その他登記費（円）</label>
          <input type="number" id="rc-other-reg" class="qs-control" step="1" value="${costs.other_reg ?? ''}">
        </div>
      </div>
    </div>

    <div class="section" style="margin-bottom:16px;">
      <div class="section-title"><span class="icon">💰</span>収入履歴</div>
      ${makeCostLogSec(incCats, 'monthly', true)}
    </div>

    <div class="section" style="margin-bottom:16px;">
      <div class="section-title"><span class="icon">📅</span>年次経費</div>
      ${makeCostLogSec(annualCats, 'annual', false)}
    </div>

    <div class="section" style="margin-bottom:16px;">
      <div class="section-title"><span class="icon">🗓</span>月次経費</div>
      ${makeCostLogSec(monthlyCats, 'monthly', false)}
    </div>

    <div class="section" style="margin-bottom:40px;">
      <div class="section-title"><span class="icon">⚡</span>不定期経費</div>
      ${makeCostLogSec(irregCats, 'irregular', false)}
    </div>
  `;
}

async function saveRentalCost(rentalId) {
  const v = id => document.getElementById(id)?.value;
  const data = {
    rental_id:                  rentalId,
    acquisition_date:           v('rc-acq-date')    || null,
    acquisition_cost:           parseFloatOrNull(v('rc-acq')),
    land_acquisition_cost:      parseFloatOrNull(v('rc-land-acq')),
    building_acquisition_cost:  parseFloatOrNull(v('rc-bld-acq')),
    broker_fee:                 parseFloatOrNull(v('rc-broker')),
    acquisition_tax:            parseFloatOrNull(v('rc-acq-tax')),
    transfer_reg:               parseFloatOrNull(v('rc-transfer-reg')),
    stamp_tax:                  parseFloatOrNull(v('rc-stamp')),
    survey_purchase:            parseFloatOrNull(v('rc-survey')),
    other_purchase:             parseFloatOrNull(v('rc-other-purch')),
    reform_cost:                parseFloatOrNull(v('rc-reform')),
    equipment_cost:             parseFloatOrNull(v('rc-equip')),
    ground_warranty:            parseFloatOrNull(v('rc-ground')),
    interior_cost:              parseFloatOrNull(v('rc-interior')),
    other_construction:         parseFloatOrNull(v('rc-other-const')),
    reg_survey:                 parseFloatOrNull(v('rc-reg-survey')),
    farmland:                   parseFloatOrNull(v('rc-farmland')),
    dev_permit:                 parseFloatOrNull(v('rc-dev-permit')),
    other_reg:                  parseFloatOrNull(v('rc-other-reg')),
    updated_at:                 new Date().toISOString(),
  };

  const { error } = await db.from('rental_costs').upsert(data, { onConflict: 'rental_id' });
  if (error) { toast('保存失敗: ' + error.message, 'error'); return; }
  toast('取得コストを保存しました', 'success');
  await renderRentalCost(rentalId);
}

async function addRentalCostLog(rentalId, cat, inputType) {
  const amt = parseFloat(document.getElementById(`rli-amt-${cat}`)?.value);
  if (!amt || amt <= 0) { toast('金額を入力してください', 'error'); return; }

  const data = {
    rental_id: rentalId,
    category:  cat,
    amount:    amt,
    memo:      document.getElementById(`rli-memo-${cat}`)?.value.trim() || null,
  };

  if (inputType === 'monthly') {
    const yr = parseInt(document.getElementById(`rli-yr-${cat}`)?.value);
    const mo = parseInt(document.getElementById(`rli-mo-${cat}`)?.value);
    if (!yr || !mo) { toast('年・月を入力してください', 'error'); return; }
    data.record_year  = yr;
    data.record_month = mo;
  } else if (inputType === 'annual') {
    const yr = parseInt(document.getElementById(`rli-yr-${cat}`)?.value);
    if (!yr) { toast('年を入力してください', 'error'); return; }
    data.record_year = yr;
  } else {
    const dt = document.getElementById(`rli-dt-${cat}`)?.value;
    if (!dt) { toast('日付を入力してください', 'error'); return; }
    data.record_date  = dt;
    data.record_year  = parseInt(dt.slice(0,4));
    data.record_month = parseInt(dt.slice(5,7));
  }

  const { error } = await db.from('rental_cost_logs').insert(data);
  if (error) { toast('追加失敗: ' + error.message, 'error'); return; }
  toast('追加しました', 'success');
  await renderRentalCost(rentalId);
}

async function deleteRentalCostLog(id, rentalId) {
  if (!confirm('この記録を削除しますか？')) return;
  const { error } = await db.from('rental_cost_logs').delete().eq('id', id);
  if (error) { toast('削除失敗: ' + error.message, 'error'); return; }
  toast('削除しました', 'success');
  await renderRentalCost(rentalId);
}

function toggleRentalYearGroup(gid, btn) {
  const rows    = document.querySelectorAll('.rcgrow-' + gid);
  const moreRow = document.getElementById('rcmore-' + gid);
  const isHidden = rows.length > 3 && rows[3].style.display === 'none';
  rows.forEach((r, i) => { if (i >= 3) r.style.display = isHidden ? '' : 'none'; });
  if (btn) btn.textContent = isHidden ? '折りたたむ▲' : 'もっと見る▼';
}

// ════════════════════════════════════════════════════════════
// 修繕台帳
// ════════════════════════════════════════════════════════════

async function renderRepairLog() {
  const el = document.getElementById('content');
  el.innerHTML = '<div style="padding:40px;text-align:center;color:var(--text-muted);">読み込み中…</div>';

  const [repairsRes, propsRes] = await Promise.all([
    db.from('repair_logs')
      .select('*, rental_properties(property_name, address, code)')
      .order('repair_date', { ascending: false }),
    db.from('rental_properties').select('id, property_name, address, code').order('created_at', { ascending: false }),
  ]);

  if (repairsRes.error) { toast('取得失敗: ' + repairsRes.error.message, 'error'); return; }
  const repairs = repairsRes.data || [];
  const props   = propsRes.data   || [];
  window._repairProps = props;

  const pName = r => {
    const rp = r.rental_properties;
    return rp ? (rp.property_name || rp.address || rp.code || '（名称未入力）') : '—';
  };

  const rows = repairs.map(r => `
    <tr>
      <td style="white-space:nowrap;font-size:12px;">${esc(pName(r))}</td>
      <td style="white-space:nowrap;">${r.repair_date || '—'}</td>
      <td>${esc(r.location || '—')}</td>
      <td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;"
          title="${esc(r.description || '')}">${esc(r.description || '—')}</td>
      <td>${esc(r.contractor || '—')}</td>
      <td style="white-space:nowrap;">${r.cost != null ? Number(r.cost).toLocaleString('ja-JP') + '円' : '—'}</td>
      <td style="white-space:nowrap;font-size:12px;">${r.next_inspection || '—'}</td>
      <td>
        <button class="btn-sm" onclick="openRepairModal('${r.rental_id}','${r.id}')">編集</button>
        <button class="btn-sm btn-danger" onclick="deleteRepair('${r.id}')">削除</button>
      </td>
    </tr>`).join('');

  el.innerHTML = `
    <div class="page-header">
      <div>
        <div class="page-title">🔧 修繕台帳</div>
        <div class="page-sub">全${repairs.length}件</div>
      </div>
      <button class="btn-primary" onclick="openRepairModal()">＋ 修繕記録を追加</button>
    </div>

    ${repairs.length === 0
      ? `<div class="section" style="text-align:center;padding:40px;color:var(--text-muted);">修繕記録がありません</div>`
      : `<div class="section" style="padding:0;overflow:hidden;">
           <div style="overflow-x:auto;">
             <table class="data-table">
               <thead><tr>
                 <th>物件名</th><th>修繕日</th><th>場所</th><th>内容</th>
                 <th>業者</th><th>費用</th><th>次回点検</th><th></th>
               </tr></thead>
               <tbody>${rows}</tbody>
             </table>
           </div>
         </div>`
    }
  `;
}

async function openRepairModal(rentalId, repairId) {
  let props = window._repairProps;
  if (!props) {
    const { data } = await db.from('rental_properties')
      .select('id, property_name, address, code').order('created_at', { ascending: false });
    props = data || [];
    window._repairProps = props;
  }

  let d = {};
  if (repairId) {
    const { data } = await db.from('repair_logs').select('*').eq('id', repairId).single();
    d = data || {};
  }

  const propOpts = props.map(p =>
    `<option value="${p.id}" ${(rentalId === p.id || d.rental_id === p.id) ? 'selected' : ''}>
      ${esc(p.property_name || p.address || p.code || '（名称未入力）')}
    </option>`
  ).join('');

  document.getElementById('modal').innerHTML = `
    <div class="modal-header">
      <div class="modal-title">🔧 ${repairId ? '修繕記録を編集' : '修繕記録を追加'}</div>
      <button class="modal-close" onclick="closeModal()">✕</button>
    </div>
    <div class="modal-body">
      <input type="hidden" id="rep-id" value="${repairId || ''}">
      <div class="form-section">物件・日時</div>
      <div class="form-row">
        <div class="form-group" style="grid-column:span 2;">
          <label>物件 *</label>
          <select id="rep-prop" class="qs-control">
            <option value="">（物件を選択）</option>
            ${propOpts}
          </select>
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>修繕日 *</label>
          <input type="date" id="rep-date" class="qs-control" value="${d.repair_date || ''}">
        </div>
        <div class="form-group">
          <label>場所</label>
          <input type="text" id="rep-location" class="qs-control" placeholder="外壁・屋根・給水管 など" value="${esc(d.location || '')}">
        </div>
      </div>
      <div class="form-section">内容・費用</div>
      <div class="form-row">
        <div class="form-group" style="grid-column:span 2;">
          <label>修繕内容</label>
          <textarea id="rep-desc" class="qs-control" rows="3">${esc(d.description || '')}</textarea>
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>業者</label>
          <input type="text" id="rep-contractor" class="qs-control" value="${esc(d.contractor || '')}">
        </div>
        <div class="form-group">
          <label>費用（円）</label>
          <input type="number" id="rep-cost" class="qs-control" step="1" value="${d.cost ?? ''}">
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>次回点検予定日</label>
          <input type="date" id="rep-next" class="qs-control" value="${d.next_inspection || ''}">
        </div>
        <div class="form-group">
          <label>備考</label>
          <input type="text" id="rep-notes" class="qs-control" value="${esc(d.notes || '')}">
        </div>
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn-cancel" onclick="closeModal()">キャンセル</button>
      <button class="btn-primary" onclick="saveRepair()">💾 保存</button>
    </div>
  `;
  document.getElementById('modal-bg').classList.remove('hidden');
}

async function saveRepair() {
  const repairId = document.getElementById('rep-id')?.value || null;
  const data = {
    rental_id:       document.getElementById('rep-prop')?.value || null,
    repair_date:     document.getElementById('rep-date')?.value || null,
    location:        document.getElementById('rep-location')?.value.trim()   || null,
    description:     document.getElementById('rep-desc')?.value.trim()       || null,
    contractor:      document.getElementById('rep-contractor')?.value.trim() || null,
    cost:            parseFloatOrNull(document.getElementById('rep-cost')?.value),
    next_inspection: document.getElementById('rep-next')?.value              || null,
    notes:           document.getElementById('rep-notes')?.value.trim()      || null,
    updated_at:      new Date().toISOString(),
  };

  if (!data.rental_id)   { toast('物件を選択してください', 'error'); return; }
  if (!data.repair_date) { toast('修繕日を入力してください', 'error'); return; }

  let err;
  if (repairId) {
    ({ error: err } = await db.from('repair_logs').update(data).eq('id', repairId));
  } else {
    ({ error: err } = await db.from('repair_logs').insert(data));
  }
  if (err) { toast('保存失敗: ' + err.message, 'error'); return; }
  toast('保存しました', 'success');
  closeModal();
  await renderRepairLog();
}

async function deleteRepair(id) {
  if (!confirm('この修繕記録を削除しますか？')) return;
  const { error } = await db.from('repair_logs').delete().eq('id', id);
  if (error) { toast('削除失敗: ' + error.message, 'error'); return; }
  toast('削除しました', 'success');
  await renderRepairLog();
}
