INV 9 averaged 41.4% vs INV 6's 43.0% (both over 256 games) — indistinguishable, but repetition endings rose (6–7 vs 2–3). Let me check who lost those repetition games.

```python
import sys, json, numpy as np, collections
sys.path.insert(0,'/work/tools')
from ana import load
for k in [15, 16, 17, 18]:
    g, B, V = load(k)
    rep = [(gm['moves'][-1]['by'], gm['result']) for gm in g if gm['end'] == 'repetition']
    ms = np.array([gm['margin'] for gm in g])
    print(k, 'repetition (last mover, our result):', rep, ' blowouts>60:', int((ms > 60).sum()), ' close losses:', int(((ms > -10) & (ms < 0)).sum()))
```