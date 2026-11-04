Roughly unchanged vs strong (65% vs 67.5%, within noise), better vs weak (97%), fewer stones lost; Black remains the weak side (50%). Let me look at early-move quality now and at Black's losses.

```python
import json, numpy as np, sys
sys.path.insert(0,'/work')
import go
from collections import Counter
for pss in [4, 5]:
    g = json.load(open(f'/work/pass_{pss}/games.json'))
    early = Counter(); probs=[]
    for x in g:
        for m in x['moves']:
            if m['by']=='net' and m['ply'] < 30 and m['move'] < 81:
                early[go.line_of(m['move'])] += 1
                probs.append(dict((a,b) for a,b in m['top5']).get(m['move'], 0.0))
    probs = np.array(probs)
    bl = [x['margin'] for x in g if x['opponent']=='strong' and x['net_color']=='black']
    wh = [x['margin'] for x in g if x['opponent']=='strong' and x['net_color']=='white']
    print(pss, 'early lines', dict(sorted(early.items())), 'not-top5', (probs==0).mean().round(3),
          'black margins sorted', sorted(bl)[:20], 'white losses', sorted(wh)[:10])
```