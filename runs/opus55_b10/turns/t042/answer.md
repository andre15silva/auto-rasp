Compiles in 315 s (within limits), 188M params. Before a first games pass, let me fix the 5-head layer (schedule the near-one constant one layer later) and slightly refine the save values (escapes that leave only 2 liberties are ladder-prone).

```python
s = open('/work/go.py').read()
s = s.replace("""    nq = cmap(lambda i: NEAR_N, idx)""", """    nq = smap(lambda t, l: NEAR_N, tok, ltok)     # delayed one layer (spreads heads)""")
s = s.replace("""    if aX1:
        if safe: s += 9.0 + (1.0 if lo >= 3 else 0.0)
        elif not sa: s += 4.0""", """    if aX1:
        if safe: s += 10.0 if lo >= 3 else 7.0
        elif not sa: s += 3.0""")
open('/work/go.py','w').write(s)
import sys; sys.path.insert(0,'/work'); sys.setrecursionlimit(10000)
import importlib, go, estimate
importlib.reload(go)
print(estimate.estimate(go.program()))
r = compile_program()
print({k:v for k,v in r.items() if k!='residual_labels'})
```