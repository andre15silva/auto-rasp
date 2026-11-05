Margins cluster tightly around zero (median ≈ −2.5 as Black), so a few points would flip many games. Let me find *when* we lose the points: track a simple influence-based score estimate (stones + empty points assigned by majority within distance 2) along close games.

```python
import sys, json, numpy as np, collections
sys.path.insert(0,'/work/tools')
from ana import *
g, B, V = load(8)
D2 = [[k for k in range(81) if abs(k//9-i//9)+abs(k%9-i%9) <= 2] for i in range(81)]
def est(b, me):
    rel = b * me
    s = rel.sum()
    for i in range(81):
        if rel[i] == 0:
            t = sum(rel[k] for k in D2[i])
            s += (t > 0) - (t < 0)
    return s
traj = collections.defaultdict(list)
for gm_i, gm in enumerate(g):
    if not (-12 < gm['margin'] < 0): continue
    me = 1 if gm['net_color']=='black' else -1
    komi = -7.5 if me == 1 else 7.5
    n = int(V[gm_i].sum())
    for p in range(9, n, 10):
        traj[p // 10].append(est(B[gm_i, p], me) + komi)
for k in sorted(traj):
    if len(traj[k]) > 5: print('ply', k*10+9, 'n', len(traj[k]), 'mean est margin', round(np.mean(traj[k]), 1))
# same for close wins
traj2 = collections.defaultdict(list)
for gm_i, gm in enumerate(g):
    if not (0 < gm['margin'] < 12): continue
    me = 1 if gm['net_color']=='black' else -1
    komi = -7.5 if me == 1 else 7.5
    n = int(V[gm_i].sum())
    for p in range(9, n, 10): traj2[p // 10].append(est(B[gm_i, p], me) + komi)
print('wins:', [(k*10+9, round(np.mean(v),1)) for k, v in sorted(traj2.items()) if len(v) > 5])
```