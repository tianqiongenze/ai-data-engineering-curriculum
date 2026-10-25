#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 LF3 课标的原子编号改回 Table2 规范编号（A13—A18＋A29），消除与 LF4 的撞号。"""
import re, os
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
f = 'LF3_模型训练与评估_课程标准_正式版.md'
p = os.path.join(D, f)
t = open(p, encoding='utf-8').read()

MAP = [('LF3-Q1-A16', 'LF3-Q1-A13'), ('LF3-Q1-A17', 'LF3-Q1-A14'),
       ('LF3-Q2-A18', 'LF3-Q2-A15'), ('LF3-Q2-A19', 'LF3-Q2-A16'),
       ('LF3-Q2-A20', 'LF3-Q2-A17'), ('LF3-Q2-A21', 'LF3-Q2-A18')]
for i, (a, b) in enumerate(MAP):
    t = t.replace(a, f'@@TMP{i}@@')
for i, (a, b) in enumerate(MAP):
    t = t.replace(f'@@TMP{i}@@', b)

# 声明行：6 条 → 7 条，补 A29
t = t.replace('原子按 Table2 口径 LF3-Q1-A13/A14、LF3-Q2-A15—A18 共 6 条',
              '原子按 Table2 口径 LF3-Q1-A13/A14、LF3-Q2-A15—A18 及 A29（合规留痕·巩固）共 7 条')
# G8 合规目标绑定补 A29
t = t.replace('| G8 | S | 双人复核与超参签认零遗漏，数据卡"已知局限"与授权信息栏如实填写 | LF3-Q1-A14 | 合规检查表 |',
              '| G8 | S | 双人复核与超参签认零遗漏，数据卡"已知局限"与授权信息栏如实填写；训练启动前核对数据集授权链并留痕 | LF3-Q1-A14、LF3-Q2-A29 | 合规检查表＋授权链核对记录 |')
# 详表原子能力补 A29
t = t.replace('**原子能力**：LF3-Q2-A15、A16（执行段首次教学）；LF3-Q2-A17、A18（诊断段首次教学）',
              '**原子能力**：LF3-Q2-A15、A16（执行段首次教学）；LF3-Q2-A17、A18（诊断段首次教学）；LF3-Q2-A29（授权链核对与合规留痕·巩固，首次在 C28·S4 教学，本课做训练前核对）')
open(p, 'w', encoding='utf-8').write(t)

print('--- 复算四门课标原子 ---')
allа = set()
for k in ['LF1_数据采集与标注_课程标准_正式版.md', 'LF2_数据治理与质量管控_课程标准_正式版.md',
          'LF3_模型训练与评估_课程标准_正式版.md', 'LF4_AI数据服务部署与运维_课程标准_正式版.md']:
    txt = open(os.path.join(D, k), encoding='utf-8').read()
    a = set(re.findall(r'LF\d-Q\d-A\d\d', txt)); allа |= a
    print(f'{k[:6]}: {len(a)} 条  {sorted(a)}')
print('合计', len(allа), '（应 30）')
dup = [x for x in allа if sum(len(set(re.findall(r'LF\d-Q\d-A\d\d', open(os.path.join(D,k),encoding='utf-8').read())) & {x})
      for k in ['LF1_数据采集与标注_课程标准_正式版.md','LF2_数据治理与质量管控_课程标准_正式版.md',
                'LF3_模型训练与评估_课程标准_正式版.md','LF4_AI数据服务部署与运维_课程标准_正式版.md']) > 1]
print('跨课重号：', dup if dup else '无 ✅')
