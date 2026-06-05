// ════════════════════════════════════════════════════════════
// 顧客情報・値下げ履歴・物件マップ v1
// ════════════════════════════════════════════════════════════

// ── Google Maps APIキー（ここに設定してください）──
const GOOGLE_MAPS_API_KEY = '';

// ════════════════════════════════════════════════════════════
// 顧客情報（売主・仲介）
// ════════════════════════════════════════════════════════════

async function showSellerInfo(propId) {
  state.view   = 'seller-info';
  state.propId = propId;
  setActiveNav('');
  await renderSellerInfo(propId);
}

async function renderSellerInfo(propId) {
  const el = document.getElementById('content');
  el.innerHTML = '<div style="padding:40px;text-align:center;color:var(--text-muted);">読み込み中…</div>';

  const { data: prop, error } = await db.from('properties')
    .select('property_name, code, address, seller_info').eq('id', propId).single();
  if (error) { toast('取得失敗: ' + error.message, 'error'); return; }

  const info  = prop.seller_info || {};
  const title = prop.property_name || prop.address || prop.code || '（名称未入力）';

  el.innerHTML = `
    <div class="page-header">
      <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;">
        <button class="btn-back" onclick="showDetail('${propId}')">← 詳細へ</button>
        <div class="page-title">👤 顧客情報 — ${esc(title)}</div>
      </div>
      <button class="btn-primary" onclick="saveSellerInfo('${propId}')">💾 保存</button>
    </div>

    <div class="two-col" style="margin-bottom:16px;">
      <div class="section">
        <div class="section-title">基本情報</div>
        <div class="form-section">氏名・法人</div>
        <div class="form-row">
          <div class="form-group">
            <label>氏名</label>
            <input type="text" id="si-name" class="qs-control" value="${esc(info.name||'')}">
          </div>
          <div class="form-group">
            <label>フリガナ</label>
            <input type="text" id="si-kana" class="qs-control" value="${esc(info.kana||'')}">
          </div>
        </div>
        <div class="form-row">
          <div class="form-group" style="grid-column:span 2;">
            <label>法人名</label>
            <input type="text" id="si-company" class="qs-control" value="${esc(info.company||'')}">
          </div>
        </div>
        <div class="form-section">連絡先</div>
        <div class="form-row">
          <div class="form-group">
            <label>電話番号（自宅）</label>
            <input type="tel" id="si-tel-home" class="qs-control" value="${esc(info.tel_home||'')}">
          </div>
          <div class="form-group">
            <label>電話番号（携帯）</label>
            <input type="tel" id="si-tel-mobile" class="qs-control" value="${esc(info.tel_mobile||'')}">
          </div>
        </div>
        <div class="form-row">
          <div class="form-group" style="grid-column:span 2;">
            <label>メールアドレス</label>
            <input type="email" id="si-email" class="qs-control" value="${esc(info.email||'')}">
          </div>
        </div>
      </div>

      <div class="section">
        <div class="section-title">住所・属性</div>
        <div class="form-section">住所</div>
        <div class="form-row">
          <div class="form-group">
            <label>郵便番号</label>
            <input type="text" id="si-zip" class="qs-control" placeholder="例：992-0045" value="${esc(info.zip||'')}">
          </div>
          <div class="form-group"></div>
        </div>
        <div class="form-row">
          <div class="form-group" style="grid-column:span 2;">
            <label>住所</label>
            <input type="text" id="si-address" class="qs-control" value="${esc(info.address||'')}">
          </div>
        </div>
        <div class="form-section">属性</div>
        <div class="form-row">
          <div class="form-group">
            <label>生年月日</label>
            <input type="date" id="si-dob" class="qs-control" value="${esc(info.dob||'')}">
          </div>
          <div class="form-group">
            <label>職業</label>
            <input type="text" id="si-occupation" class="qs-control" value="${esc(info.occupation||'')}">
          </div>
        </div>
        <div class="form-section">備考</div>
        <div class="form-row">
          <div class="form-group" style="grid-column:span 2;">
            <label>備考・特記事項</label>
            <textarea id="si-notes" class="qs-control" rows="5">${esc(info.notes||'')}</textarea>
          </div>
        </div>
      </div>
    </div>

    <div style="text-align:right;margin-bottom:40px;">
      <button class="btn-primary" onclick="saveSellerInfo('${propId}')" style="min-width:120px;">💾 保存</button>
    </div>
  `;
}

async function saveSellerInfo(propId) {
  const g = id => document.getElementById(id)?.value.trim() || null;
  const info = {
    name:       g('si-name'),
    kana:       g('si-kana'),
    company:    g('si-company'),
    tel_home:   g('si-tel-home'),
    tel_mobile: g('si-tel-mobile'),
    email:      g('si-email'),
    zip:        g('si-zip'),
    address:    g('si-address'),
    dob:        document.getElementById('si-dob')?.value || null,
    occupation: g('si-occupation'),
    notes:      document.getElementById('si-notes')?.value.trim() || null,
  };

  const { error } = await db.from('properties')
    .update({ seller_info: info, updated_at: new Date().toISOString() })
    .eq('id', propId);
  if (error) { toast('保存失敗: ' + error.message, 'error'); return; }
  toast('顧客情報を保存しました', 'success');
  await showDetail(propId);
}

