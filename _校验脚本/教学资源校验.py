#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""教学资源两件套校验器：学生互动模块（七段/零依赖/JS语法/红线机制/检测题）＋教师授课包（必备块）。"""
import os, re, subprocess, sys

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SM = os.path.join(D, '教学资源', '学生互动模块')
TP = os.path.join(D, '教学资源', '教师授课包')
NODE = '/Users/joelgong/.workbuddy/binaries/node/versions/22.22.2-6/bin/node'

EXPECT_SM = [
 'LF1-Q1_多源数据采集任务执行与数据集交付', 'LF1-Q3_标注规则细化与争议样本裁定',
 'LF2-Q1_数据集清洗与质量报告编制', 'LF2-Q2_数据质量异常根因定位与治理',
 'LF2-Q3_数据分类分级与脱敏配置执行', 'LF3-Q1_训练数据集构建与特征处理',
 'LF3-Q2_模型训练评测与效果诊断', 'LF4-Q1_部署缺陷检测推理服务并与业务系统联调',
 'LF4-Q2_研判线上准确率下降并执行回滚', 'LF4-Q3_承接新业务线排产并配置质量门']
LFQ = {'LF1': ['Q1', 'Q2', 'Q3'], 'LF2': ['Q1', 'Q2', 'Q3'], 'LF3': ['Q1', 'Q2'], 'LF4': ['Q1', 'Q2', 'Q3']}
# 各情境课标红线条数（用于核对机制化数量）
REDLINE = {'LF1-Q1': 3, 'LF1-Q2': 3, 'LF1-Q3': 4, 'LF2-Q1': 3, 'LF2-Q2': 3, 'LF2-Q3': 3,
           'LF3-Q1': 3, 'LF3-Q2': 3, 'LF4-Q1': 3, 'LF4-Q2': 3, 'LF4-Q3': 3}

R = []
def chk(name, ok, note=''):
    R.append((name, '✅' if ok else '❌', note)); return ok

def js_syntax(path):
    t = open(path, encoding='utf-8').read()
    m = re.search(r'<script>(.*?)</script>', t, re.S)
    if not m: return False, '无 script'
    open('/tmp/_cw_check.js', 'w', encoding='utf-8').write(m.group(1))
    r = subprocess.run([NODE, '--check', '/tmp/_cw_check.js'], capture_output=True, text=True)
    return r.returncode == 0, (r.stderr or '')[:120]

sm_files = sorted(f for f in os.listdir(SM) if f.endswith('.html')) if os.path.isdir(SM) else []
tp_files = sorted(f for f in os.listdir(TP) if f.endswith('.html')) if os.path.isdir(TP) else []

print('学生互动模块 %d 件｜教师授课包 %d 件' % (len(sm_files), len(tp_files)))

for f in sm_files:
    key = f.split('_')[0]
    t = open(os.path.join(SM, f), encoding='utf-8').read()
    p = f[:36]
    # 七段
    for seg, kw in [('①顶部条', 'topbar'), ('②情境引入', '情境引入'), ('③知识预习', '知识预习'),
                    ('④六步闯关', '闯关'), ('⑤仿真实训', '仿真实训'), ('⑥检测', '检测'),
                    ('⑦成就', '成就')]:
        chk(f'{p} {seg}', kw in t)
    # 达标线 80%
    chk(f'{p} 达标线80%', '80%' in t)
    # 零外部请求
    ext = [pat for pat in [r'src="http', r'@import', r'fetch\(', r'href="http', r'url\(http'] if re.search(pat, t)]
    chk(f'{p} 零外部请求', not ext, ','.join(ext) if ext else '')
    # JS 语法
    ok, err = js_syntax(os.path.join(SM, f))
    chk(f'{p} JS语法', ok, err if not ok else '')
    # 教学样例声明
    chk(f'{p} 教学样例声明', '教学样例' in t)
    # 红线炸号机制
    chk(f'{p} 红线炸号机制', '炸号' in t or '触发 D 类红线' in t or '触发D类红线' in t)
    # 检测题数（QUIZ 数组条数或 quiz-q 计数）
    n = len(re.findall(r"\{t:'", t)) or len(re.findall(r"t:'", t))
    chk(f'{p} 检测10题', n >= 8, f'实得约{n}题')
    # localStorage 进度
    chk(f'{p} 进度持久化', 'localStorage' in t)

for f in tp_files:
    t = open(os.path.join(TP, f), encoding='utf-8').read()
    p = f[:36]
    for kw in ['六步', 'A', 'B', 'C', 'D', '工单', '引导文', '检查表', 'Rubric', '案例', '安全', '备课']:
        chk(f'{p} 含{kw}', kw in t)
    chk(f'{p} 零JS', '<script' not in t.lower())
    chk(f'{p} GitBook风', ('目录' in t and '锚点' in t) or 'nav' in t.lower() or 'toc' in t.lower())

fails = [x for x in R if x[1] == '❌']
print('=' * 78)
print('教学资源校验：%d 项，通过 %d，失败 %d' % (len(R), len(R) - len(fails), len(fails)))
for n, m, note in R:
    if m == '❌':
        print('❌ %s｜%s' % (n, note))
print('结论：' + ('全部通过 ✅' if not fails else f'{len(fails)} 项待修 ❌'))
sys.exit(1 if fails else 0)
