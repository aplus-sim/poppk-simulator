"""
Markdown → 단일 HTML 변환기 (외부 의존성 없음).

.md 파일은 Windows에서 더블클릭으로 안 열리므로, 브라우저에서 바로 열리는
스타일 적용된 HTML로 변환한다.

    python md2html.py PRD.md              -> PRD.html
    python md2html.py 개선점_트래커.md     -> 개선점_트래커.html
"""
import re, sys, os, html as _html

CSS = """
:root{--fg:#1f2328;--muted:#656d76;--accent:#1f4e79;--border:#d0d7de;--bg:#fff;--code:#f6f8fa}
*{box-sizing:border-box}
body{margin:0;background:#f3f4f6;color:var(--fg);
 font-family:"Malgun Gothic","Segoe UI",system-ui,-apple-system,sans-serif;line-height:1.7}
.wrap{max-width:900px;margin:0 auto;padding:48px 56px;background:var(--bg);min-height:100vh;
 box-shadow:0 0 24px rgba(0,0,0,.06)}
h1{font-size:28px;margin:32px 0 12px;color:var(--accent);border-bottom:2px solid var(--accent);padding-bottom:8px}
h1:first-child{margin-top:0}
h2{font-size:21px;margin:28px 0 10px;color:var(--accent)}
h3{font-size:17px;margin:22px 0 8px}
p{margin:10px 0}
ul,ol{margin:10px 0;padding-left:26px}
li{margin:4px 0}
table{border-collapse:collapse;width:100%;margin:14px 0;font-size:14px}
th,td{border:1px solid var(--border);padding:7px 10px;text-align:left;vertical-align:top}
th{background:#eef2f7;font-weight:600}
tr:nth-child(even) td{background:#fafbfc}
code{background:var(--code);padding:1.5px 5px;border-radius:4px;font-size:13px;
 font-family:Consolas,"Courier New",monospace}
pre{background:var(--code);padding:14px 16px;border-radius:8px;overflow-x:auto;border:1px solid var(--border)}
pre code{background:none;padding:0;font-size:13px;line-height:1.55}
blockquote{margin:14px 0;padding:10px 16px;border-left:4px solid var(--accent);
 background:#f6f8fa;color:var(--muted)}
hr{border:0;border-top:1px solid var(--border);margin:28px 0}
a{color:var(--accent)}
@media print{body{background:#fff}.wrap{box-shadow:none;padding:0;max-width:none}}
"""

def inline(s):
    s = _html.escape(s)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', s)
    return s

BLOCK_START = re.compile(r'^\s*(#{1,6}\s|[-*]\s|\d+\.\s|\||>|```|---+\s*$)')

def convert(md):
    lines = md.split('\n')
    out, i, in_code, code_buf = [], 0, False, []
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith('```'):
            if not in_code:
                in_code, code_buf = True, []
            else:
                in_code = False
                out.append('<pre><code>' + _html.escape('\n'.join(code_buf)) + '</code></pre>')
            i += 1; continue
        if in_code:
            code_buf.append(line); i += 1; continue

        # 표
        if line.strip().startswith('|') and i + 1 < len(lines) and re.match(r'^\s*\|[\s:|-]+\|\s*$', lines[i+1]):
            head = [c.strip() for c in line.strip().strip('|').split('|')]
            i += 2
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')]); i += 1
            t = '<table><thead><tr>' + ''.join(f'<th>{inline(c)}</th>' for c in head) + '</tr></thead><tbody>'
            for r in rows:
                t += '<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>'
            out.append(t + '</tbody></table>'); continue

        m = re.match(r'^(#{1,6})\s+(.*)$', line)
        if m:
            lv = len(m.group(1))
            out.append(f'<h{lv}>{inline(m.group(2))}</h{lv}>'); i += 1; continue

        if re.match(r'^\s*---+\s*$', line):
            out.append('<hr>'); i += 1; continue

        if line.strip().startswith('>'):
            buf = []
            while i < len(lines) and lines[i].strip().startswith('>'):
                buf.append(lines[i].strip().lstrip('>').strip()); i += 1
            out.append('<blockquote>' + inline(' '.join(buf)) + '</blockquote>'); continue

        if re.match(r'^\s*[-*]\s+', line) or re.match(r'^\s*\d+\.\s+', line):
            ordered = bool(re.match(r'^\s*\d+\.\s+', line))
            items = []
            while i < len(lines) and (re.match(r'^\s*[-*]\s+', lines[i]) or re.match(r'^\s*\d+\.\s+', lines[i])):
                items.append('<li>' + inline(re.sub(r'^\s*(?:[-*]|\d+\.)\s+', '', lines[i])) + '</li>'); i += 1
            tag = 'ol' if ordered else 'ul'
            out.append(f'<{tag}>' + ''.join(items) + f'</{tag}>'); continue

        if not line.strip():
            i += 1; continue

        buf = [line]; i += 1
        while i < len(lines) and lines[i].strip() and not BLOCK_START.match(lines[i]):
            buf.append(lines[i]); i += 1
        out.append('<p>' + inline(' '.join(buf)) + '</p>')
    return '\n'.join(out)

def main():
    if len(sys.argv) < 2:
        print(__doc__); return
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(src)[0] + '.html'
    md = open(src, encoding='utf-8').read()
    title = os.path.splitext(os.path.basename(src))[0]
    body = convert(md)
    page = (f'<!DOCTYPE html>\n<html lang="ko">\n<head>\n<meta charset="UTF-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            f'<title>{_html.escape(title)}</title>\n<style>{CSS}</style>\n</head>\n'
            f'<body>\n<div class="wrap">\n{body}\n</div>\n</body>\n</html>\n')
    open(dst, 'w', encoding='utf-8').write(page)
    print(f'OK: {dst} ({len(page):,} bytes)')

if __name__ == '__main__':
    main()
