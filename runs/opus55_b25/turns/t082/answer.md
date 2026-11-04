```python
import json, numpy as np
from collections import Counter
for pss in [12, 13]:
    G = [g for g in json.load(open(f'/work/pass_{pss}/games.json'))]
    blow = sum(1 for g in G if g['margin'] > 60)
    nb = [g for g in G if g['margin'] < 60]
    print(pss, 'blow', blow, 'nb wins', sum(g['result']==1 for g in nb), '/', len(nb), 'nb margin', round(np.mean([g['margin'] for g in nb]),1),
          Counter((g['end'], g['result']) for g in G), 'B', sum(g['result']==1 for g in G if g['net_color']=='black'))
    losses = [g for g in G if g['result']==-1]
    print('  loss margins', sorted(round(g['margin'],1) for g in losses))
```