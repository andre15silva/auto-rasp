Let me complete the pass/TT tables, influence and shape tables, gate the tactical term at the pass index, and assemble `gonet4.py`.

```python
src = open('/work/gonet4_draft.py').read()
# gate tactical term to empty points
src = src.replace("    t1c = cat(SM(tact, la, escm), 't1c')",
"""    escg = cat(SM(lambda e, c: e if c == 'E' else -1, escm, color), 'escg')
    t1c = cat(SM(lambda l, e: 0.0 if e == -1 else tact(l, e), la, escg), 't1c')""")
# TT dummies: build colT with many dummy categories, ttc from it
src = src.replace("""    ttc = cat(SM(ttf, color, region), 'ttc')
    TTV = {'own': 1.0, 'opp': 0.0, 'neu': 0.5, 'side': 0.5}
    ttn = num(M(lambda v: TTV[v], ttc), 'ttn')
    neun = num(M(lambda v: 1 if v == 'neu' else 0, ttc), 'neun')""",
"""    colT = cat(SM(lambda t, i: (('dum', i % NDUM) if (t in ('B', 'W') and i < 81) else COL[t]), tok, idx), 'colT')
    def ttf2(c, r):
        if isinstance(c, tuple): return c
        return ttf(c, r)
    ttc = cat(SM(ttf2, colT, region), 'ttc')
    TTV = {'own': 1.0, 'opp': 0.0, 'neu': 0.5, 'side': 0.5}
    ttn = num(M(lambda v: (TT_DUM[v[1]] if isinstance(v, tuple) else TTV[v]), ttc), 'ttn')
    neun = num(M(lambda v: (NEU_DUM.get(v[1], 0) if isinstance(v, tuple) else (1 if v == 'neu' else 0)), ttc), 'neun')""")
tables = r'''
# ---------------- tables
TACT = {
    'cap': {1: 8.0, 2: 9.5, 3: 11.0, 4: 12.5}, 'capsave': 2.0,
    'esc3': {1: 7.0, 2: 8.5, 3: 10.0, 4: 11.5}, 'esc2': {1: 2.0, 2: 3.0, 3: 4.0, 4: 5.0}, 'escf': -5.0,
    'sui': -10.0, 'sa': {1: -6.0, 2: -8.0, 3: -10.0, 4: -12.0}, 'fill2': -1.0, 'noE': -2.0,
    'def2': {1: 0.8, 2: 1.5, 3: 2.5, 4: 3.5},
    'atari': {1: 1.5, 2: 2.0, 3: 2.5, 4: 3.0},
}
SHAPE = {(1, 0): -0.2, (2, 0): -0.8, (3, 0): -1.5, (0, 1): 0.2, (0, 2): 0.3, (1, 1): 0.5, (2, 1): 0.3, (1, 2): 0.6}
REG = {'own': -1.5, 'opp': -1.0, 'both': 0.0, 'none': 0.0}
PRIOR = [-2.0, -0.6, 0.6, 0.7, 0.8]
EYE, FEYE = -12.0, -5.0
INFL = {(0, 0): 1.0, (1, 0): 0.5, (2, 0): -0.3, (3, 0): -1.5, (0, 1): 0.7, (0, 2): -0.2, (0, 3): -1.5,
        (1, 1): 1.0, (2, 1): 0.7, (1, 2): 0.7, (2, 2): 0.3, (3, 3): -0.3}
# Tromp-Taylor: m = 0.5 + d/162, d = own - opp area; classes c0..c6 by thresholds -15.5,-7.5,-0.5,0.5,7.5,15.5
def _m(d): return 0.5 + d / 162.0
_TTD = [(-16, 0), (-15, 1), (-8, 1), (-7, 2), (-1, 2), (0, 3), (1, 4), (7, 4), (8, 5), (15, 5), (16, 6)]
TT_KEEP = [(_m(d), c) for d, c in _TTD]
NDUM = len(_TTD)
TT_DUM = {k: _m(d) for k, (d, c) in enumerate(_TTD)}
_NEUD = [(0, 0), (1, 1), (2, 1), (3, 2), (5, 2), (6, 3)]
NEU_KEEP = [(n / 81.0, c) for n, c in _NEUD]
NEU_DUM = {k: n / 81.0 for k, (n, c) in enumerate(_NEUD) if n > 0}
def PASSTAB(tc, nc, sd):
    win = (tc >= 5) if sd == 'B' else (tc >= 2)
    big = (tc >= 6) if sd == 'B' else (tc >= 4)
    if win and nc == 0: return 6.0
    if win and nc == 1: return 1.0 if big else -1.0
    return -8.0
'''
src = src[:src.index('# ---------------- tables')] + tables
open('/work/gonet4.py','w').write(src)
open('/work/program.py','w').write('''
import sys
sys.path.insert(0, '/work')
import importlib, gonet4
importlib.reload(gonet4)
MLP_EXACTNESS = 500000
def program():
    return gonet4.build()
''')
import time; t0 = time.time()
r = compile_program(); print('wall', round(time.time()-t0))
```