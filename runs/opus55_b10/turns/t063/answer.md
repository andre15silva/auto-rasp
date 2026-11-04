MLP width rose to 667 because the new positional table (16×21=336 hidden) landed in the same layer as the SelectorWidth MLPs. Let me factor it: first combine densities with adjacency into an equivalence class (classes defined by identical score rows across lines), then combine the class with the line.

```python
s = open('/work/go.py').read()
s = s.replace("""    adj = smap(lambda a, b: (a, b), hasx, haso)
    e2 = smap(lambda a, b: (a, b), nx2, no2)
    lin = cmap(lambda i: 'P' if i >= 81 else line_of(i), idx)
    adjl = smap(lambda a, l: 'P' if l == 'P' else a + (l,), adj, lin)
    def pfin(e, a):
        if a == 'P': return PASS_LOGIT
        return pos_score(e[0], e[1], a[0], a[1], a[2])
    pcat = smap(pfin, e2, adjl).named('pcat')""",
"""    adj = smap(lambda a, b: (a, b), hasx, haso)
    e2 = smap(lambda a, b: (a, b), nx2, no2)
    sit = smap(lambda e, a: POS_CLASS[(e[0], e[1], a[0], a[1])], e2, adj)
    lin = cmap(lambda i: 'P' if i >= 81 else line_of(i), idx)
    pcat = smap(lambda c, l: PASS_LOGIT if l == 'P' else POS_ROW[c][l], sit, lin).named('pcat')""")
s = s.replace("""TRIPLE_CLASS, TRIPLE_REP = build_triple_classes()""", """TRIPLE_CLASS, TRIPLE_REP = build_triple_classes()
def build_pos_classes():
    cls, rows = {}, {}
    sig = {}
    for a in range(4):
        for b in range(4):
            for c in range(2):
                for d in range(2):
                    key = tuple(pos_score(a, b, c, d, l) for l in range(5))
                    sig.setdefault(key, []).append((a, b, c, d))
    for k, (key, members) in enumerate(sorted(sig.items())):
        rows[k] = key
        for m in members: cls[m] = k
    return cls, rows
POS_CLASS, POS_ROW = build_pos_classes()""")
open('/work/go.py','w').write(s)
import sys; sys.path.insert(0,'/work'); sys.setrecursionlimit(10000)
import importlib, go, estimate
importlib.reload(go)
print(len(go.POS_ROW), estimate.estimate(go.program()))
r = compile_program()
print({k:v for k,v in r.items() if k!='residual_labels'})
```