The collapse in game 97 is a priority problem: twice the network captured a single stone (score 9) while its own 17–21-stone group was in atari. I need group-size awareness. Let me look at losses against the strong bot too, listing large captures against us and what we played just before.

```python
import sys, json, numpy as np, collections
sys.path.insert(0,'/work/tools')
from ana import *
g, B, V = load(4)
def net_sign(gm): return 1 if gm['net_color'] == 'black' else -1
events = collections.Counter(); examples = []
for gi, gm in enumerate(g):
    if gm['opponent'] != 'strong': continue
    s = net_sign(gm); mv = gm['moves']; prev = np.zeros(81, int)
    for p in range(int(V[gi].sum())):
        b = B[gi, p]
        lostn = int(((prev == s) & (b != s)).sum())
        if lostn >= 4 and mv[p]['by'] == 'opponent':
            pm = mv[p-1]
            examples.append((gi, p, lostn, pm['move'], pm['top5'][:3]))
        prev = b
print(len(examples), 'big-loss events in', sum(1 for x in g if x['opponent']=='strong'), 'games')
for e in examples[:12]:
    print(e)
gi, p = examples[0][0], examples[0][1]
mv = g[gi]['moves']
print(side_by_side([B[gi,p-2], B[gi,p-1], B[gi,p]], ['before', 'after ours', 'after capture'], [mv[p-2]['move'], mv[p-1]['move'], mv[p]['move']]))
gi, p = examples[3][0], examples[3][1]; mv = g[gi]['moves']
print(side_by_side([B[gi,p-2], B[gi,p-1], B[gi,p]], ['before', 'after ours', 'after capture'], [mv[p-2]['move'], mv[p-1]['move'], mv[p]['move']]))
```