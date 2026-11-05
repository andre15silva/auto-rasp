No improvement (36.7%); all variants are within noise of ~39%. Let me check whether the "pass less" rule at least increased bot blowups (games won by >60), comparing passes 8–12.

```python
import sys, json, numpy as np
sys.path.insert(0,'/work/tools')
from ana import load
for k in [8, 9, 10, 11, 12]:
    g, B, V = load(k)
    ms = np.array([gm['margin'] for gm in g])
    wins = ms > 0
    print(k, 'win%', round(wins.mean()*100, 1), 'blowouts>60', int((ms > 60).sum()), 'close losses (-10,0)', int(((ms > -10) & (ms < 0)).sum()), 'close wins (0,10)', int(((ms > 0) & (ms < 10)).sum()))
```