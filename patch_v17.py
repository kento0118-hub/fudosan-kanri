"""
patch_v17.py — レスポンシブデザイン対応
実行: python patch_v17.py
"""
import sys, os

SRC = 'index.html'

with open(SRC, 'rb') as f:
    raw = f.read()

text = raw.replace(b'\r\n', b'\n').decode('utf-8')
original = text

# ════════════════════════════════════════════
# Step 1: レスポンシブ CSS を </style> 直前に挿入
# ════════════════════════════════════════════
RESPONSIVE_CSS = """\
    /* ══ ハンバーガーメニュー ══ */
    .hamburger {
      display: none;
      position: fixed;
      top: 12px; left: 12px;
      z-index: 200;
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 8px;
      width: 44px; height: 44px;
      font-size: 20px;
      cursor: pointer;
      align-items: center; justify-content: center;
      box-shadow: 0 2px 8px rgba(0,0,0,.15);
      padding: 0; line-height: 1; color: var(--text-primary);
    }
    .sidebar-overlay {
      position: fixed; inset: 0;
      background: rgba(0,0,0,.5);
      z-index: 90;
      display: none;
    }
    .sidebar-overlay.open { display: block; }

    /* ══ プロパティカード（スマホ用一覧） ══ */
    .list-cards-wrap { display: none; }
    .prop-card {
      padding: 14px 16px;
      border-bottom: 1px solid var(--border);
      cursor: pointer;
      transition: background .15s;
    }
    .prop-card:last-child { border-bottom: none; }
    .prop-card:active { background: var(--bg-card-hover); }
    .prop-card-top {
      display: flex; align-items: center; gap: 8px; margin-bottom: 4px;
    }
    .prop-card-code {
      font-size: 11px; color: var(--text-muted); font-weight: 600;
    }
    .prop-card-name {
      font-size: 14px; font-weight: 600; color: var(--text-primary);
      margin-bottom: 6px;
      overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
    }
    .prop-card-row {
      display: flex; align-items: baseline; gap: 12px; margin-bottom: 6px;
    }
    .prop-card-price {
      font-size: 15px; font-weight: 700; color: var(--accent);
    }
    .prop-card-area { font-size: 12px; color: var(--text-secondary); }
    .prop-card-status {
      display: flex; align-items: center; gap: 6px; flex-wrap: wrap;
    }

    /* ══ レスポンシブ：スマホ（～767px） ══ */
    @media (max-width: 767px) {
      .hamburger { display: flex; }
      .sidebar {
        transform: translateX(-100%);
        transition: transform .25s ease;
        z-index: 150;
      }
      .sidebar.open { transform: translateX(0); }
      .main {
        margin-left: 0 !important;
        padding: 68px 14px 24px;
      }
      .page-title { font-size: 17px; }
      .page-header { flex-direction: column; gap: 10px; }
      .filter-tabs { flex-wrap: wrap; }
      .filter-tab { min-height: 36px; }
      .form-row { grid-template-columns: 1fr !important; }
      .two-col { grid-template-columns: 1fr; }
      .photo-grid { grid-template-columns: repeat(2, 1fr); }
      .doc-checkboxes { grid-template-columns: 1fr; }
      .btn-primary, .btn-secondary, .btn-cancel, .btn-back {
        min-height: 44px;
        padding: 10px 16px;
        font-size: 14px;
      }
      .btn-sm { min-height: 36px; padding: 6px 10px; }
      .modal-bg { align-items: flex-end; padding: 0; }
      .modal {
        max-width: 100%;
        border-radius: 16px 16px 0 0;
        max-height: 92vh;
      }
      .section { padding: 14px; }
      .list-cards-wrap { display: block; }
      .list-table-wrap { display: none; }
      .qs-control { font-size: 16px; }
      .info-table th { width: 90px; }
      .page-sub { font-size: 12px; }
    }

    /* ══ レスポンシブ：タブレット（768px～1023px） ══ */
    @media (min-width: 768px) and (max-width: 1023px) {
      :root { --sidebar-w: 180px; }
      .main { padding: 24px 20px; }
    }
"""

