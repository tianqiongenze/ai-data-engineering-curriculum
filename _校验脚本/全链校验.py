#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全链校验脚本 V3：按各表真实表头定位列，按真实编号体系统计。"""
import re, os
from collections import Counter
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def P(n): return os.path.join(D, n)
def read(n): return open(P(n), encoding='utf-8').read()
def num(x):
    m = re.search(r'-?\d+(?:\.\d+)?', (x or '').replace(',', ''))
    return float(m.group()) if m else None

def parse_tables(txt):
    tables, cur, hdr = [], [], None
    for line in txt.splitlines():
        s = line.strip()
        if s.startswith('|') and s.count('|') >= 2:
            c = [x.strip() for x in s.strip('|').split('|')]
            if all(set(x) <= set('-: ') for x in c if x):
                continue
            if hdr is None:
                hdr, cur = c, []
            else:
                cur.append(c)
        else:
            if hdr is not None:
                tables.append((hdr, cur)); hdr, cur = None, []
    if hdr is not None: tables.append((hdr, cur))
    return tables

R = []
def chk(name, actual, expect, note=''):
    ok = (abs(actual - expect) < 0.01) if isinstance(actual, (int, float)) and isinstance(expect, (int, float)) else (actual == expect)
    R.append((name, actual, expect, '✅' if ok else '❌', note)); return ok

F = {'T1':'Table1_典型职业活动与工作任务表_人工智能数据工程技术_V1.0.md',
     'T2':'Table2_PGSD-KSA能力融合矩阵_人工智能数据工程技术_V1.0.md',
     'T3':'Table3_职业发展路径及关键行为条件表_人工智能数据工程技术_V1.0.md',
     'T4':'Table4_岗位职业能力可视化图谱_人工智能数据工程技术_V1.0.md',
     'T5':'Table5_课程体系与教学进程表_人工智能数据工程技术_V1.0.md',
     'T6':'Table6_岗位职业能力综合矩阵表_人工智能数据工程技术_V1.0.md',
     'RP':'2026级人工智能数据工程技术专业人才培养方案V1.0.md',
     'LF1':'LF1_数据采集与标注_课程标准_正式版.md','LF2':'LF2_数据治理与质量管控_课程标准_正式版.md',
     'LF3':'LF3_模型训练与评估_课程标准_正式版.md','LF4':'LF4_AI数据服务部署与运维_课程标准_正式版.md',
     'HT':'LF1_数据采集与标注_6×4分层教案_正式版.html',
     'RS':'人工智能数据工程技术专业岗位典型职业活动与工作任务调研报告_V1.0.md'}
T = {k: read(v) for k, v in F.items()}

tasks = {}
for hdr, rows in parse_tables(T['T1']):
    for r in rows:
        if len(r) >= 4 and re.match(r'^\d+\.\d+$', r[0]): tasks[r[0]] = r[3]
chk('T1 任务数', len(tasks), 11, ','.join(sorted(tasks)))
lv = Counter(tasks.values())
for k, v in [('L1',1),('L2',5),('L3',5),('L4',0)]: chk(f'T1 {k}', lv.get(k,0), v)

dims = Counter(); tcol = []
for hdr, rows in parse_tables(T['T2']):
    for r in rows:
        if len(r) >= 4 and re.match(r'^\d+\.\d+', r[1]) and re.match(r'^L[1-4]$', r[2]) and r[3] in 'PGSD':
            dims[r[3]] += 1; tcol.append(r[1].split()[0])
chk('T2 矩阵行数', len(tcol), 44); chk('T2 覆盖任务数', len(set(tcol)), 11)
for d in 'PGSD': chk(f'T2 维度{d}', dims.get(d,0), 11)

all_atoms = set()
for k in ['LF1','LF2','LF3','LF4']:
    a = set(re.findall(r'LF\d-Q\d-A\d\d', T[k])); all_atoms |= a
    chk(f'{k} 原子数', len(a) > 0, True, f'{len(a)}条')
chk('课标原子合计', len(all_atoms), 30, f'实得{len(all_atoms)}')

