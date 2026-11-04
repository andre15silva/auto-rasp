Many losses are close (−2.5 to −10.5) and end with passes. Let me inspect final boards of close losses to see whether dead stones or unfinished boundaries cost us.

```python
import sys, json, numpy as np
sys.path.insert(0,'/work/tools')
from ana import *
g, B, V = load(4)
close = [(gi, gm['margin']) for gi, gm in enumerate(g) if gm['opponent'] == 'strong' and -12 < gm['margin'] < 0]
print(close)
sel = [x[0] for x in close[:8]]
for k in range(0, len(sel), 4):
    gs = sel[k:k+4]
    print(side_by_side([B[gi, int(V[gi].sum())-1] for gi in gs], [f"g{gi} {g[gi]['net_color'][0]} {g[gi]['margin']}" for gi in gs]))
```