Layer 4 still has 4 heads (seeds ×2, near-one, t2). Moving t2 one level later:

```python
s = open('/work/go.py').read()
s = s.replace("""    t2 = rasp.Aggregate(rasp.Select(idx, qB, GEQ), tok_d2)             # soft token mix within distance 2
    tok_d3 = cmap(lambda t: t, tok_d2)""", """    tok_d3 = cmap(lambda t: t, tok_d2)
    t2 = rasp.Aggregate(rasp.Select(idx, qB, GEQ), tok_d3)             # soft token mix within distance 2""")
open('/work/go.py','w').write(s)
import sys; sys.path.insert(0,'/work'); sys.setrecursionlimit(10000)
import importlib, go; importlib.reload(go)
r = compile_program()
print({k:v for k,v in r.items() if k not in ('residual_labels',)})
```