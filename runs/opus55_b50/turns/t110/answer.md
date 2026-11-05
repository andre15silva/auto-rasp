The crude influence estimate says we're ~+10 at ply 40–50 in close losses but end at −5: we lose ~12–15 points between ply 50 and the end. Let me look at what happens in that phase in a couple of close losses.

```python
import sys, json, numpy as np
sys.path.insert(0,'/work/tools')
from ana import *
g, B, V = load(8)
close = [i for i, gm in enumerate(g) if -8 < gm['margin'] < 0]
for gi in close[:2]:
    mv = g[gi]['moves']; n = int(V[gi].sum())
    plies = [49, 59, 69, 79, 89, n-1]
    print('game', gi, 'net', g[gi]['net_color'], 'margin', g[gi]['margin'])
    print(side_by_side([B[gi,p] for p in plies], [str(p) for p in plies], [mv[p]['move'] for p in plies]))
    print([(m['ply'], m['by'][0], m['move'], (m['top5'][0][1] if m['by']=='net' else '')) for m in mv[50:80]])
```