find1 = (
    '    .setup-card code {\n'
    '      display: block; background: var(--bg-input);\n'
    '      border: 1px solid var(--border); border-radius: 6px;\n'
    '      padding: 12px 14px; font-size: 12px; font-family: monospace;\n'
    '      color: var(--accent); margin-bottom: 16px; word-break: break-all;\n'
    '    }\n'
    '  </style>'
)
repl1 = (
    '    .setup-card code {\n'
    '      display: block; background: var(--bg-input);\n'
    '      border: 1px solid var(--border); border-radius: 6px;\n'
    '      padding: 12px 14px; font-size: 12px; font-family: monospace;\n'
    '      color: var(--accent); margin-bottom: 16px; word-break: break-all;\n'
    '    }\n'
    + RESPONSIVE_CSS +
    '  </style>'
)
if find1 not in text:
    print('Step 1 FAILED: marker not found'); sys.exit(1)
text = text.replace(find1, repl1, 1)
print('Step 1 OK: レスポンシブCSS追加')

# ════════════════════════════════════════════
# Step 2: ハンバーガーボタン追加 + aside に id="sidebar"
# ════════════════════════════════════════════
find2 = '<!-- ========== サイドバー ========== -->\n<aside class="sidebar">'
repl2 = (
    '<button class="hamburger" id="hamburger" onclick="toggleSidebar()">&#9776;</button>\n'
    '<!-- ========== サイドバー ========== -->\n'
    '<aside class="sidebar" id="sidebar">'
)
if find2 not in text:
    print('Step 2 FAILED: marker not found'); sys.exit(1)
text = text.replace(find2, repl2, 1)
print('Step 2 OK: ハンバーガーボタン追加')

# ════════════════════════════════════════════
# Step 3: サイドバーオーバーレイ追加（</aside>の後）
# ════════════════════════════════════════════
find3 = '</aside>\n\n<!-- ========== メインコンテンツ ========== -->'
repl3 = (
    '</aside>\n'
    '<div class="sidebar-overlay" id="sidebar-overlay" onclick="toggleSidebar()"></div>\n\n'
    '<!-- ========== メインコンテンツ ========== -->'
)
if find3 not in text:
    print('Step 3 FAILED: marker not found'); sys.exit(1)
text = text.replace(find3, repl3, 1)
print('Step 3 OK: サイドバーオーバーレイ追加')

# ════════════════════════════════════════════
# Step 4: setActiveNav でスマホ時にサイドバーを閉じる
# ════════════════════════════════════════════
find4 = (
    'function setActiveNav(id) {\n'
    '  document.querySelectorAll(\'.nav-item\').forEach(el => {\n'
    '    el.classList.toggle(\'active\', el.id === id);\n'
    '  });\n'
    '}'
)
repl4 = (
    'function setActiveNav(id) {\n'
    '  document.querySelectorAll(\'.nav-item\').forEach(el => {\n'
    '    el.classList.toggle(\'active\', el.id === id);\n'
    '  });\n'
    '  if (window.innerWidth < 768) {\n'
    '    const s = document.getElementById(\'sidebar\');\n'
    '    const o = document.getElementById(\'sidebar-overlay\');\n'
    '    if (s) s.classList.remove(\'open\');\n'
    '    if (o) o.classList.remove(\'open\');\n'
    '  }\n'
    '}'
)
if find4 not in text:
    print('Step 4 FAILED: marker not found'); sys.exit(1)
text = text.replace(find4, repl4, 1)
print('Step 4 OK: setActiveNav修正')

# ════════════════════════════════════════════
# Step 5: toggleSidebar 関数を追加
# ════════════════════════════════════════════
find5 = (
    '// ════════════════════════════════════════════════════════════\n'
    '// 物件一覧ビュー\n'
    '// ════════════════════════════════════════════════════════════'
)
repl5 = (
    'function toggleSidebar() {\n'
    '  const s = document.getElementById(\'sidebar\');\n'
    '  const o = document.getElementById(\'sidebar-overlay\');\n'
    '  if (!s) return;\n'
    '  const open = s.classList.toggle(\'open\');\n'
    '  if (o) o.classList.toggle(\'open\', open);\n'
    '}\n\n'
    '// ════════════════════════════════════════════════════════════\n'
    '// 物件一覧ビュー\n'
    '// ════════════════════════════════════════════════════════════'
)
if find5 not in text:
    print('Step 5 FAILED: marker not found'); sys.exit(1)
