Config B: 103/256 = 40.2%, not better than A's 42.0% over 576 games. I'll revert to config A (the best-supported) as the final network and verify it compiles.

```python
s = open('/work/gonet4.py').read()
s = s.replace("        return (not win) and nc <= 2", "        return (not win) and nc <= 1")
s = s.replace("""    if win and nc == 0: return -4.0
    if win and nc == 1: return -5.0 if big else -6.0
    return -8.0""", """    if win and nc == 0: return -1.0
    if win and nc == 1: return -2.5 if big else -4.0
    return -8.0""")
open('/work/gonet4.py','w').write(s)
import importlib, sys
sys.path.insert(0, '/work'); import gonet4; importlib.reload(gonet4)
print('INV', gonet4.INV, 'N_PROP', gonet4.N_PROP, 'TINY', gonet4.TINY, 'PASSTAB win', gonet4.PASSTAB(5, 0, 'B'), gonet4.PASSTAB(6, 1, 'B'), 'lose', gonet4.PASSTAB(4, 0, 'B'))
r = compile_program()
```