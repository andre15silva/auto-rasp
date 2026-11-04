I forgot the rewritten module lacks the `stop` hooks. Let me add them and bisect (with fewer compiles per run).

```python
s = open('/work/gonet.py').read()
s = s.replace("    R, C, TXc, TOc = flags[:9], flags[9:18], flags[18], flags[19]\n",
              "    R, C, TXc, TOc = flags[:9], flags[9:18], flags[18], flags[19]\n    if stop == 'prop': return flags[0]\n")
s = s.replace("    nbs = {d: shift(nbinfo", "    if stop == 'nbinfo': return rasp.numerical(rasp.Map(lambda v: 1.0 if v == 'E' else 0.0, nbinfo))\n    nbs = {d: shift(nbinfo")
s = s.replace("    t1 = rasp.numerical(rasp.Map(lambda v: v, t1c)).named('t1')\n", "    t1 = rasp.numerical(rasp.Map(lambda v: v, t1c)).named('t1')\n    if stop == 't1': return t1\n")
open('/work/gonet.py','w').write(s)
for stop in ['prop', 'prop', 'nbinfo']:
    open('/work/program.py','w').write(f'''
import sys
sys.path.insert(0, '/work')
import importlib, gonet
importlib.reload(gonet)
MLP_EXACTNESS = 1000
def program():
    return gonet.build(stop={stop!r})
''')
    print(stop, end=' '); r = compile_program()
```