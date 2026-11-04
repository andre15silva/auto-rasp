Everything checks out: liberty classes are now ~99.8% accurate (7 false ataris out of 4048 stones), phase and cut detection are exact, and region classification is right in all but 5 of 4052 empty points. Let me fix the index-81 run membership and compile.

```python
s = open('/work/go.py').read()
s = s.replace("""    srow = clean_bool(smap(lambda t, l: t != l, tok, ltok))
    scol = clean_bool(smap(lambda t, u: t != u, tok, utok))""",
"""    srow = clean_bool(smap(lambda t, l: (t != l) or (t in ('B', 'W')), tok, ltok))
    scol = clean_bool(smap(lambda t, u: (t != u) or (t in ('B', 'W')), tok, utok))""")
open('/work/go.py','w').write(s)
import sys; sys.path.insert(0,'/work'); sys.setrecursionlimit(10000)
import importlib, go; importlib.reload(go)
r = compile_program()
print({k:v for k,v in r.items() if k not in ('residual_labels',)})
```