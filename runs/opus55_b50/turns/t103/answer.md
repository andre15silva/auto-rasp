Passing was actually correct there — the only legal moves left were our own eyes; those games were simply lost on territory by a few points. Let me look at how decisive our opening/middle-game choices are now (top-move probabilities by move number) in pass 6.

```python
import sys, json, numpy as np, collections
sys.path.insert(0,'/work/tools')
from ana import *
g, B, V = load(6)
byply = collections.defaultdict(list)
for gm in g:
    if gm['opponent'] != 'strong': continue
    for m in gm['moves']:
        if m['by'] == 'net' and m['ply'] < 60:
            byply[m['ply'] // 10].append(m['top5'][0][1])
for k in sorted(byply): print('plies', k*10, '-', k*10+9, 'mean top1 prob', round(np.mean(byply[k]), 3))
# opponent first moves distribution
first = collections.Counter(gm['moves'][0]['move'] for gm in g if gm['opponent']=='strong' and gm['net_color']=='white')
print('strong first moves (as black):', first.most_common(8))
ours = collections.Counter(gm['moves'][0]['move'] for gm in g if gm['net_color']=='black')
print('our first moves:', ours.most_common(8))
gi = [i for i, gm in enumerate(g) if gm['opponent']=='strong' and gm['net_color']=='black' and gm['result'] < 0][0]
mv = g[gi]['moves']
plies = [5, 11, 17, 23, 29, 35, 41, 47]
print(side_by_side([B[gi,p] for p in plies], [str(p) for p in plies], [mv[p]['move'] for p in plies]))
```