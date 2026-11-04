The key failure: when our big group is in atari and a capture of an adjacent attacker would save it, we often pick a different (equally scored) capture elsewhere — e.g., capturing 1 stone at 6 instead of the capture at 27 that saves our 10-stone group. I'll add a "saving capture" bonus: flag opponent stones in atari that touch one of our stones in atari, and reward capturing them. I'll also downweight ko-shaped captures (our capturing stone left with no friendly or empty neighbor) to reduce superko-cycle losses.

```python
s = open('/work/go.py').read()
# 1) ko-shaped captures are worth less
s = s.replace("""    if cap: s += 10.0 + 2.0 * (min(nO1, 2) - 1)""",
"""    kolike = cap and nE == 0 and not xs and nO1 == 1
    if cap: s += (3.0 if kolike else 10.0 + 2.0 * (min(nO1, 2) - 1))""")
# 2) saving-capture bonus
s = s.replace("""    tact = nmap(lambda v: v + T_OFF, tcat).named('tact')""",
"""    tact = nmap(lambda v: v + T_OFF, tcat).named('tact')
    # opponent stones in atari that touch one of our stones in atari -> capturing them saves us
    isx1 = nmap(lambda c: 1.0 if c == 'X1' else 0.0, nmap(lambda v: v, cst))         # depth +2 (delay)
    x1n = rasp.numerical(rasp.Aggregate(rasp.Select(idx, qA, GEQ), isx1, default=0))
    hx1 = cmap(lambda x: int(x > 0.05), x1n)
    flag = smap(lambda c, h: 'F' if (c == 'O1' and h) else ('N' if c != 'Z' else 'Z'), cst, hx1)
    fsoft = rasp.Aggregate(rasp.Select(idx, qA, GEQ), flag)
    fnum = nmap(lambda v: 1.0 if v == 'F' else (0.1 if v == 'Z' else 0.0), fsoft)
    savecap = nmap(lambda x: SAVECAP_BONUS if x > 0.05 else 0.0, fnum).named('savecap')""")
s = s.replace("""    return add(tact, pos).named('logit')""", """    return add(add(tact, savecap), pos).named('logit')""")
s = s.replace("""PASS_LOGIT = -2.0""", """PASS_LOGIT = -2.0
SAVECAP_BONUS = 7.0""", 1)
# make sure 'Z' exists in cst's value set as an impossible category
s = s.replace("""    def catf(cr, b):
        col, a = cr
        if col == 0: return 'E'""", """    def catf(cr, b):
        col, a = cr
        if col == 3 and a == 3: return 'Z'           # impossible combination (side token with 3 rows)
        if col == 0: return 'E'""")
open('/work/go.py','w').write(s)
import sys; sys.path.insert(0,'/work'); sys.setrecursionlimit(10000)
import importlib, go, estimate
importlib.reload(go)
print(go.CATS, estimate.estimate(go.program()))
```