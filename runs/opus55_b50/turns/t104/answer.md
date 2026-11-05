The strong bot always opens at (5,3), while our first ~10 moves are nearly uniform (top-1 prob 0.07) — the opening is where we fall behind. I'll add a game-phase signal (stone count via a cheap positional mean, discretised with the dummy-value trick) and make the line prior and influence table phase-dependent: strongly centre/4th-line in the opening, mild later. I'll also strengthen defence of 2-liberty groups and weaken ladder-prone escapes.

```python
s = open('/work/gonet4.py').read()
# phase variable
s = s.replace("    mtt = num(rasp.Aggregate(selall, ttn, default=0), 'mtt')",
"""    stn = num(M(lambda v: (PH_DUM.get(v[1], 0) if isinstance(v, tuple) else (1 if v in ('X', 'O') else 0)), colT), 'stn')
    mst = num(rasp.Aggregate(selall, stn, default=0), 'mst')
    def phf(x):
        for v, cl in PH_KEEP:
            if abs(x - v) < 1e-9: return cl
        return None
    phase = cat(M(phf, mst), 'phase')
    mtt = num(rasp.Aggregate(selall, ttn, default=0), 'mtt')""")
# move t4/t5 construction after phase: replace their definitions to use phase
s = s.replace("""    t4c = cat(SM(s4, aux, linec), 't4c')
    t4 = num(M(lambda v: v, t4c), 't4')
    t5c = cat(SM(lambda inf, c: round(OFF5 + (INFL.get(inf, 0.0) if c == 'E' else 0.0), 2), infl, color), 't5c')
    t5 = num(M(lambda v: v, t5c), 't5')
""", "")
s = s.replace("""    t6 = num(M(lambda v: v, t6c), 't6')""", """    t6 = num(M(lambda v: v, t6c), 't6')
    lp = cat(SM(lambda ln, ph: (ln, ph), linec, phase), 'lp')
    def s4p(a, lph):
        e, rg = a
        ln, ph = lph
        if e == 'side': return OFF4
        v = REG[rg] + (PRIOR[ph][ln] if ln < 9 else 0.0)
        if e == 'eye': v += EYE
        elif e == 'feye': v += FEYE
        return round(OFF4 + v, 2)
    t4c = cat(SM(s4p, aux, lp), 't4c')
    t4 = num(M(lambda v: v, t4c), 't4')
    cph = cat(SM(lambda c, ph: (c, ph), color, phase), 'cph')
    t5c = cat(SM(lambda inf, cp: round(OFF5 + (INFL[cp[1]].get(inf, 0.0) if cp[0] == 'E' else 0.0), 2), infl, cph), 't5c')
    t5 = num(M(lambda v: v, t5c), 't5')""")
s = s.replace("    if stop == 't6': return t6\n", "")
# tables
s = s.replace("PRIOR = [-2.0, -0.6, 0.6, 0.7, 0.8]", """PRIOR = {0: [-3.0, -1.5, 0.8, 1.6, 2.0], 1: [-1.5, -0.4, 0.5, 0.6, 0.6], 2: [-0.3, 0.0, 0.0, 0.0, 0.0]}
_PHD = [(9, 0), (10, 1), (39, 1), (40, 2)]
PH_KEEP = [(n / 81.0, c) for n, c in _PHD]
PH_DUM = {k: n / 81.0 for k, (n, c) in enumerate(_PHD)}""")
s = s.replace("""INFL = {(0, 0): 1.0, (1, 0): 0.5, (2, 0): -0.3, (3, 0): -1.5, (0, 1): 0.7, (0, 2): -0.2, (0, 3): -1.5,
        (1, 1): 1.0, (2, 1): 0.7, (1, 2): 0.7, (2, 2): 0.3, (3, 3): -0.3}""", """_INFL_MID = {(0, 0): 1.0, (1, 0): 0.5, (2, 0): -0.3, (3, 0): -1.5, (0, 1): 0.7, (0, 2): -0.2, (0, 3): -1.5,
        (1, 1): 1.0, (2, 1): 0.7, (1, 2): 0.7, (2, 2): 0.3, (3, 3): -0.3}
_INFL_OPEN = {(0, 0): 1.0, (1, 0): -0.5, (2, 0): -1.5, (3, 0): -2.5, (0, 1): 0.6, (0, 2): -0.5, (0, 3): -2.0,
        (1, 1): 0.5, (2, 1): 0.0, (1, 2): 0.0, (2, 2): 0.0, (3, 3): -0.3}
INFL = {0: _INFL_OPEN, 1: _INFL_MID, 2: _INFL_MID}""")
s = s.replace("'esc3': {'s': 6.5, 'm': 9.0}, 'esc2': {'s': 1.5, 'm': 3.5}", "'esc3': {'s': 6.5, 'm': 9.0}, 'esc2': {'s': 0.5, 'm': 2.5}")
s = s.replace("'atari': 2.0, 'def2': 1.5}", "'atari': 2.0, 'def2': 2.5}")
open('/work/gonet4.py','w').write(s)
import importlib, sys
sys.path.insert(0, '/work'); import gonet4; importlib.reload(gonet4)
assert gonet4.NDUM >= len(gonet4._PHD)
r = compile_program()
```