text = text.replace(find5, repl5, 1)
print('Step 5 OK: toggleSidebar関数追加')

# ════════════════════════════════════════════
# Step 6: renderList でカードラッパーを追加
# ════════════════════════════════════════════
find6 = (
    '      : `<div class="section" style="padding:0;overflow:hidden;">\n'
    '           <div style="overflow-x:auto;">${buildListTable(displayed)}</div>\n'
    '         </div>`\n'
    '    }'
)
repl6 = (
    '      : `<div class="section" style="padding:0;overflow:hidden;">\n'
    '           <div class="list-table-wrap" style="overflow-x:auto;">${buildListTable(displayed)}</div>\n'
    '           <div class="list-cards-wrap">${buildListCards(displayed)}</div>\n'
    '         </div>`\n'
    '    }'
)
if find6 not in text:
    print('Step 6 FAILED: marker not found'); sys.exit(1)
text = text.replace(find6, repl6, 1)
print('Step 6 OK: カードラッパー追加')

# ════════════════════════════════════════════
# Step 7: buildListCards 関数を buildListTable の後に追加
# ════════════════════════════════════════════
BUILD_LIST_CARDS = """\

function buildListCards(props) {
  return props.map(p => {
    const d   = p.property_details || {};
    const iq  = p._iq || {};
    const iqText = (iq.v || iq.i)
      ? (iq.v ? '内見' + iq.v : '') + (iq.v && iq.i ? ' / ' : '') + (iq.i ? '問合 ' + iq.i : '')
      : '';
    const areaText = p.type === 'land'
      ? (d.area_tsubo ? d.area_tsubo + '坪' : '—')
      : (d.land_area_tsubo ? d.land_area_tsubo + '坪' : '—');
    const typeBadge = p.type === 'land'
      ? '<span class="badge-land">土地</span>'
      : '<span class="badge-house">中古住宅</span>';
    const listed = [
      d.suumo_listed  ? '<span class="badge-suumo">SUUMO</span>' : '',
      d.hp_listed     ? '<span class="badge-hp">HP掲載</span>' : '',
      d.for_sale_sign ? '<span class="badge-sign">売看板</span>' : '',
      iqText          ? `<span style="font-size:10px;color:var(--text-secondary);">${iqText}</span>` : '',
    ].filter(Boolean).join('');
    return `<div class="prop-card" onclick="showDetail('${p.id}')">
      <div class="prop-card-top">
        <span class="prop-card-code">${esc(p.code||'')}</span>
        ${typeBadge}
        ${statusBadge(p.status)}
      </div>
      <div class="prop-card-name">${esc(p.property_name||p.address||'(名称未入力)')}</div>
      <div class="prop-card-row">
        <span class="prop-card-price">${p.price ? p.price.toLocaleString()+'万円' : '—'}</span>
        <span class="prop-card-area">${areaText}</span>
      </div>
      ${listed ? `<div class="prop-card-status">${listed}</div>` : ''}
    </div>`;
  }).join('');
}
"""

find7 = (
    '// ════════════════════════════════════════════════════════════\n'
    '// 物件詳細ビュー\n'
    '// ════════════════════════════════════════════════════════════'
)
repl7 = BUILD_LIST_CARDS + (
    '// ════════════════════════════════════════════════════════════\n'
    '// 物件詳細ビュー\n'
    '// ════════════════════════════════════════════════════════════'
)
if find7 not in text:
    print('Step 7 FAILED: marker not found'); sys.exit(1)
text = text.replace(find7, repl7, 1)
print('Step 7 OK: buildListCards関数追加')

# ════════════════════════════════════════════
# 書き出し
# ════════════════════════════════════════════
if text == original:
    print('ERROR: no changes made'); sys.exit(1)

out = text.replace('\n', '\r\n').encode('utf-8')
with open(SRC, 'wb') as f:
    f.write(out)
print('\nAll steps OK — index.html updated')
