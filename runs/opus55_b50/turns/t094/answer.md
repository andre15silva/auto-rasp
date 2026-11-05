Found it: Tracr's categorical→numerical MLP has a ReLU on its 1-unit hidden layer, so every **negative** score was clipped to 0 — in v3 too (that's why eye-filling and self-atari penalties never worked!). Since softmax is shift-invariant, I'll add constant offsets so all table values are non-negative.

```python
s = open('/work/gonet4.py').read()
s = s.replace("t1c = cat(SM(lambda a, b: tactical(list(a) + list(b)), pNS, pWE), 't1c')",
              "t1c = cat(SM(lambda a, b: round(OFF1 + tactical(list(a) + list(b)), 2), pNS, pWE), 't1c')")
s = s.replace("""        if e == 'side': return 0.0
        v = REG[rg] + (PRIOR[ln] if ln < 9 else 0.0)
        if e == 'eye': v += EYE
        elif e == 'feye': v += FEYE
        return round(v, 2)""", """        if e == 'side': return OFF4
        v = REG[rg] + (PRIOR[ln] if ln < 9 else 0.0)
        if e == 'eye': v += EYE
        elif e == 'feye': v += FEYE
        return round(OFF4 + v, 2)""")
s = s.replace("t5c = cat(SM(lambda inf, c: (INFL.get(inf, 0.0) if c == 'E' else 0.0), infl, color), 't5c')",
              "t5c = cat(SM(lambda inf, c: round(OFF5 + (INFL.get(inf, 0.0) if c == 'E' else 0.0), 2), infl, color), 't5c')")
s = s.replace("""        if sd not in ('B', 'W'): return 0.0
        tc, nc = ps
        return PASSTAB(tc, nc, sd)""", """        if sd not in ('B', 'W'): return OFF6
        tc, nc = ps
        return round(OFF6 + PASSTAB(tc, nc, sd), 2)""")
s = s.replace("# ---------------- tables", "# ---------------- tables\nOFF1, OFF4, OFF5, OFF6 = 25.0, 20.0, 2.0, 10.0")
open('/work/gonet4.py','w').write(s)
import importlib, sys
sys.path.insert(0, '/work'); import gonet4; importlib.reload(gonet4)
# sanity: all table outputs non-negative
vals = []
import itertools
for l in itertools.product(gonet4.NBC, repeat=4):
    vals.append(gonet4.OFF1 + gonet4.tactical(list(l)))
print('t1 range', min(vals), max(vals))
r = compile_program()
```