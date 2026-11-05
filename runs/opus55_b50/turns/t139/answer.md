Config A totals 242/576 = 42.0% vs strong. Now config B: broaden the losing-lottery condition (up to 5 neutral points) and prolong slightly when winning (settled-win pass −4 instead of −1), to give the bot more chances to err.

```python
s = open('/work/gonet4.py').read()
s = s.replace("        return (not win) and nc <= 1", "        return (not win) and nc <= 2")
s = s.replace("""    if win and nc == 0: return -1.0
    if win and nc == 1: return -2.5 if big else -4.0
    return -8.0""", """    if win and nc == 0: return -4.0
    if win and nc == 1: return -5.0 if big else -6.0
    return -8.0""")
open('/work/gonet4.py','w').write(s)
r = compile_program()
```