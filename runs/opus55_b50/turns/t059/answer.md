73 s on the real machine despite a 3.7× smaller dense size, so something specific dominates. Let me bisect v2 in the sandbox (its timings roughly track the real machine for these models): full vs no propagation vs fixed selectors vs ungraded run search.

```python
s = open('/work/gonet.py').read()
if 'FIXSEL' not in s:
    s = s.replace("UNSEL_B = -10.0", "UNSEL_B = -10.0\nFIXSEL = False\nNOGRADE = False")
    s = s.replace("    hrun = rasp.categorical(rasp.Aggregate(rasp.Select(hkey, idx, ph), idx)).named('hrun')",
"""    if NOGRADE:
        ph = pv = (lambda k, q: SEL if k == q else UNSEL_B)
    hrun = rasp.categorical(rasp.Aggregate(rasp.Select(hkey, idx, ph), idx)).named('hrun')""")
    s = s.replace("    selV = rasp.Select(vrun, vrun, eq)\n", """    selV = rasp.Select(vrun, vrun, eq)
    if FIXSEL:
        def fx(k, q):
            if k >= 81 or q >= 81: return SEL if k == q else UNSEL
            return SEL if abs(k//9 - q//9) + abs(k%9 - q%9) <= 1 else UNSEL
        selH = selV = rasp.Select(idx, idx, fx)
""")
    open('/work/gonet.py','w').write(s)
import time
for v in [dict(N_PROP=0), dict(FIXSEL=True), dict(NOGRADE=True), dict()]:
    hdr = '\n'.join(f'gonet.{k} = {val}' for k, val in v.items())
    open('/work/program.py','w').write(f'''
import sys
sys.path.insert(0, '/work')
import importlib, gonet
importlib.reload(gonet)
{hdr}
MLP_EXACTNESS = 1000
def program():
    return gonet.build()
''')
    t0 = time.time()
    print(v, end=' '); r = compile_program(); print('  wall', round(time.time()-t0))
```