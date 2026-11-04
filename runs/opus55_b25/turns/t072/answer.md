```python
import json, numpy as np
for pss in [7,8,10,11]:
    G = [g for g in json.load(open(f'/work/pass_{pss}/games.json')) if g['opponent']=='strong']
    blow = sum(1 for g in G if g['margin'] > 60)
    nb = [g for g in G if g['margin'] < 60]
    print(pss, 'blow', blow, 'nb wins', sum(g['result']==1 for g in nb), '/', len(nb), 'nb margin', round(np.mean([g['margin'] for g in nb]),1),
          'lost', round(np.mean([g['lost'] for g in nb]),1), 'capt', round(np.mean([g['captured'] for g in nb]),1),
          'B nb', sum(g['result']==1 for g in nb if g['net_color']=='black'), '/', sum(1 for g in nb if g['net_color']=='black'))
```