// ════════════════════════════════════════════════════════════
// 値下げ履歴
// ════════════════════════════════════════════════════════════

function openPriceHistoryModal(propId, currentPrice) {
  document.getElementById('modal').innerHTML = `
    <div class="modal-header">
      <div class="modal-title">📉 値下げを記録</div>
      <button class="modal-close" onclick="closeModal()">✕</button>
    </div>
    <div class="modal-body">
      <div class="form-row">
        <div class="form-group">
          <label>変更前の価格（万円）</label>
          <input type="number" id="ph-old" class="qs-control" step="0.01" value="${currentPrice || ''}">
        </div>
        <div class="form-group">
          <label>変更後の価格（万円）</label>
          <input type="number" id="ph-new" class="qs-control" step="0.01">
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>値下げ日</label>
          <input type="date" id="ph-date" class="qs-control" value="${new Date().toISOString().slice(0,10)}">
        </div>
        <div class="form-group">
          <label>メモ</label>
          <input type="text" id="ph-memo" class="qs-control" placeholder="値下げ理由など">
        </div>
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn-cancel" onclick="closeModal()">キャンセル</button>
      <button class="btn-primary" onclick="savePriceHistory('${propId}')">💾 保存</button>
    </div>
  `;
  document.getElementById('modal-bg').classList.remove('hidden');
}

async function savePriceHistory(propId) {
  const oldP = parseFloat(document.getElementById('ph-old')?.value);
  const newP = parseFloat(document.getElementById('ph-new')?.value);
  const date = document.getElementById('ph-date')?.value;
  const memo = document.getElementById('ph-memo')?.value.trim() || null;

  if (!date) { toast('日付を入力してください', 'error'); return; }

  const { error } = await db.from('price_history').insert({
    property_id:   propId,
    old_price:     isNaN(oldP) ? null : oldP,
    new_price:     isNaN(newP) ? null : newP,
    recorded_date: date,
    memo,
  });
  if (error) { toast('保存失敗: ' + error.message, 'error'); return; }

  if (!isNaN(newP) && newP > 0) {
    await db.from('properties')
      .update({ price: newP, updated_at: new Date().toISOString() })
      .eq('id', propId);
  }

  toast('値下げ履歴を保存しました', 'success');
  closeModal();
  await renderDetail(propId);
}

async function deletePriceHistory(id, propId) {
  if (!confirm('この履歴を削除しますか？')) return;
  const { error } = await db.from('price_history').delete().eq('id', id);
  if (error) { toast('削除失敗: ' + error.message, 'error'); return; }
  toast('削除しました', 'success');
  await renderDetail(propId);
}

// ════════════════════════════════════════════════════════════
// 物件マップ
// ════════════════════════════════════════════════════════════

async function showPropertyMap() {
  state.view = 'map';
  setActiveNav('nav-map');
  await renderPropertyMap();
}

async function renderPropertyMap() {
  const el = document.getElementById('content');
  el.innerHTML = `
    <div class="page-header">
      <div>
        <div class="page-title">🗺 物件マップ</div>
        <div class="page-sub">売買・賃貸の全物件をマップで確認できます</div>
      </div>
      ${!GOOGLE_MAPS_API_KEY ? `<div style="font-size:12px;color:var(--red);background:#3a1e1e;padding:6px 12px;border-radius:6px;border:1px solid var(--red);">
        ⚠️ Google Maps APIキーが未設定です。feature_v15.js の GOOGLE_MAPS_API_KEY を設定してください。
      </div>` : ''}
    </div>

    <div class="section" style="padding:10px 16px;margin-bottom:12px;">
      <div style="display:flex;gap:20px;font-size:12px;flex-wrap:wrap;align-items:center;">
        <span style="display:flex;align-items:center;gap:6px;">
          <svg width="14" height="14" viewBox="0 0 14 14"><circle cx="7" cy="7" r="7" fill="#1a73e8"/></svg>
          売買物件
        </span>
        <span style="display:flex;align-items:center;gap:6px;">
          <svg width="14" height="14" viewBox="0 0 14 14"><circle cx="7" cy="7" r="7" fill="#2e9e68"/></svg>
          賃貸物件
        </span>
        <span style="display:flex;align-items:center;gap:6px;">
          <svg width="14" height="14" viewBox="0 0 14 14"><circle cx="7" cy="7" r="7" fill="#888888"/></svg>
          成約済み
        </span>
      </div>
    </div>

    <div id="prop-map" style="width:100%;height:600px;border-radius:12px;border:1px solid var(--border);background:var(--bg-input);display:flex;align-items:center;justify-content:center;">
      <div style="color:var(--text-muted);">読み込み中…</div>
    </div>
  `;

  if (!GOOGLE_MAPS_API_KEY) {
    document.getElementById('prop-map').innerHTML =
      '<div style="color:var(--text-muted);padding:40px;">APIキーを設定してください</div>';
    return;
  }

  const [salesRes, rentalRes] = await Promise.all([
    db.from('properties').select('id, property_name, address, code, type, price, is_sold').order('code'),
    db.from('rental_properties').select('id, property_name, address, code, type, status').order('code'),
  ]);

  const sales   = salesRes.data  || [];
  const rentals = rentalRes.data || [];

  try {
    await loadGoogleMaps();
    initPropertyMapView(sales, rentals);
  } catch(e) {
    document.getElementById('prop-map').innerHTML =
      '<div style="padding:40px;text-align:center;color:var(--red);">Google Maps の読み込みに失敗しました。<br>APIキーとドメイン設定を確認してください。</div>';
  }
}

