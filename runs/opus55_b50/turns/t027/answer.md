The slowness appears in the propagation stage (16M params → 16 s). The selectors there use attention-derived run ids; I suspect float32 denormals from particular logit gaps. Let me test variants of the predicate magnitudes.

```python
import importlib, sys
sys.path.insert(0,'/work')
variants = [
  dict(SEL=5.0, UNSEL=-5.0, GTOP=6.9, GSTEP=0.7),
  dict(SEL=5.0, UNSEL=0.0, GTOP=6.9, GSTEP=0.7),
  dict(SEL=3.0, UNSEL=-3.0, GTOP=6.9, GSTEP=0.7),
  dict(SEL=5.0, UNSEL=-5.0, GTOP=4.0, GSTEP=0.3),
]
s = open('/work/gonet.py').read()
s = s.replace("6.9 if (q == 81 and k == 81) else UNSEL", "GTOP if (q == 81 and k == 81) else UNSEL")
s = s.replace("return 6.9 - 0.7 * (q - k)", "return GTOP - GSTEP * (q - k)")
s = s.replace("return 6.9 - 0.7 * ((q - k) // 9)", "return GTOP - GSTEP * ((q - k) // 9)")
s = s.replace("SEL, UNSEL = 5.0, -5.0", "SEL, UNSEL = 5.0, -5.0\nGTOP, GSTEP = 6.9, 0.7")
open('/work/gonet.py','w').write(s)
for v in variants:
    hdr = '\n'.join(f'gonet.{k} = {val}' for k, val in v.items())
    open('/work/program.py','w').write(f'''
import sys
sys.path.insert(0, '/work')
import importlib, gonet
importlib.reload(gonet)
{hdr}
MLP_EXACTNESS = 1000
def program():
    return gonet.build(stop='prop')
''')
    print(v); r = compile_program()
```