INV 9 causes more repetition losses (we're the repeating player 5×/pass) and fewer blowouts (26–31 vs 35–36 with INV 6). I'll revert to INV = 6 for the final network and confirm it compiles.

```python
s = open('/work/gonet4.py').read()
s = s.replace("OFF7, INV = 1.0, 9.0", "OFF7, INV = 1.0, 6.0")
open('/work/gonet4.py','w').write(s)
print(open('/work/program.py').read())
r = compile_program()
```