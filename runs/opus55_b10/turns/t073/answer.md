Layer 11 stacks the phase map (165) with the run-key maps (2×164). I'll delay the phase computation further. Let me also list the largest residual consumers to find dims to trim.

```python
import sys, collections; sys.path.insert(0,'/work')
s = open('/work/go.py').read()
s = s.replace("""    isst_d = nmap(lambda v: v, nmap(lambda v: v, nmap(lambda v: v, isst)))   # delay (depth 4)""",
"""    isst_d = isst
    for _ in range(6): isst_d = nmap(lambda v: v, isst_d)               # delay (aggregate lands at depth 8)""")
open('/work/go.py','w').write(s)
import importlib, go; importlib.reload(go)
r = compile_program()
print({k:v for k,v in r.items() if k not in ('residual_labels',)})
c = collections.Counter(l.split(':')[0] for l in r['residual_labels'])
print(sorted(c.items(), key=lambda x: -x[1])[:25])
print(sum(v for k,v in c.items() if v >= 50), sum(v for k,v in c.items() if v < 50), len(c))
```