
import math, itertools
from gocore import LSC, PASSI

def man_window(q):
    r, c = divmod(q, 9); on, off = [], 0
    for dr in range(-2, 3):
        for dc in range(-2, 3):
            if (dr, dc) == (0, 0) or abs(dr) + abs(dc) > 2: continue
            rr, cc = r + dr, c + dc
            if 0 <= rr < 9 and 0 <= cc < 9: on.append(rr * 9 + cc)
            else: off += 1
    return set(on), off
WIN = [man_window(q) for q in range(81)]

def P_win(k, q):
    if q == PASSI: return 2.0 if k == PASSI else -2.0
    on, off = WIN[q]
    if k in on: return 2.0
    if k == PASSI: return 2.0 + math.log(off) / LSC if off > 0 else -2.0
    return -2.0

WGRID = [0, 1, 2, 4, 7]
WE = [0.0, 1.5, 5.0]
WT = []
for E in WE:
    for X in WGRID:
        for O in WGRID:
            if X + O + E <= 12: WT.append((X, O, E))
WT.append((0, 0, 12.0))
WTS = 400.0

def wgroup(v):
    return {"x": "x", "o": "o", "B": "edge", "W": "edge"}.get(v, None)

def P_tW(k, q):
    if k >= len(WT): return -WTS * 10
    X, O, E = WT[k]
    c = {"x": X / 12.0, "o": O / 12.0, "edge": E / 12.0}
    nn = sum(v * v for v in c.values())
    g = wgroup(q)
    return WTS * ((2 * c[g] if g else 0.0) - nn)

def scoreW(X, O, E):
    if E >= 12: return 0.0
    line = {0.0: 1.0, 1.5: 0.0, 5.0: -1.5}[E]
    if X == 0 and O == 0: inf = 0.0
    elif O == 0: inf = 0.3 if X <= 2 else -1.5
    elif X == 0: inf = 0.8 if O <= 2 else -1.0
    else: inf = 1.2
    return line + inf

def tlevelW(t):
    if t >= len(WT): return 0.0
    return float(scoreW(*WT[t]))
