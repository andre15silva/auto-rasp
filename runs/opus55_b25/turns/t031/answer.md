```python
import json, numpy as np
G = json.load(open('/work/pass_3/games.json'))
print(len(G), G[0].keys())
from collections import Counter
for opp in ['strong','weak']:
    gs = [g for g in G if g['opponent']==opp]
    c = Counter((g['end'], g['result']) for g in gs)
    print(opp, c)
    print(' margins', sorted(round(g['margin'],1) for g in gs))
    # who passed first and when
    fp = []
    for g in gs:
        for m in g['moves']:
            if m['move']==81:
                fp.append((m['ply'], 'net' if m['by']=='net' or m['by']==g['net_color'] else m['by'])); break
    print(' first passes', fp[:40])
print(G[0]['moves'][:3])
```