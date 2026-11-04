Only 52 triple-classes matter, so the 960-wide final SequenceMap can shrink to 52×8=416 by having the triple step output class ids. Let me also go back to 6 diffusion rounds (pass 2 showed undercounts were rare) and delay the near-one constant via a Map of qA (few extra paths).

```python
s = open('/work/go.py').read()
s = s.replace("R_ROUNDS = 8", "R_ROUNDS = 6")
s = s.replace("""    nq = smap(lambda t, l: NEAR_N, tok, ltok)     # delayed one layer (spreads heads)""",
              """    nq = cmap(lambda q: NEAR_N, qA)               # delayed one layer (spreads heads)""")
s = s.replace("""    tW = smap(lambda p, w: msum(p, (w,)), pNS, cW)
    tcat = smap(lambda t, e: tactic_score(msum(t, (e,))), tW, cE).named('tcat')""",
"""    tW = smap(lambda p, w: TRIPLE_CLASS[msum(p, (w,))], pNS, cW)
    tcat = smap(lambda t, e: tactic_score(msum(TRIPLE_REP[t], (e,))), tW, cE).named('tcat')""")
s = s.replace("""PASS_LOGIT = -2.0""", """PASS_LOGIT = -2.0
def build_triple_classes():
    import itertools
    triples = sorted({tuple(sorted(t)) for t in itertools.product(CATS, repeat=3)})
    sig = {}
    for t in triples:
        key = tuple(tactic_score(msum(t, (e,))) for e in CATS)
        sig.setdefault(key, []).append(t)
    cls, rep = {}, {}
    for k, (key, ts) in enumerate(sorted(sig.items())):
        rep[k] = ts[0]
        for t in ts: cls[t] = k
    return cls, rep""")
s = s.replace("""def program():""", """TRIPLE_CLASS, TRIPLE_REP = build_triple_classes()

def program():""")
open('/work/go.py','w').write(s)
import sys; sys.path.insert(0,'/work'); sys.setrecursionlimit(10000)
import importlib, go, estimate
importlib.reload(go)
print(len(go.TRIPLE_REP), estimate.estimate(go.program()))
r = compile_program()
print({k:v for k,v in r.items() if k!='residual_labels'})
```