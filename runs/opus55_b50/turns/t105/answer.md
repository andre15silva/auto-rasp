Before testing: the opening INFL table now goes down to −2.5, but OFF5 is only 2 (values would be clipped). Fix the offset, then run 128 games against the strong bot.

```python
s = open('/work/gonet4.py').read()
s = s.replace("OFF1, OFF4, OFF5, OFF6 = 25.0, 20.0, 2.0, 10.0", "OFF1, OFF4, OFF5, OFF6 = 25.0, 20.0, 5.0, 10.0")
open('/work/gonet4.py','w').write(s)
import importlib, sys
sys.path.insert(0, '/work'); import gonet4; importlib.reload(gonet4)
print(min(min(t.values()) for t in gonet4.INFL.values()) + gonet4.OFF5, min(min(p) for p in gonet4.PRIOR.values()) + min(gonet4.REG.values()) + gonet4.EYE + gonet4.OFF4)
r = compile_program()
```