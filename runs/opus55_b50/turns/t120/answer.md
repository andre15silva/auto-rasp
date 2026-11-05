Still ~40% — every variant lands within noise of 40%. I have 13 runs left, so let me do one focused analysis of late-game decisions in a close loss (our chosen move vs alternatives), to target the endgame where the points disappear.

```python
import sys, json, numpy as np
sys.path.insert(0,'/work/tools')
from ana import *
g, B, V = load(11)
close = [i for i, gm in enumerate(g) if -6 < gm['margin'] < 0]
gi = close[0]; gm = g[gi]; mv = gm['moves']; n = int(V[gi].sum())
print('net', gm['net_color'], 'margin', gm['margin'], 'len', n)
plies = [p for p in range(50, n-1) if mv[p]['by'] == 'net'][::3][:10]
for k in range(0, len(plies), 5):
    ps = plies[k:k+5]
    print(side_by_side([B[gi, p-1] for p in ps], [f"{p}:{mv[p]['move']}" for p in ps], [mv[p]['move'] for p in ps]))
    for p in ps: print(p, mv[p]['move'], mv[p]['top5'][:4], ' opp next:', mv[p+1]['move'] if p+1 < n else None)
```