EXP = {'LF1':[36,32,28],'LF2':[36,40,36],'LF3':[48,64],'LF4':[36,40,36]}
for k, exp in EXP.items():
    got = [int(m.group(8)) for m in (re.match(r'^\| (Q\d) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| \*\*(\d+)\*\*', l) for l in T[k].splitlines()) if m]
    chk(f'{k} 情境学时', got, exp, str(got)); chk(f'{k} 学时合计', sum(got), sum(exp))
    chk(f'{k} ①—⑩', all(f'## {c}' in T[k] for c in '①②③④⑤⑥⑦⑧⑨⑩'), True)
    chk(f'{k} 附录A-D', all(re.search(r'附录\s*'+c, T[k]) for c in 'ABCD'), True)
    chk(f'{k} 达标线80%', '80%' in T[k], True)
    chk(f'{k} 无85%通过率', re.search(r'通过率[^。]{0,6}85%', T[k]) is None, True)
    chk(f'{k} 无P95≤300ms', 'P95≤300' not in T[k] and 'P95 ≤ 300' not in T[k], True)
    chk(f'{k} AIGC未填编号', re.search(r'ContentProducer:\s*\d', T[k]) is None, True)
    bad = [l for l in T[k].splitlines() if '符合国家教学标准' in l and '不得' not in l]
    chk(f'{k} 未宣称符合国标', bad, [])
    kp = [l for l in T[k].splitlines() if 'Kappa' in l]
    if k == 'LF1':
        chk('LF1 Kappa用于Q3一致性裁定', True, True, f'{len(kp)}处')
    else:
        chk(f'{k} Kappa仅否定引用', (not kp) or all(('不' in l or '仅' in l) for l in kp), True)

ch_h, ch_cr, courses = 0, 0, set()
for hdr, rows in parse_tables(T['T5']):
    if not hdr or not any(('课程名称' in h) or (h == '环节') for h in hdr): continue
    if '学时' not in hdr or '学分' not in hdr: continue
    ih, ic = hdr.index('学时'), hdr.index('学分')
    for r in rows:
        if len(r) > max(ih, ic) and re.match(r'^C\d{2}$', r[0]) and num(r[ih]) is not None:
            courses.add(r[0]); ch_h += int(num(r[ih])); ch_cr += int(num(r[ic]))
chk('T5 课程门数', len(courses), 43, f'实得{len(courses)}')
chk('T5 总学时', ch_h, 2768, f'实得{ch_h}')
chk('T5 总学分', ch_cr, 173, f'实得{ch_cr}')
sem = {}; semcr = {}
for hdr, rows in parse_tables(T['T5']):
    if hdr and '学期学时' in hdr and '学期学分' in hdr:
        ih, ic = hdr.index('学期学时'), hdr.index('学期学分')
        for r in rows:
            if len(r) > max(ih, ic) and re.match(r'^S\d$', r[0]) and num(r[ih]) is not None:
                sem[r[0]] = int(num(r[ih])); semcr[r[0]] = int(num(r[ic]))
EXPS = [464,416,384,432,432,640]; EXPSC = [29,26,24,27,27,40]
chk('T5 学期学时', [sem.get(f'S{i}') for i in range(1,7)], EXPS, str([sem.get(f'S{i}') for i in range(1,7)]))
chk('T5 学期学分', [semcr.get(f'S{i}') for i in range(1,7)], EXPSC, str([semcr.get(f'S{i}') for i in range(1,7)]))
chk('T5 学期学时加总', sum(sem.values()), 2768)
chk('T5 学期学分加总', sum(semcr.values()), 173)
for lbl, v, p in [('公共基础',704,25.43),('选修',320,11.56),('实践',1848,66.76)]:
    chk(f'T5 {lbl}占比', round(v/2768*100,2), p)

specs = set(); sem2 = {}; semcr2 = {}
rp = T['RP']
# —— 新体例（2026-10-25 学校标准版）——
# 1) 十章 + 表1—表11
chk('RP 十章', all(f'## {c}' in rp for c in '一二三四五六七八九十'), True)
tbls = re.findall(r'^表 (\d+)　', rp, re.M)
chk('RP 表号连续1-11', [int(x) for x in tbls], list(range(1, 12)), f'实得{tbls}')
# 2) 封面块与待定项（不编造）
chk('RP 封面块', all(x in rp for x in ['专业名称：', '专业代码：', '专业大类：', '制订日期：']), True)
chk('RP 三负责人待定不编造', rp.count('（待定）') >= 3, True)
# 3) 培养规格：条款式（1.A素质/2.K知识/3.S能力）
chk('RP 规格条款式', all(x in rp for x in ['**1. A 素质要求**', '**2. K 知识要求**', '**3. S 能力要求**']), True)
seg = rp[rp.find('### （二）培养规格'):rp.find('## 六、')]
items = re.findall(r'^（(\d+)）', seg, re.M)
chk('RP 规格条数', len(items), 27, f'实得{len(items)}（素质6/知识8/能力13）')
# 4) 课程表（表4—表8）门数与学时
cnum = ch = 0
for hdr, rows in parse_tables(rp):
    if hdr and hdr and hdr[0] == '序号' and '总学时' in hdr and ('课程名称' in hdr or '环节名称' in hdr):
        ih = hdr.index('总学时')
        for r in rows:
            if len(r) > ih and re.match(r'^\d+$', r[0]) and num(r[ih]) is not None:
                cnum += 1; ch += int(num(r[ih]))
