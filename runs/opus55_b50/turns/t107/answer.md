No significant change (40.6% ± 4%); Black is the weak side (26.6% vs 54.7% as White). Let me look at Black games: margins and how our moves compare in the first 20 plies.

```python
import sys, json, numpy as np, collections
sys.path.insert(0,'/work/tools')
from ana import *
g, B, V = load(8)
bl = sorted(gm['margin'] for gm in g if gm['net_color']=='black')
wh = sorted(gm['margin'] for gm in g if gm['net_color']=='white')
print('black margins', bl)
print('white margins', wh)
first = collections.Counter(gm['moves'][0]['move'] for gm in g if gm['net_color']=='black')
print('our first moves as black', first.most_common(6))
resp = collections.Counter(gm['moves'][1]['move'] for gm in g if gm['net_color']=='white')
print('our reply to 48 as white', resp.most_common(6))
# strong bot's replies to our first move
rep = collections.defaultdict(collections.Counter)
for gm in g:
    if gm['net_color']=='black': rep[gm['moves'][0]['move']][gm['moves'][1]['move']] += 1
print({k: v.most_common(3) for k, v in list(rep.items())[:6]})
```