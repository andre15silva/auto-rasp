```python
import json, numpy as np
from collections import Counter
G = [g for g in json.load(open('/work/pass_12/games.json'))]
blow = sum(1 for g in G if g['margin'] > 60)
nb = [g for g in G if g['margin'] < 60]
print('blow', blow, 'nb wins', sum(g['result']==1 for g in nb), '/', len(nb), 'nb margin', round(np.mean([g['margin'] for g in nb]),1))
print(Counter((g['end'], g['result']) for g in G))
print(sorted(round(g['margin'],1) for g in G if g['result']==-1))
```