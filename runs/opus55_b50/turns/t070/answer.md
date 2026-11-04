Big jump: 30% vs strong (from 1.5%), 53% vs weak, 94% vs random, at 7.1 s/1000 positions. Let me analyze the losses, starting with the two losses to random.

```python
import sys, json, numpy as np
sys.path.insert(0,'/work/tools')
from ana import *
g, B, V = load(4)
for gi, gm in enumerate(g):
    if gm['opponent'] == 'random' and gm['result'] < 0:
        n = int(V[gi].sum())
        print('game', gi, 'net', gm['net_color'], 'margin', gm['margin'], 'end', gm['end'], 'len', n, 'cap', gm['captured'], 'lost', gm['lost'])
        plies = [n//4, n//2, 3*n//4, n-1]
        print(side_by_side([B[gi,p] for p in plies], [str(p) for p in plies]))
        ps = [(m['ply'], m['by']) for m in gm['moves'] if m['move'] == 81]
        print('passes', ps)
```