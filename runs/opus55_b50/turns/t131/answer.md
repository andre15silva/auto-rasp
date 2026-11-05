The invasion lottery looks positive: 43.0% over 256 games (vs ~40% baseline) and the mean margin rose from ~14 to ~19. Let me strengthen it (INV 6 → 9) and evaluate over two passes.

```python
s = open('/work/gonet4.py').read()
s = s.replace("OFF7, INV = 1.0, 6.0", "OFF7, INV = 1.0, 9.0")
open('/work/gonet4.py','w').write(s)
r = compile_program()
```