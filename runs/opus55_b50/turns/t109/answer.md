```python
import sys, json, numpy as np, collections
sys.path.insert(0,'/work/tools')
from ana import *
g, B, V = load(8)
D2 = [[k for k in range(81) if abs(k//9-i//9)+abs(k%9-i%9) <= 2] for i in range(81)]
def est(b, me):
    rel = b.astype(int) * me
    s = int(rel.sum())
    for i in range(81):
        if rel[i] == 0:
            t = int(sum(rel[k] for k in D2[i]))
            s += int(t > 0) - int(t < 0)
    return s
for lo, hi, nm in [(-12, 0, 'close losses'), (0, 12, 'close wins')]:
    traj = collections.defaultdict(list)
    for gm_i, gm in enumerate(g):
        if not (lo < gm['margin'] < hi): continue
        me = 1 if gm['net_color']=='black' else -1
        komi = -7.5 if me == 1 else 7.5
        n = int(V[gm_i].sum())
        for p in range(9, n, 10):
            traj[p // 10].append(est(B[gm_i, p], me) + komi)
    print(nm, [(k*10+9, len(v), round(float(np.mean(v)),1)) for k, v in sorted(traj.items()) if len(v) > 5])
```