#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Markdown → 互动阅读 HTML（GitBook 风：左目录 + 右正文，内联 CSS，无 JS）。
   仅做呈现转换，不改内容、不改数字。"""
import re, os, html, sys

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(D, 'LF1_数据采集与标注_课程标准_正式版.md')
OUT = os.path.join(D, 'LF1_数据采集与标注_课程标准_正式版.html')

def slug(t):
    s = re.sub(r'[^\w\u4e00-\u9fff]+', '-', t).strip('-')
    return s or 'sec'

def inline(s):
    s = html.escape(s)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<em>\1</em>', s)
    s = re.sub(r'~~([^~]+)~~', r'<del>\1</del>', s)
    s = s.replace('→', ' → ').replace('≥', '≥').replace('≤', '≤')
    return s

def build(txt):
    lines = txt.splitlines()
    body, toc = [], []
    i, n = 0, len(lines)
    hid = {}
    while i < n:
        l = lines[i]
        if l.startswith('```'):
            i += 1; buf = []
            while i < n and not lines[i].startswith('```'):
                buf.append(lines[i]); i += 1
            body.append('<pre class="code">' + html.escape('\n'.join(buf)) + '</pre>'); i += 1; continue
        m = re.match(r'^(#{1,6})\s+(.*)$', l)
        if m:
            lvl, txt2 = len(m.group(1)), m.group(2).strip()
            anchor = slug(txt2)
            while anchor in hid: hid[anchor] += 1; anchor = anchor + '-' + str(hid[anchor])
            hid[anchor] = 0
            if lvl <= 3: toc.append((lvl, txt2, anchor))
            cls = {1: 'h1', 2: 'h2', 3: 'h3'}.get(lvl, 'h4')
            body.append(f'<h{lvl} id="{anchor}" class="{cls}">{inline(txt2)}</h{lvl}>')
            i += 1; continue
        if l.strip().startswith('|') and i + 1 < n and re.match(r'^\s*\|[\s\-:|]+\|\s*$', lines[i + 1]):
            head = [c.strip() for c in l.strip().strip('|').split('|')]
            i += 2; rows = []
            while i < n and lines[i].strip().startswith('|'):
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')]); i += 1
            t = ['<div class="tw"><table><thead><tr>']
            t += [f'<th>{inline(c)}</th>' for c in head]
            t.append('</tr></thead><tbody>')
            for r in rows:
                t.append('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>')
            t.append('</tbody></table></div>')
            body.append(''.join(t)); continue
        if re.match(r'^\s*[-*]\s+', l):
            items = []
            while i < n and re.match(r'^\s*[-*]\s+', lines[i]):
                items.append(re.sub(r'^\s*[-*]\s+', '', lines[i])); i += 1
            body.append('<ul>' + ''.join(f'<li>{inline(x)}</li>' for x in items) + '</ul>'); continue
        if re.match(r'^\s*\d+\.\s+', l):
            items = []
            while i < n and re.match(r'^\s*\d+\.\s+', lines[i]):
                items.append(re.sub(r'^\s*\d+\.\s+', '', lines[i])); i += 1
            body.append('<ol>' + ''.join(f'<li>{inline(x)}</li>' for x in items) + '</ol>'); continue
        if l.strip().startswith('>'):
            buf = []
            while i < n and lines[i].strip().startswith('>'):
                buf.append(lines[i].strip().lstrip('>').strip()); i += 1
            body.append('<blockquote>' + '<br>'.join(inline(x) for x in buf if x) + '</blockquote>'); continue
        if re.match(r'^\s*---+\s*$', l):
            body.append('<hr>'); i += 1; continue
        if not l.strip():
            i += 1; continue
        body.append(f'<p>{inline(l)}</p>'); i += 1
    return '\n'.join(body), toc

md = open(SRC, encoding='utf-8').read()
body, toc = build(md)
title = md.splitlines()[0].lstrip('# ').strip()

CSS = """
:root{--bg:#f7f8fa;--card:#fff;--ink:#1f2430;--ink2:#4a5261;--line:#e3e6ec;--acc:#1f5fa9;--acc2:#eaf1fa;--warn:#b3261e}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.75 -apple-system,"PingFang SC","Microsoft YaHei",sans-serif}
.top{position:sticky;top:0;z-index:9;background:linear-gradient(90deg,#1f5fa9,#2f7ac4);color:#fff;padding:10px 18px;font-size:13px;display:flex;gap:14px;align-items:center;flex-wrap:wrap}
.top b{font-weight:600}
.top span{opacity:.9}
.layout{display:flex;align-items:flex-start;max-width:1400px;margin:0 auto}
nav{position:sticky;top:44px;width:290px;flex:none;height:calc(100vh - 44px);overflow:auto;border-right:1px solid var(--line);background:var(--card);padding:14px 10px 40px}
nav h4{margin:6px 8px 10px;font-size:12px;color:var(--ink2);letter-spacing:.08em}
nav a{display:block;padding:5px 10px;border-radius:6px;color:var(--ink2);text-decoration:none;font-size:13px;line-height:1.5}
nav a.l1{font-weight:600;color:var(--ink);margin-top:8px}
nav a.l2{padding-left:20px}
nav a.l3{padding-left:32px;font-size:12.5px;color:#7a8290}
nav a:hover{background:var(--acc2);color:var(--acc)}
main{flex:1;min-width:0;padding:26px 30px 80px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:6px 26px 22px;margin:0 0 22px}
h1{font-size:25px;margin:18px 0 14px;padding-bottom:12px;border-bottom:2px solid var(--acc)}
h2{font-size:20px;margin:26px 0 12px;padding-left:11px;border-left:4px solid var(--acc)}
h3{font-size:16.5px;margin:20px 0 9px;color:#243}
h4{font-size:15px;margin:15px 0 7px;color:var(--ink2)}
p{margin:9px 0}
ul,ol{margin:8px 0 8px 20px;padding:0}
li{margin:4px 0}
strong{color:#0d1b2e}
code{background:#eef1f6;border:1px solid #e0e4ec;border-radius:4px;padding:1px 5px;font-size:13px;color:#b3261e}
pre.code{background:#1f2430;color:#e6eaf2;padding:14px 16px;border-radius:8px;overflow:auto;font-size:13px;line-height:1.6}
blockquote{margin:10px 0;padding:9px 14px;background:var(--acc2);border-left:4px solid var(--acc);border-radius:0 6px 6px 0;color:#25364d;font-size:14px}
hr{border:0;border-top:1px solid var(--line);margin:20px 0}
.tw{overflow-x:auto;margin:12px 0;border:1px solid var(--line);border-radius:8px;background:#fff}
table{border-collapse:collapse;width:100%;font-size:13px}
th,td{border-bottom:1px solid var(--line);border-right:1px solid var(--line);padding:7px 9px;text-align:left;vertical-align:top}
th{background:#eef3fa;font-weight:600;color:#1b3a63;white-space:nowrap;position:sticky;top:0}
tr:nth-child(even) td{background:#fafbfd}
td:last-child,th:last-child{border-right:0}
table tr:last-child td{border-bottom:0}
@media(max-width:900px){nav{display:none}.layout{display:block}main{padding:16px}}
@media print{body{background:#fff}nav,.top{display:none}.card{border:0;padding:0}h2{page-break-after:avoid}tr{page-break-inside:avoid}}
"""

nav_html = ['<nav><h4>目录</h4>']
for lvl, t, a in toc:
    nav_html.append(f'<a class="l{min(lvl,3)}" href="#{a}">{html.escape(re.sub(r"[`*]","",t))}</a>')
nav_html.append('</nav>')

doc = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><style>{CSS}</style></head>
<body>
<div class="top"><b>6×4 分层教案配套 · 课程标准</b><span>人工智能数据工程技术（510217）· 重庆现代制造职业学院</span><span>LF1 数据采集与标注 · V1.0 · 11 章正式版</span><span>标准未发布·仅作校本标准</span></div>
<div class="layout">
{''.join(nav_html)}
<main><div class="card">
{body}
</div></main></div>
</body></html>"""

open(OUT, 'w', encoding='utf-8').write(doc)
print(f'✅ 生成 {OUT}')
print(f'   大小 {len(doc)/1024:.1f} KB｜目录条目 {len(toc)}｜脚本依赖 {"无" if "<script" not in doc else "有"}')
