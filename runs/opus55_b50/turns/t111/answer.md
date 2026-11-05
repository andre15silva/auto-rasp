In game 5 we **passed at ply 66** in the middle of an unsettled fight (p=0.52): the Tromp-Taylor estimate counts our dead invading stones as ours and sees few neutral points, so the "+6 pass when winning" rule fires too early. Let me measure how often we pass without the game ending.

```python
import sys, json, numpy as np, collections
sys.path.insert(0,'/work/tools')
from ana import *
g, B, V = load(8)
prem = 0; tot = 0; res = collections.Counter()
for gm in g:
    mv = gm['moves']
    for j, m in enumerate(mv):
        if m['by'] == 'net' and m['move'] == 81:
            tot += 1
            ended = (j == len(mv) - 1) or (j + 1 < len(mv) and mv[j+1]['move'] == 81 and j + 1 == len(mv) - 1)
            if not ended:
                prem += 1; res[gm['result']] += 1
print('our passes', tot, 'non-final', prem, 'by result of game', res)
```