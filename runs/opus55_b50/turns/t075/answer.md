Close losses are mostly decided by territory, not endgame cleanup. Let me look at a whole close game every 8 plies to understand the positional differences.

```python
import sys, json, numpy as np
sys.path.insert(0,'/work/tools')
from ana import *
g, B, V = load(4)
gi = 9
mv = g[gi]['moves']; n = int(V[gi].sum())
print('net', g[gi]['net_color'], 'margin', g[gi]['margin'])
for k0 in range(0, 64, 32):
    plies = list(range(k0 + 3, min(k0 + 35, n), 4))
    print(side_by_side([B[gi,p] for p in plies], [str(p) for p in plies], [mv[p]['move'] for p in plies]))
print([ (m['ply'], m['move'], m.get('top5', [[None, None]])[0][1] if m['by']=='net' else '') for m in mv[:40]])
```