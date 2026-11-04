```python
s = open('/work/gonet.py').read()
s = s.replace("rasp.Map(lambda v: v > 0.5, flags[NBUCK])", "rasp.Map(lambda v: v > 0.5, flags[NBUCK], simplify=False)")
s = s.replace("rasp.Map(lambda v: v > 0.5, flags[NBUCK + 1])", "rasp.Map(lambda v: v > 0.5, flags[NBUCK + 1], simplify=False)")
open('/work/gonet.py','w').write(s)
r = compile_program()
```