// ════════════════════════════════════════════════════════════
// 内見・問い合わせ記録 v1
// ════════════════════════════════════════════════════════════

const IQ_TYPE  = { viewing:'内見', inquiry:'問い合わせ' };
const IQ_ROUTE = { suumo:'SUUMO', hp:'HP', sign:'売看板', referral:'紹介', other:'その他' };
const IQ_STAT  = { considering:'検討中', positive:'前向き', declined:'見送り', contracted:'成約' };
const IQ_STAT_COLOR = {
  considering: 'color:var(--text-secondary);',
  positive:    'color:var(--green);font-weight:600;',
  declined:    'color:var(--text-muted);',
  contracted:  'color:var(--accent);font-weight:600;',
};

function buildInquirySection(logs, propId, propType) {
  const rows = logs.map(l => `
    <tr>
      <td style="white-space:nowrap;">${l.date || '—'}</td>
      <td>
        <span style="font-size:11px;padding:2px 7px;border-radius:4px;font-weight:600;
          ${l.type === 'viewing'
            ? 'background:#1a3a6e;color:#6ea8fe;'
            : 'background:#2a1a5e;color:#b39ddb;'}">
          ${IQ_TYPE[l.type] || l.type}
        </span>
      </td>
      <td style="font-size:12px;">${IQ_ROUTE[l.route] || '—'}</td>
      <td style="font-size:12px;${IQ_STAT_COLOR[l.status] || ''}">${IQ_STAT[l.status] || '—'}</td>
      <td style="font-size:12px;max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;"
          title="${esc(l.memo || '')}">${esc(l.memo || '')}</td>
      <td>
        <button class="btn-sm btn-danger"
                onclick="deleteInquiryLog('${l.id}','${propId}','${propType}')">削除</button>
      </td>
    </tr>`).join('');

  return `
    <div class="section" style="margin-bottom:16px;">
      <div class="section-title" style="display:flex;justify-content:space-between;align-items:center;">
        <span><span class="icon">📞</span>内見・問い合わせ記録</span>
        <button class="btn-sm" onclick="openInquiryModal('${propId}','${propType}')">＋ 記録を追加</button>
      </div>
      ${logs.length === 0
        ? '<div style="padding:10px 0;font-size:12px;color:var(--text-muted);">記録がありません</div>'
        : `<div style="overflow-x:auto;">
             <table class="data-table">
               <thead><tr>
                 <th>日付</th><th>種別</th><th>経路</th><th>検討状況</th><th>メモ</th><th></th>
               </tr></thead>
               <tbody>${rows}</tbody>
             </table>
           </div>`
      }
    </div>`;
}

function openInquiryModal(propId, propType) {
  const today = new Date().toISOString().slice(0, 10);
  const sel   = (id, opts) =>
    `<select id="${id}" class="qs-control">
      ${opts.map(([v,l]) => `<option value="${v}">${l}</option>`).join('')}
    </select>`;

  document.getElementById('modal').innerHTML = `
    <div class="modal-header">
      <div class="modal-title">📞 内見・問い合わせを記録</div>
      <button class="modal-close" onclick="closeModal()">✕</button>
    </div>
    <div class="modal-body">
      <input type="hidden" id="iq-prop-id"   value="${propId}">
      <input type="hidden" id="iq-prop-type" value="${propType}">
      <div class="form-row">
        <div class="form-group">
          <label>日付 *</label>
          <input type="date" id="iq-date" class="qs-control" value="${today}">
        </div>
        <div class="form-group">
          <label>種別 *</label>
          ${sel('iq-type', [['viewing','内見'],['inquiry','問い合わせ']])}
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>経路</label>
          ${sel('iq-route', [['','（未選択）'],['suumo','SUUMO'],['hp','HP'],['sign','売看板'],['referral','紹介'],['other','その他']])}
        </div>
        <div class="form-group">
          <label>検討状況</label>
          ${sel('iq-status', [['','（未選択）'],['considering','検討中'],['positive','前向き'],['declined','見送り'],['contracted','成約']])}
        </div>
      </div>
      <div class="form-row">
        <div class="form-group" style="grid-column:span 2;">
          <label>メモ</label>
          <input type="text" id="iq-memo" class="qs-control" placeholder="顧客の反応・特記事項など">
        </div>
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn-cancel" onclick="closeModal()">キャンセル</button>
      <button class="btn-primary" onclick="saveInquiryLog()">💾 保存</button>
    </div>
  `;
  document.getElementById('modal-bg').classList.remove('hidden');
}

async function saveInquiryLog() {
  const propId   = document.getElementById('iq-prop-id')?.value;
  const propType = document.getElementById('iq-prop-type')?.value;
  const date     = document.getElementById('iq-date')?.value;
  const type     = document.getElementById('iq-type')?.value;
  const route    = document.getElementById('iq-route')?.value  || null;
  const status   = document.getElementById('iq-status')?.value || null;
  const memo     = document.getElementById('iq-memo')?.value.trim() || null;

  if (!date) { toast('日付を入力してください', 'error'); return; }

  const { error } = await db.from('inquiry_logs').insert({
    property_id: propId, property_type: propType, date, type, route, status, memo,
  });
  if (error) { toast('保存失敗: ' + error.message, 'error'); return; }
  toast('記録を保存しました', 'success');
  closeModal();
  if (propType === 'sale')   await renderDetail(propId);
  else                       await renderRentalDetail(propId);
}

async function deleteInquiryLog(id, propId, propType) {
  if (!confirm('この記録を削除しますか？')) return;
  const { error } = await db.from('inquiry_logs').delete().eq('id', id);
  if (error) { toast('削除失敗: ' + error.message, 'error'); return; }
  toast('削除しました', 'success');
  if (propType === 'sale')   await renderDetail(propId);
  else                       await renderRentalDetail(propId);
}