function loadGoogleMaps() {
  return new Promise((resolve, reject) => {
    if (window.google?.maps?.Map) { resolve(); return; }
    const cbName = '_gmapLoaded' + Date.now();
    window[cbName] = () => { resolve(); delete window[cbName]; };
    const s = document.createElement('script');
    s.src = `https://maps.googleapis.com/maps/api/js?key=${GOOGLE_MAPS_API_KEY}&callback=${cbName}&language=ja`;
    s.async = true;
    s.defer = true;
    s.onerror = () => { reject(new Error('Google Maps load failed')); };
    document.head.appendChild(s);
  });
}

function initPropertyMapView(sales, rentals) {
  const mapEl = document.getElementById('prop-map');
  if (!mapEl) return;

  const map = new google.maps.Map(mapEl, {
    center: { lat: 37.9229, lng: 140.1148 },
    zoom: 13,
    mapTypeControl: true,
    fullscreenControl: true,
  });

  const geocoder = new google.maps.Geocoder();
  const infoWin  = new google.maps.InfoWindow();

  function pinSvg(color) {
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="26" height="38" viewBox="0 0 26 38">
      <path fill="${color}" stroke="rgba(0,0,0,0.3)" stroke-width="1"
            d="M13 0C6.4 0 1 5.4 1 12c0 8 12 26 12 26S25 20 25 12C25 5.4 19.6 0 13 0z"/>
      <circle cx="13" cy="12" r="5.5" fill="white" opacity="0.9"/>
    </svg>`;
    return 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(svg);
  }

  function placeMarker(address, color, infoContent, title) {
    if (!address) return;
    geocoder.geocode({ address: address + ' 日本' }, (results, status) => {
      if (status !== 'OK' || !results?.[0]) return;
      const marker = new google.maps.Marker({
        position: results[0].geometry.location,
        map,
        title,
        icon: { url: pinSvg(color), scaledSize: new google.maps.Size(26, 38), anchor: new google.maps.Point(13, 38) },
      });
      marker.addListener('click', () => {
        infoWin.setContent(`<div style="font-size:13px;line-height:1.7;max-width:240px;padding:4px 0;">${infoContent}</div>`);
        infoWin.open(map, marker);
      });
    });
  }

  sales.forEach(p => {
    const isSold  = !!p.is_sold;
    const color   = isSold ? '#888888' : '#1a73e8';
    const name    = esc(p.property_name || p.address || p.code || '（名称未入力）');
    const type    = p.type === 'land' ? '土地' : '中古住宅';
    const priceStr = p.price ? p.price.toLocaleString() + '万円' : '—';
    const statusStr = isSold ? '<span style="color:#888;">成約済み</span>' : '掲載中';
    const content  = `<strong>${name}</strong><br>${type} ／ ${statusStr}<br>価格: ${priceStr}
      <br><a href="#" onclick="showDetail('${p.id}');return false;" style="color:#1a73e8;font-weight:600;">詳細を見る →</a>`;
    placeMarker(p.address, color, content, p.property_name || p.code || '');
  });

  rentals.forEach(p => {
    const color   = '#2e9e68';
    const name    = esc(p.property_name || p.address || p.code || '（名称未入力）');
    const type    = { land:'土地', house:'住宅', building:'ビル' }[p.type] || p.type;
    const stat    = { recruiting:'募集中', occupied:'入居中', vacant:'空室', leaving:'退去予定', closed:'管理終了' }[p.status] || '';
    const content = `<strong>${name}</strong><br>賃貸 ${type} ／ ${stat}
      <br><a href="#" onclick="showRentalDetail('${p.id}');return false;" style="color:#2e9e68;font-weight:600;">詳細を見る →</a>`;
    placeMarker(p.address, color, content, p.property_name || p.code || '');
  });
}
