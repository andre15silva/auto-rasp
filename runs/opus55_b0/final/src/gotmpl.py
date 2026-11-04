
import math, itertools
from tracr.rasp import rasp
from gocore import *

MLP_EXACTNESS = 100
ST8 = ["e", "x1", "x2", "x3", "o1", "o2", "o3", "edge"]
TS = 40.0
SCALE = 2.5
OFF = 50.0

def P_left(k, q):
    if q == PASSI: return 2.0 if k == PASSI else -2.0
    if q % 9 == 0: return 2.0 if k == PASSI else -2.0
    return 2.0 if k == q - 1 else -2.0

def P_run(k, q):
    if q == PASSI: return 2.0 if k == PASSI else -10.0
    if k == PASSI: return -10.0
    if k // 9 == q // 9 and k <= q: return 2.0 + 3.0 * (k % 9)
    return -10.0

def P_group2(k, q):
    if q == PASSI: return 2.0 if k == "P" else -2.0
    return 2.0 if k == q else -2.0

def P_minlib(k, q):
    t, v = k, q
    if v == PASSI: return 50.0 if t == PASSI else 0.0
    if t == PASSI: return -60000.0
    if t == v: return 1000.0
    if t > v: return -8000.0
    return 0.0

def P_eqm(k, q):
    if q == PASSI: return 3.0 if k == PASSI else -2.0
    if k == q: return 3.0
    if k == PASSI: return 1.0
    return -2.0

# ---------- templates ----------
GROUPS = {
  "A": {"o1s": "o1s", "o1b": "o1b", "o2": "o2", "x1s": "x1s"},
  "B": {"e": "e", "x1b": "x1b", "x2": "x2", "x3": "x3"},
  "C": {"e": "e", "o1s": "o", "o1b": "o", "o2": "o", "o3": "o", "x1s": "x", "x1b": "x", "x2": "x", "x3": "x", "edge": "edge"},
}
GNAMES = {"A": ["o1s", "o1b", "o2", "x1s", "r"], "B": ["e", "x1b", "x2", "x3", "r"], "C": ["e", "o", "x", "edge"]}

def gof(h, s):
    return GROUPS[h].get(s, "r")

def cfgs(h):
    out = []
    for combo in itertools.combinations_with_replacement(GNAMES[h], 4):
        c = {g: 0 for g in GNAMES[h]}
        for g in combo: c[g] += 1
        out.append(c)
    return out
CFG = {h: cfgs(h) for h in "ABC"}

def scoreA(c):
    s = 0.0
    if c["o1b"] >= 1: s += 40.0 + 4.0 * (c["o1b"] + c["o1s"] - 1)
    elif c["o1s"] >= 1: s += 25.0 + 4.0 * (c["o1s"] - 1)
    elif c["o2"] >= 1: s += 3.0 + 1.0 * (c["o2"] - 1)
    if c["x1s"] >= 1: s += 8.0 + 2.0 * (c["x1s"] - 1)
    return s

def scoreB(c):
    e, xb, x2, x3 = c["e"], c["x1b"], c["x2"], c["x3"]
    if c["r"] == 4: return -12.0
    safe = x3 >= 1 or e >= 2
    if safe:
        s = 0.0
        if xb >= 1: s += 30.0 if (e >= 3 or x3 >= 1) else 24.0
        if x2 >= 1 and e >= 2: s += 2.0
        return s
    if xb >= 1: return -14.0
    if e == 1: return -6.0 if x2 >= 1 else -12.0
    return -6.0 if x2 >= 2 else -12.0

def scoreC(c):
    e, o, x, ed = c["e"], c["o"], c["x"], c["edge"]
    if ed == 4: return 7.0   # pass: total = A0 + B(-12) + 7 = -5
    if o == 0 and e == 0: return -40.0
    if o == 0 and e == 1: return -7.0
    return 1.0 if (o >= 1 and e >= 2) else 0.0

SCOREF = {"A": scoreA, "B": scoreB, "C": scoreC}

def make_tpred(h):
    cl = CFG[h]
    def P(k, q):
        if k >= len(cl): return -TS * 10
        c = cl[k]
        ch = {g: c[g] / 4.0 for g in c}
        nn = sum(x * x for x in ch.values())
        return TS * (2 * ch[gof(h, q)] - nn)
    return P

def make_tlevel(h):
    cl = CFG[h]
    def f(t):
        if t >= len(cl): return 0.0
        return float(SCOREF[h](cl[t]))
    return f

def prior(i):
    if i >= 81: return 0.0
    r, c = divmod(i, 9)
    d = min(r, c, 8 - r, 8 - c)
    return [-1.5, 0.0, 1.0, 1.0, 0.8][d]
