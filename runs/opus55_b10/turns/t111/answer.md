Layer 47 combines the 288-wide triple step with the 165-wide threshold of the saving-capture aggregate. I'll compress the pair step to pair-equivalence classes (defined w.r.t. any completion by two more neighbors), which narrows the triple step.

```python
s = open('/work/go.py').read()
s = s.replace("""TRIPLE_CLASS, TRIPLE_REP = build_triple_classes()""", """TRIPLE_CLASS, TRIPLE_REP = build_triple_classes()
def build_pair_classes():
    import itertools
    pairs = sorted({tuple(sorted(t)) for t in itertools.product(CATS, repeat=2)})
    comps = sorted({tuple(sorted(t)) for t in itertools.product(CATS, repeat=2)})
    sig = {}
    for p in pairs:
        key = tuple(tactic_score(msum(p, q)) for q in comps)
        sig.setdefault(key, []).append(p)
    cls, rep = {}, {}
    for k, (key, ps) in enumerate(sorted(sig.items())):
        rep[k] = ps[0]
        for p in ps: cls[p] = k
    return cls, rep
PAIR_CLASS, PAIR_REP = build_pair_classes()""")
s = s.replace("""    pNS = smap(lambda a, b: msum((a,), (b,)), cN, cS)
    tW = smap(lambda p, w: TRIPLE_CLASS[msum(p, (w,))], pNS, cW)""",
"""    pNS = smap(lambda a, b: PAIR_CLASS[msum((a,), (b,))], cN, cS)
    tW = smap(lambda p, w: TRIPLE_CLASS[msum(PAIR_REP[p], (w,))], pNS, cW)""")
open('/work/go.py','w').write(s)
import sys; sys.path.insert(0,'/work'); sys.setrecursionlimit(10000)
import importlib, go; importlib.reload(go)
print(len(go.PAIR_REP), len(go.TRIPLE_REP))
# sanity: pair-class representative substitution preserves final scores
import itertools
ok = True
for a, b, w, e in itertools.product(go.CATS, repeat=4):
    p = go.PAIR_CLASS[go.msum((a,), (b,))]
    t = go.TRIPLE_CLASS[go.msum(go.PAIR_REP[p], (w,))]
    v1 = max(-20.0, go.tactic_score(go.msum(go.TRIPLE_REP[t], (e,))))
    v2 = max(-20.0, go.tactic_score(go.msum((a, b, w), (e,))))
    if v1 != v2: ok = False; break
print('equivalence ok', ok)
r = compile_program()
print({k:v for k,v in r.items() if k not in ('residual_labels',)})
```