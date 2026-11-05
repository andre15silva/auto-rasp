That loss came from a lower-side group dying in a liberty fight — reading depth I can't add cheaply. With limited runs left, I'll test one combined variant of changes I believe are positive: a sharper opening prior (×1.5) and slightly stronger atari/defence bonuses.

```python
s = open('/work/gonet4.py').read()
s = s.replace("PRIOR = {0: [-3.0, -1.5, 0.8, 1.6, 2.0],", "PRIOR = {0: [-4.5, -2.2, 1.2, 2.4, 3.0],")
s = s.replace("'atari': 2.0, 'def2': 2.5}", "'atari': 2.5, 'def2': 3.0}")
open('/work/gonet4.py','w').write(s)
import importlib, sys
sys.path.insert(0, '/work'); import gonet4; importlib.reload(gonet4)
print(min(min(p) for p in gonet4.PRIOR.values()) + min(gonet4.REG.values()) + gonet4.EYE + gonet4.OFF4)
r = compile_program()
```