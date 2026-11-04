In these examples the groups were already lost; the deeper issue is positional play (many moves with equal ~0.14 probability → essentially random when there's no tactic). Let me look at margins and endings to see how close games are and how passing behaves.

```python
import sys, json, numpy as np, collections
sys.path.insert(0,'/work/tools')
from ana import *
g, B, V = load(4)
for opp in ['strong', 'weak']:
    ms = [(gm['margin'], gm['end'], gm['net_color']) for gm in g if gm['opponent'] == opp]
    ms.sort()
    print(opp, [m[0] for m in ms])
# who passed first in two-pass endings, and ply
for gi, gm in enumerate(g):
    if gm['opponent'] != 'strong' or gm['end'] != 'two_passes': continue
    mv = gm['moves']; n = len(mv)
    seq = [(m['by'][0], m['move']) for m in mv[-6:]]
    print(gi, gm['net_color'][0], gm['margin'], n, seq)
    if gi > 40: break
```