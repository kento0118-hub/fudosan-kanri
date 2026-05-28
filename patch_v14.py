import os, re

base      = os.path.dirname(os.path.abspath(__file__))
html_path = os.path.join(base, 'index.html')
js_path   = os.path.join(base, 'rental_v1.js')

with open(html_path, 'rb') as f:
    raw = f.read()
crlf = b'\r\n' in raw
text = raw.decode('utf-8').replace('\r\n', '\n')

with open(js_path, 'rb') as f:
    rental_js = f.read().decode('utf-8').replace('\r\n', '\n')

# ── 1. CSS: 賃貸バッジを badge-negotiating の後に追加 ──────────────────────
old_css = "    .badge-negotiating{ font-size: 10px; background: #e67e00; color: #ffffff;       padding: 2px 8px; border-radius: 6px; font-weight: 600; white-space: nowrap; }"
new_css = old_css + """
    .badge-recruiting{ font-size: 10px; background: #1a3a6e; color: #6ea8fe;       padding: 2px 8px; border-radius: 6px; font-weight: 600; white-space: nowrap; }
    .badge-occupied  { font-size: 10px; background: #1a3a1e; color: var(--green);  padding: 2px 8px; border-radius: 6px; font-weight: 600; white-space: nowrap; }
    .badge-vacant    { font-size: 10px; background: #2a2d35; color: var(--text-muted); padding: 2px 8px; border-radius: 6px; font-weight: 600; white-space: nowrap; }
    .badge-leaving   { font-size: 10px; background: #e67e00; color: #ffffff;       padding: 2px 8px; border-radius: 6px; font-weight: 600; white-space: nowrap; }
    .badge-r-closed  { font-size: 10px; background: #cc0000; color: #ffffff;       padding: 2px 8px; border-radius: 6px; font-weight: 600; white-space: nowrap; }
    .badge-building  { font-size: 10px; background: #2a1a5e; color: #b39ddb;       padding: 2px 8px; border-radius: 6px; font-weight: 600; white-space: nowrap; }"""
if old_css not in text:
    raise RuntimeError('badge-negotiating CSS が見つかりません')
text = text.replace(old_css, new_css, 1)
print('1. CSS バッジ追加 OK')

# ── 2. nav: 物件一覧 → 売買 ─────────────────────────────────────────────────
old_nav_list = '    <a class="nav-item" id="nav-list" onclick="showList()" href="#">\n      <span class="icon">🏠</span>物件一覧\n    </a>'
new_nav_list = '    <a class="nav-item" id="nav-list" onclick="showList()" href="#">\n      <span class="icon">🏠</span>売買\n    </a>'
if old_nav_list not in text:
    raise RuntimeError('nav-list が見つかりません')
text = text.replace(old_nav_list, new_nav_list, 1)
print('2. 物件一覧→売買 OK')

# ── 3. nav: 記録台帳 → 売買台帳 + 賃貸・修繕台帳を追加 ──────────────────────
old_nav_logs = '    <a class="nav-item" id="nav-logs" onclick="showLogs()" href="#">\n      <span class="icon">📋</span>記録台帳\n    </a>'
new_nav_logs = ('    <a class="nav-item" id="nav-logs" onclick="showLogs()" href="#">\n'
                '      <span class="icon">📋</span>売買台帳\n'
                '    </a>\n'
                '    <a class="nav-item" id="nav-rental" onclick="showRentalList()" href="#">\n'
                '      <span class="icon">🏢</span>賃貸\n'
                '    </a>\n'
                '    <a class="nav-item" id="nav-repair" onclick="showRepairLog()" href="#">\n'
                '      <span class="icon">🔧</span>修繕台帳\n'
                '    </a>')
if old_nav_logs not in text:
    raise RuntimeError('nav-logs が見つかりません')
text = text.replace(old_nav_logs, new_nav_logs, 1)
print('3. ナビ追加 OK')

# ── 4. state に賃貸用プロパティを追加 ─────────────────────────────────────────
old_state = ("let state = {\n"
             "  view:           'list',\n"
             "  propId:         null,\n"
             "  filterType:     'all',\n"
             "  filterSold:     false,\n"
             "  checklistItems: [],\n"
             "  logsFilter:     '',\n"
             "  detailYear:     new Date().getFullYear(),\n"
             "};")
new_state = ("let state = {\n"
             "  view:             'list',\n"
             "  propId:           null,\n"
             "  filterType:       'all',\n"
             "  filterSold:       false,\n"
             "  checklistItems:   [],\n"
             "  logsFilter:       '',\n"
             "  detailYear:       new Date().getFullYear(),\n"
             "  rentalId:         null,\n"
             "  rentalFilterType: 'all',\n"
             "};")
if old_state not in text:
    raise RuntimeError('state オブジェクトが見つかりません')
text = text.replace(old_state, new_state, 1)
print('4. state 追加 OK')

# ── 5. rental_v1.js を最後の </script> の直前に挿入 ────────────────────────
last_script = text.rfind('</script>')
if last_script == -1:
    raise RuntimeError('</script> が見つかりません')
text = text[:last_script] + rental_js.rstrip('\n') + '\n\n' + text[last_script:]
print('5. rental_v1.js 挿入 OK')

# ── 書き戻し ──────────────────────────────────────────────────────────────
if crlf:
    text = text.replace('\n', '\r\n')
with open(html_path, 'wb') as f:
    f.write(text.encode('utf-8'))

print('patch_v14 完了')
