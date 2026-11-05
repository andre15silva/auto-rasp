Barely changed (42%), and we still pass ~3 times per game. So at those moments all alternatives must score below the pass. Let me inspect non-final passes: the network's top-5 and the board.

```python
import sys, json, numpy as np, collections
sys.path.insert(0,'/work/tools')
from ana import *
g, B, V = load(9)
ex = []
for gi, gm in enumerate(g):
    mv = gm['moves']
    for j, m in enumerate(mv):
        if m['by'] == 'net' and m['move'] == 81 and j < len(mv) - 2:
            ex.append((gi, j, m['top5'][:4], int((B[gi, j-1] == 0).sum())))
print(len(ex))
for e in ex[:12]: print(e)
gi, j = ex[3][0], ex[3][1]
print(side_by_side([B[gi, j-1], B[gi, j+1], B[gi, j+3]], ['before pass', 'opp reply', '+2'], [g[gi]['moves'][j-1]['move'], g[gi]['moves'][j+1]['move'], g[gi]['moves'][j+3]['move']]), g[gi]['net_color'])
```