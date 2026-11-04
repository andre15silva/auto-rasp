Level 3 has 5 aggregates. Let me move the positional aggregates back to layer 2 using the existing qA/qB queries (dropping qC entirely), giving ≤4 heads per layer and saving 82 residual dims.

```python
s = open('/work/go.py').read()
s = s.replace("""    qC = cmap(lambda q: Q(q.i, 'C'), qA)                         # delayed query (spreads heads over layers)
    tadj = rasp.Aggregate(rasp.Select(idx, qC, GT), tok)      # soft token mix of on-board neighbours
    t2 = rasp.Aggregate(rasp.Select(idx, qC, LT), tok)        # soft token mix within distance 2""",
"""    tadj = rasp.Aggregate(rasp.Select(idx, qA, GEQ), tok)     # soft token mix of on-board neighbours
    t2 = rasp.Aggregate(rasp.Select(idx, qB, GEQ), tok)       # soft token mix within distance 2""")
open('/work/go.py','w').write(s)
import sys; sys.path.insert(0,'/work'); sys.setrecursionlimit(10000)
import importlib, go, estimate
importlib.reload(go)
print(estimate.estimate(go.program()))
r = compile_program()
print({k:v for k,v in r.items() if k!='residual_labels'})
```