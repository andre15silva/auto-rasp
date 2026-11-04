The delay map was mistakenly numerical (on string categories). Fix: categorical identity delay, then the numeric indicator.

```python
s = open('/work/go.py').read()
s = s.replace("""    isx1 = nmap(lambda c: 1.0 if c == 'X1' else 0.0, nmap(lambda v: v, cst))         # depth +2 (delay)""",
"""    isx1 = nmap(lambda c: 1.0 if c == 'X1' else 0.0, cmap(lambda v: v, cst))         # depth +2 (delay)""")
open('/work/go.py','w').write(s)
import sys; sys.path.insert(0,'/work'); sys.setrecursionlimit(10000)
import importlib, go; importlib.reload(go)
r = compile_program()
print({k:v for k,v in r.items() if k not in ('residual_labels',)})
```