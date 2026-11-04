Improved to 67.5% vs strong (Black 60%, White 75%). Let me re-check opening move quality, flatness, and the loss profile.

```python
import json, numpy as np
g = json.load(open('/work/pass_4/games.json'))
def line(m):
    r, c = divmod(m, 9); return min(r, c, 8-r, 8-c)
early = {0:0,1:0,2:0,3:0,4:0}; probs=[]
for x in g:
    for m in x['moves']:
        if m['by']=='net' and m['ply'] < 30 and m['move'] < 81:
            early[line(m['move'])] += 1
            probs.append(dict((a,b) for a,b in m['top5']).get(m['move'], 0.0))
probs=np.array(probs)
print('early by line', early, 'not-top5 frac', (probs==0).mean().round(3), 'median p', np.median(probs))
for opp in ['strong','weak']:
    for res in [1,-1]:
        sel = [x for x in g if x['opponent']==opp and x['result']==res]
        if sel: print(opp, res, len(sel), 'cap', np.mean([x['captured'] for x in sel]).round(1), 'lost', np.mean([x['lost'] for x in sel]).round(1), 'margin', np.mean([x['margin'] for x in sel]).round(1), 'len', np.mean([len(x['moves']) for x in sel]).round(1))
losses = [(i, x['net_color'], x['margin'], x['end']) for i,x in enumerate(g) if x['opponent']=='strong' and x['result']<0]
print(losses)
# first moves as black
from collections import Counter
print('first move as black', Counter(x['moves'][0]['move'] for x in g if x['net_color']=='black').most_common(8))
```