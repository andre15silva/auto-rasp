Worse (35.9%), likely because strong region penalties stop us from defending/attacking inside regions; I'll revert them. A different observation is more promising: about a quarter of the strong-bot games are total wipeouts (+73.5/+88.5) where the bot, forced to move in a settled position, filled its own eyes. If we pass less (prefer safe fills in our own territory), the bot gets more chances to self-destruct. Let me revert REGP and make passing a last resort.

```python
s = open('/work/gonet4.py').read()
s = s.replace("REGP = {0: REG, 1: {'own': -1.8, 'opp': -1.5, 'both': 0.0, 'none': 0.0}, 2: {'own': -3.0, 'opp': -3.5, 'both': 0.0, 'none': 0.0}}",
              "REGP = {0: REG, 1: REG, 2: REG}")
s = s.replace("""    if win and nc == 0: return -1.0
    if win and nc == 1: return -2.5 if big else -4.0
    return -8.0""", """    if win and nc == 0: return -7.0
    if win and nc == 1: return -7.5
    return -9.0""")
open('/work/gonet4.py','w').write(s)
r = compile_program()
```