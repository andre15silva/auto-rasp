```python
import json, numpy as np
from collections import Counter
G = json.load(open('/work/pass_19/games.json'))
G = [g for g in G if g['opponent']=='strong']
L = [g for g in G if g['result']==-1]
print(Counter((g['end'], g['net_color']) for g in L))
print(sorted(round(g['margin'],1) for g in L))
print('lost', np.mean([g['lost'] for g in L]).round(1), 'capt', np.mean([g['captured'] for g in L]).round(1))
W = [g for g in G if g['result']==1]
print('wins: margin<60', sum(1 for g in W if g['margin']<60), 'blowouts', sum(1 for g in W if g['margin']>=60))
```