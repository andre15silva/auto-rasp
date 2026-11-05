Dropping the minor "+0.5 reduce a 3+-liberty group" term cuts the triple classes from 55 to 40, shrinking the widest MLP. Let me apply it and recompile.

```python
s = open('/work/go.py').read()
s = s.replace("    if aO3 and safe: s += 0.5\n", "")
open('/work/go.py','w').write(s)
import sys; sys.path.insert(0,'/work'); sys.setrecursionlimit(10000)
import importlib, go; importlib.reload(go)
print(len(go.TRIPLE_REP))
r = compile_program()
print({k:v for k,v in r.items() if k not in ('residual_labels',)})
```