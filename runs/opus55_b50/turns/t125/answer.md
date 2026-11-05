I over-reached: with MLP_EXACTNESS = 2e6, float32 rounding in the threshold MLPs could reach ±0.125 per liberty flag, risking wrong liberty counts. Safer: 7 propagation steps with TINY = 8e-6 and exactness 5e5 (same precision regime as the verified v4).

```python
s = open('/work/gonet4.py').read()
s = s.replace("N_PROP = 8\n", "N_PROP = 7\n").replace("TINY = 2e-6\n", "TINY = 8e-6\n")
open('/work/gonet4.py','w').write(s)
open('/work/program.py','w').write('''
import sys
sys.path.insert(0, '/work')
import importlib, gonet4
importlib.reload(gonet4)
MLP_EXACTNESS = 500000
def program():
    return gonet4.build()
''')
import importlib, sys
sys.path.insert(0, '/work'); import gonet4; importlib.reload(gonet4)
print(gonet4.N_PROP, gonet4.TINY, gonet4.SHAPE, gonet4.PASSTAB(5, 0, 'B'), gonet4.PRIOR[0], gonet4.TACT['atari'], gonet4.TACT['def2'])
r = compile_program()
```