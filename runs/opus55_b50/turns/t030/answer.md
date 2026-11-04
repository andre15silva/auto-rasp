Big improvement (182 s → 46 s) but the propagation-only model is still slower than comparable toys. Let me isolate further with cheap variants.

```python
s = open('/work/gonet.py').read()
s = s.replace("    selH = rasp.Select(hrun, hrun, eq)\n    selV = rasp.Select(vrun, vrun, eq)\n",
"""    selH = rasp.Select(hrun, hrun, eq)
    selV = rasp.Select(vrun, vrun, eq)
    if FIXSEL:
        def fx(k, q):
            if k >= 81 or q >= 81: return SEL if k == q else UNSEL
            return SEL if abs(k//9 - q//9) + abs(k%9 - q%9) <= 1 else UNSEL
        selH = selV = rasp.Select(idx, idx, fx)
""")
s = s.replace("SEL, UNSEL = 10.6, -10.0\n", "SEL, UNSEL = 10.6, -10.0\nFIXSEL = False\n")
open('/work/gonet.py','w').write(s)
variants = [dict(), dict(GSTEP=0.0), dict(UNSEL=0.0), dict(FIXSEL=True), dict(N_PROP=2)]
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