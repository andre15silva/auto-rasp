Those late passes happen in settled positions (fine) — and in the example the opponent then filled its own eye and lost 20 stones, explaining the +88 wins. So the late-game loss comes from our moves. Let me classify our moves after ply 50 by region type and whether the stone was later captured (wasted tempo).

```python
import sys, json, numpy as np, collections
sys.path.insert(0,'/work/tools')
from ana import *
from gorules import NB
g, B, V = load(9)
def region_of(b, me, i):
    rel = b.astype(int) * me
    st=[i]; reg={i}; tx=to=False
    while st:
        j=st.pop()
        for k in NB[j]:
            if rel[k]==0 and k not in reg: reg.add(k); st.append(k)
            elif rel[k]==1: tx=True
            elif rel[k]==-1: to=True
    return 'own' if tx and not to else 'opp' if to and not tx else 'both', len(reg)
stat = collections.Counter(); died = collections.Counter()
for gi, gm in enumerate(g):
    me = 1 if gm['net_color']=='black' else -1
    n = int(V[gi].sum()); mv = gm['moves']
    for m in mv:
        p = m['ply']
        if m['by'] != 'net' or m['move'] == 81 or p < 40: continue
        b = B[gi, p-1]; i = m['move']
        rg, sz = region_of(b, me, i)
        key = (rg, 'big' if sz > 6 else 'small')
        stat[key] += 1
        if B[gi, n-1][i] != me: died[key] += 1
for k in sorted(stat): print(k, stat[k], 'died/removed', died[k])
```