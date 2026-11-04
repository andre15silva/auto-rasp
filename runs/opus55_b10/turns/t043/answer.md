Compile took 440 s and the speed measurement is noisy (23–49 s per 1000). I need more margin. The biggest lever is the 960-wide tactical SequenceMap that pads every layer's MLP. Let me check how many triples of neighbor categories are actually distinguishable by the final score (quotient by equivalence), which could shrink that MLP a lot.

```python
import sys, itertools, importlib
sys.path.insert(0,'/work')
import go; importlib.reload(go)
CATS = go.CATS
def msum(a,b): return tuple(sorted(a+b))
triples = sorted({tuple(sorted(t)) for t in itertools.product(CATS, repeat=3)})
pairs = sorted({tuple(sorted(t)) for t in itertools.product(CATS, repeat=2)})
print(len(pairs), len(triples))
sig = {}
for t in triples:
    key = tuple(go.tactic_score(msum(t, (e,))) for e in CATS)
    sig.setdefault(key, []).append(t)
print('triple classes', len(sig))
# also pair classes w.r.t. completing with any 2 more
sigp = {}
for p in pairs:
    key = tuple(go.tactic_score(msum(p, q)) for q in pairs)
    sigp.setdefault(key, []).append(p)
print('pair classes', len(sigp))
# classes of pair (NS) relative to adding W then E: triple classes reachable
print(sorted(len(v) for v in sig.values())[-10:])
```