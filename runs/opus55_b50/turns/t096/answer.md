Progress: 39% vs strong (mean margin now +10.9), 72% vs weak, 100% vs random, 20.6 s/1000 positions. Let me look at the margin distribution, repetition endings, and how losses happen now.

```python
import sys, json, numpy as np, collections
sys.path.insert(0,'/work/tools')
from ana import *
g, B, V = load(6)
ms = sorted((gm['margin'], gm['net_color'][0], gm['end']) for gm in g if gm['opponent'] == 'strong')
print([ (m, c) for m, c, e in ms])
for gi, gm in enumerate(g):
    if gm['end'] == 'repetition':
        mv = gm['moves']
        print('rep game', gi, gm['opponent'], gm['net_color'], gm['result'], 'last by', mv[-1]['by'], [ (m['by'][0], m['move']) for m in mv[-8:]])
# pass behaviour: who passes first, at what margin
first = collections.Counter()
for gm in g:
    if gm['opponent'] != 'strong': continue
    mv = gm['moves']
    seq = [(m['by'][0], m['move']) for m in mv[-2:]]
    first[(seq[0][0], gm['result'])] += 1
print(first)
```