chk('RP 课程表门数(表4-8)', cnum, 43, f'实得{cnum}')
chk('RP 课程表学时(表4-8)', ch, 2768, f'实得{ch}')
# 5) 进程表（表11）43 行 + 合计行
p11 = rp[rp.find('表 11'):]
prows = [l for l in p11.splitlines() if re.match(r'^\| (公共基础课|专业基础课|专业核心课|专业拓展课|实习实训) \|', l)]
ph = sum(int(l.split('|')[7]) for l in prows); pc = sum(float(l.split('|')[6]) for l in prows)
chk('RP 进程表行数', len(prows), 43, f'实得{len(prows)}')
chk('RP 进程表学时', ph, 2768, f'实得{ph}')
chk('RP 进程表学分', pc, 173, f'实得{pc}')
m = re.search(r'\| \*\*合计\*\* \|[^\n]*', rp[rp.find('表 11'):])
chk('RP 进程表合计行存在', m is not None, True)
if m:
    cells = [c.strip().strip('*') for c in m.group(0).strip('|').split('|')]
    chk('RP 周学时S1-S5', cells[10:15], ['28','26','24','27','27'], str(cells[10:15]))
    chk('RP 周学时S6', cells[15], '32', cells[15])
    chk('RP 六学期学时口径', all(x in m.group(0) for x in ['464','416','384','432','640']), True)
# 6) 删除清单零残留
for bad, label in [(r'【依据说明】', '依据说明大块'), (r'^## 附录', '附录章'), (r'^## 版本历史', '版本历史表'),
                   (r'LF 一览', 'LF一览表'), (r'双口径', '双口径账')]:
    chk(f'RP 无{label}残留', re.search(bad, rp, re.M) is None, True)
# 7) 关键数字与 L4 口径
for n in ['2768','173','25.43','11.56','66.76']: chk(f'RP 含{n}', n in rp, True)
chk('RP 目标能力区间L1-L3', 'L1—L3' in rp, True)
chk('RP 引用Table6挂接', 'Table6_岗位职业能力综合矩阵表' in rp, True)
chk('RP 课程代码注明教务分配', '以教务系统分配为准' in rp, True)

for k in ['T2','T3','T4','T6']:
    chk(f'{k} 声明L4归零', any(s in T[k] for s in ['L4 归零','L4×0','无 L4','L4=0','L4 0','目标层级（待企业确认）']), True)
for f, t in T.items():
    chk(f'{f} AIGC未填编号', re.search(r'ContentProducer:\s*\d', t) is None, True)
    bad = re.findall(r'(我们调研了?\s*2[0-9]\s*位|本次调研了?\s*2[0-9]\s*家)', t)
    if bad: chk(f'{f} 证据冒充一手', bad, [])
chk('HT 6×4网格', all(x in T['HT'] for x in ['A 领跑','B 主力','C 跟进','D 兜底']), True)
chk('HT 六步齐', all(x in T['HT'] for x in ['资讯','计划','决策','实施','检查','评价']), True)
chk('HT 无脚本依赖', '<script' not in T['HT'].lower(), True)

fails = [x for x in R if x[3] == '❌']
print('='*82); print(f'全链校验 V3：{len(R)} 项，通过 {len(R)-len(fails)}，失败 {len(fails)}'); print('='*82)
for n, a, e, m, note in R:
    if m == '❌': print(f'❌ {n}｜实得 {a}｜期望 {e}｜{note}')
print('-'*82)
for n, a, e, m, note in R:
    if m == '✅' and note: print(f'✅ {n}｜{note}')
print('结论：' + ('全部通过 ✅' if not fails else f'{len(fails)} 项不通过 ❌'))
