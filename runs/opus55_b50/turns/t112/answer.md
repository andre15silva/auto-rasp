320 of our 444 passes didn't end the game — 2.5 free moves per game handed to the opponent, which matches the late-game point loss. I'll make passing modest even when the Tromp-Taylor estimate says we're winning (−1 relative when settled, so we pass only if the alternatives are mere territory fills).

```python
s = open('/work/gonet4.py').read()
s = s.replace("""    if win and nc == 0: return 6.0
    if win and nc == 1: return 1.0 if big else -1.0
    return -8.0""", """    if win and nc == 0: return -1.0
    if win and nc == 1: return -2.5 if big else -4.0
    return -8.0""")
open('/work/gonet4.py','w').write(s)
r = compile_program()
```