The 'Z' category would leak into the tactical chain's lookup tables; I'll instead put the dummy in the flag map via an impossible combination. Then compile and time it.

```python
s = open('/work/go.py').read()
s = s.replace("""        if col == 3 and a == 3: return 'Z'           # impossible combination (side token with 3 rows)\n""", "")
s = s.replace("""    flag = smap(lambda c, h: 'F' if (c == 'O1' and h) else ('N' if c != 'Z' else 'Z'), cst, hx1)""",
"""    flag = smap(lambda c, h: 'F' if (c == 'O1' and h) else ('Z' if (c == 'N' and h) else 'N'), cst, hx1)""")
open('/work/go.py','w').write(s)
import sys; sys.path.insert(0,'/work'); sys.setrecursionlimit(10000)
import importlib, go, estimate
importlib.reload(go)
print(estimate.estimate(go.program()))
r = compile_program()
print({k:v for k,v in r.items() if k not in ('residual_labels',)})
```