```python
import json, numpy as np
from collections import Counter
for pss in [6,7,8,10]:
    G = json.load(open(f'/work/pass_{pss}/games.json'))
    G = [g for g in G if g['opponent']=='strong']
    blow = sum(1 for g in G if g['margin'] > 60)
    nb = [g for g in G if g['margin'] < 60]
    rep = [g for g in G if g['end']=='repetition']
    print(pss, 'n', len(G), 'blow', blow, 'nb wins', sum(g['result']==1 for g in nb), '/', len(nb), 'nb margin', round(np.mean([g['margin'] for g in nb]),1),
          'rep', len(rep), 'rep losses', sum(g['result']==-1 for g in rep), 'lost', round(np.mean([g['lost'] for g in nb]),1), 'capt', round(np.mean([g['captured'] for g in nb]),1))
```