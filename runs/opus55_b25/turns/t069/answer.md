```python
import json, numpy as np
from collections import Counter
dist = {'net': [], 'opponent': []}
for pss in [7]:
    G = json.load(open(f'/work/pass_{pss}/games.json'))
    for g in G:
        mv = g['moves']
        for a, b in zip(mv, mv[1:]):
            if a['move'] < 81 and b['move'] < 81 and b['ply'] < 50:
                ra, ca = divmod(a['move'], 9); rb, cb = divmod(b['move'], 9)
                who = 'net' if b['by'] == 'net' else 'opponent'
                dist[who].append(abs(ra-rb) + abs(ca-cb))
for k, v in dist.items():
    v = np.array(v)
    print(k, len(v), 'mean', v.mean().round(2), [round(float((v<=t).mean()),2) for t in [1,2,3,4,6]])
```