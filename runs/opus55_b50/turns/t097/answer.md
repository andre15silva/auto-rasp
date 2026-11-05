Many narrow losses, and in 30 of 39 strong losses *we* passed first and the opponent ended the game. Let me check what the network saw when it passed in those games (pass probability and the TT situation).

```python
import sys, json, numpy as np
sys.path.insert(0,'/work/tools')
from ana import *
g, B, V = load(6)
cnt = 0
for gi, gm in enumerate(g):
    if gm['opponent'] != 'strong' or gm['result'] > 0: continue
    mv = gm['moves']
    if mv[-2]['by'] != 'net' or mv[-2]['move'] != 81: continue
    n = len(mv)
    b = B[gi, n-1]
    print(gi, gm['net_color'][0], gm['margin'], 'our pass top5:', mv[-2]['top5'], ' empties:', int((b == 0).sum()))
    cnt += 1
    if cnt >= 8: break
gi = [i for i, gm in enumerate(g) if gm['opponent']=='strong' and gm['result']<0 and gm['moves'][-2]['by']=='net' and gm['moves'][-2]['move']==81][0]
n = int(V[gi].sum())
print(side_by_side([B[gi, n-1]], [f"g{gi} final {g[gi]['net_color']} {g[gi]['margin']}"]))
```