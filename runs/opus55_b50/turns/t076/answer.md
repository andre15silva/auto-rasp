Our opening is essentially uniformly random (top move probabilities ≈ 0.02), which is a major weakness. But first let me understand how a *random* opponent killed a 21-stone group in game 97 — tracing that group's liberties over time and our moves.

```python
import sys, json, numpy as np
sys.path.insert(0,'/work/tools')
from ana import *
from gorules import group
g, B, V = load(4)
gi = 97; gm = g[gi]; mv = gm['moves']
s = 1  # net black
pt = 46  # a stone of the big group (row5,col1)
for p in range(50, 88):
    b = B[gi, p]
    if b[pt] != s: print(p, 'gone'); break
    gr, L = group(b, pt)
    m = mv[p]
    print(p, m['by'][0], m['move'], 'size', len(gr), 'libs', sorted(L), (m.get('top5') or [])[:2])
print(side_by_side([B[gi,p] for p in (60, 70, 76, 80, 84, 86)], ['60','70','76','80','84','86'], [mv[p]['move'] for p in (60,70,76,80,84,86)]))
```