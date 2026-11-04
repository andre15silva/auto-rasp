```python
import json, numpy as np
for pss in [6,7,8]:
    G = json.load(open(f'/work/pass_{pss}/games.json'))
    nb = [g for g in G if g['margin'] < 60]
    for res in [1,-1]:
        gg = [g for g in nb if g['result']==res]
        print(pss, res, len(gg), 'captured', np.mean([g['captured'] for g in gg]).round(1), 'lost', np.mean([g['lost'] for g in gg]).round(1), 'len', np.mean([len(g['moves']) for g in gg]).round(1))
```