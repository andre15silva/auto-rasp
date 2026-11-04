```python
import json, numpy as np
from collections import Counter
G = json.load(open('/work/pass_4/games.json'))
B = np.load('/work/pass_4/boards.npy')
gs = [g for g in G if g['opponent']=='strong']
print(Counter((g['end'], g['result'], g['net_color']) for g in gs))
print(sorted(round(g['margin'],1) for g in gs if g['result']==-1))
# for losses by two passes: who passed first & ply, and whether net's pass prob was high
for g in [g for g in gs if g['result']==-1 and g['end']=='two_passes'][:12]:
    passes = [(m['ply'], m['by'][0], (m.get('top5') or [[None,None]])[0]) for m in g['moves'] if m['move']==81]
    print(g['net_color'], g['margin'], len(g['moves']), passes[:4])
```