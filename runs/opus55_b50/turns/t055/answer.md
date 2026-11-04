The evaluation machine measured 106 s; dense FLOPs (layers × D × (4·H·K + 2·M)) is the only consistent predictor there (≈0.38 s per M dense params). I need ~3–4× cheaper. The dominant cost is 20 heads padded across all 25 layers. Idea: replace the 18 row/col liberty flags with ~8 hashed "liberty bucket" flags. Let me measure how accurately a hash with few buckets preserves liberty counts 1/2/3+ on realistic positions from the pass-1 games.

```python
import numpy as np, sys, itertools
sys.path.insert(0,'/work/tools')
from gorules import NB, group
from ana import load
g, B, V = load(1)
# collect groups: liberty sets
libsets = []
for gi in range(128):
    n = int(V[gi].sum())
    for p in range(10, n, 7):
        b = B[gi, p]
        seen = set()
        for i in range(81):
            if b[i] != 0 and i not in seen:
                gr, L = group(b, i)
                seen |= gr
                if len(L) <= 5: libsets.append((tuple(L), len(gr)))
print(len(libsets))
def evalhash(h, nb):
    conf = np.zeros((4, 4), int)
    for L, sz in libsets:
        t = min(len(L), 3); e = min(len({h(x) for x in L}), 3)
        conf[t, e] += 1
    return conf
cands = {
 'r+3c mod8': (lambda x: (x//9 + 3*(x%9)) % 8, 8),
 '2r+3c mod8': (lambda x: (2*(x//9) + 3*(x%9)) % 8, 8),
 'r+3c mod9': (lambda x: (x//9 + 3*(x%9)) % 9, 9),
 '(r%3,c%3)': (lambda x: (x//9)%3*3 + (x%9)%3, 9),
 'r+4c mod9': (lambda x: (x//9 + 4*(x%9)) % 9, 9),
 '2r+5c mod9': (lambda x: (2*(x//9) + 5*(x%9)) % 9, 9),
 'r+3c mod10': (lambda x: (x//9 + 3*(x%9)) % 10, 10),
 'r+3c mod7': (lambda x: (x//9 + 3*(x%9)) % 7, 7),
 'r+2c mod7': (lambda x: (x//9 + 2*(x%9)) % 7, 7),
 'idx mod 8': (lambda x: x % 8, 8),
 'idx mod 11': (lambda x: x % 11, 11),
}
for nm, (h, nb) in cands.items():
    c = evalhash(h, nb)
    err1 = c[2:,1].sum(); err2 = c[3,2]
    print(f'{nm:12s} true2->1: {c[2,1]:5d} true3+->1: {c[3,1]:4d} true3+->2: {c[3,2]:5d}  (n2={c[2].sum()}, n3={c[3].sum()})')
```