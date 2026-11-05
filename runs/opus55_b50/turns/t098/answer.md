We passed with p≈0.998 while actually losing, so the network believed it was winning. Let me compute the true Tromp-Taylor difference on the boards where we passed, from the mover's view, and compare with the thresholds.

```python
import sys, json, numpy as np
sys.path.insert(0,'/work/tools')
from ana import *
from gorules import NB
g, B, V = load(6)
def tt(b, me):
    rel = b * me
    own = opp = neu = 0
    seen = set()
    for i in range(81):
        if rel[i] == 1: own += 1
        elif rel[i] == -1: opp += 1
    for i in range(81):
        if rel[i] != 0 or i in seen: continue
        st=[i]; reg={i}; tx=to=False
        while st:
            j=st.pop()
            for k in NB[j]:
                if rel[k]==0 and k not in reg: reg.add(k); st.append(k)
                elif rel[k]==1: tx=True
                elif rel[k]==-1: to=True
        seen |= reg
        if tx and not to: own += len(reg)
        elif to and not tx: opp += len(reg)
        else: neu += len(reg)
    return own, opp, neu
for gi in [2, 3, 5, 12, 14, 16]:
    gm = g[gi]; mv = gm['moves']; n = len(mv)
    p = n - 2  # our pass ply
    b = B[gi, p - 1]   # board before our pass
    me = 1 if gm['net_color'] == 'black' else -1
    own, opp, neu = tt(b, me)
    print(gi, gm['net_color'], 'own', own, 'opp', opp, 'neu', neu, 'd', own - opp, 'margin(komi)', own - opp + (-7.5 if me == 1 else 7.5), 'final', gm['margin'])
```