After ply 40 we play ~4 moves per game into small opponent-only regions (43% of which die) and ~2.3 into our own small regions — wasted tempo while boundary points remain. I'll make region penalties phase-dependent: mild early, strong late (own −3.0, opp −3.5 when ≥40 stones).

```python
s = open('/work/gonet4.py').read()
s = s.replace("        v = REG[rg] + (PRIOR[ph][ln] if ln < 9 else 0.0)", "        v = REGP[ph][rg] + (PRIOR[ph][ln] if ln < 9 else 0.0)")
s = s.replace("REG = {'own': -1.5, 'opp': -1.0, 'both': 0.0, 'none': 0.0}", """REG = {'own': -1.5, 'opp': -1.0, 'both': 0.0, 'none': 0.0}
REGP = {0: REG, 1: {'own': -1.8, 'opp': -1.5, 'both': 0.0, 'none': 0.0}, 2: {'own': -3.0, 'opp': -3.5, 'both': 0.0, 'none': 0.0}}""")
open('/work/gonet4.py','w').write(s)
import importlib, sys
sys.path.insert(0, '/work'); import gonet4; importlib.reload(gonet4)
print(min(min(p) for p in gonet4.PRIOR.values()) + min(min(r.values()) for r in gonet4.REGP.values()) + gonet4.EYE + gonet4.OFF4)
r = compile_program()
```