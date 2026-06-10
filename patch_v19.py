"""
patch_v19.py — codeSort を区画グループ対応に更新
実行: python patch_v19.py
"""
import sys

SRC = 'index.html'
with open(SRC, 'rb') as f:
    raw = f.read()
text = raw.replace(b'\r\n', b'\n').decode('utf-8')
original = text

find = (
    '  const codeSort = arr => [...arr].sort((a, b) => {\n'
    '    const ORDER = { B: 0, T: 1, C: 2 };\n'
    '    const letter = p => (p?.code || \'\').charAt(0).toUpperCase();\n'
    '    const num    = p => parseInt((p?.code || \'\').replace(/^[^\\d]+/, \'\')) || 0;\n'
    '    const la = ORDER[letter(a)] ?? 3, lb = ORDER[letter(b)] ?? 3;\n'
    '    if (la !== lb) return la - lb;\n'
    '    if (num(a) !== num(b)) return num(a) - num(b);\n'
    '    const lotNum = p => { const m = (p?.property_name || \'\').match(/(\\d+)\\s*$/); return m ? parseInt(m[1]) : 0; };\n'
    '    return lotNum(a) - lotNum(b);\n'
    '  });'
)

repl = """\
  const codeSort = arr => {
    const ORDER = { B: 0, T: 1, C: 2 };
    const letter  = p => (p?.code || '').charAt(0).toUpperCase();
    const codeNum = p => parseInt((p?.code || '').replace(/^[^\\d]+/, '')) || 0;
    // 全角数字を半角に変換
    const toHalf  = s => s.replace(/[\\uFF10-\\uFF19]/g, c => String.fromCharCode(c.charCodeAt(0) - 0xFEE0));
    // 「区画N」の番号を抽出（全角・半角対応）
    const getKukaku = p => {
      const m = toHalf(p?.property_name || '').match(/\\u533a\\u753b\\s*(\\d+)/);
      return m ? parseInt(m[1]) : null;
    };
    // ベース名（「区画N」を除いた部分）
    const baseName = p => toHalf(p?.property_name || '').replace(/\\s*\\u533a\\u753b\\s*\\d+\\s*$/, '').trim();

    // 区画グループごとの代表コード（グループ内最小コード順）を事前計算
    const groups = {};
    arr.forEach(p => {
      if (getKukaku(p) === null) return;
      const bn = baseName(p);
      const gl = ORDER[letter(p)] ?? 3, gn = codeNum(p);
      if (!groups[bn] || gl < groups[bn].l || (gl === groups[bn].l && gn < groups[bn].n)) {
        groups[bn] = { l: gl, n: gn };
      }
    });

    // ソートキーを生成：区画あり → グループ代表コード + ベース名 + 区画番号
    //                  区画なし → コード文字 + コード番号 + 物件名
    const key = p => {
      const kk = getKukaku(p);
      if (kk !== null) {
        const bn = baseName(p);
        const g  = groups[bn];
        return [g.l, g.n, bn, kk];
      }
      return [ORDER[letter(p)] ?? 3, codeNum(p), p?.property_name || '', 0];
    };

    return [...arr].sort((a, b) => {
      const ka = key(a), kb = key(b);
      for (let i = 0; i < 4; i++) {
        if (ka[i] < kb[i]) return -1;
        if (ka[i] > kb[i]) return  1;
      }
      return 0;
    });
  };\
"""

if find not in text:
    print('FAILED: marker not found'); sys.exit(1)
text = text.replace(find, repl, 1)

if text == original:
    print('ERROR: no change'); sys.exit(1)

out = text.replace('\n', '\r\n').encode('utf-8')
with open(SRC, 'wb') as f:
    f.write(out)
print('OK')
