
import math, itertools
from tracr.rasp import rasp
from gocore import *
from gowin import *

MLP_EXACTNESS = 100
TS = 40.0
SCALE = 3.0
OFF = 50.0

def P_left(k, q):
    if q == PASSI or q % 9 == 0: return 2.0 if k == PASSI else -2.0
    return 2.0 if k == q - 1 else -2.0

def P_run(k, q):
    if q == PASSI: return 2.0 if k == PASSI else -10.0
    if k == PASSI: return -10.0
    if k // 9 == q // 9 and k <= q: return 2.0 + 3.0 * (k % 9)
    return -10.0

def P_group2(k, q):
    if q == PASSI: return 2.0 if k == "P" else -2.0
    return 2.0 if k == q else -2.0

def P_sz(k, q):
    if q == PASSI: return 2.0 if k == "P" else -2.0
    if k == q or k == "P": return 2.0
    return -2.0

def P_big(k, q):
    if k == 0: return 100.0 if q == "c" else 0.0
    if k == 1: return 250.0 if q == "d" else 0.0
    return -10.0

# ---------- templates over neighbour states ----------
GROUPS = {
  "A": {"o1s": "o1s", "o1b": "o1b", "x1s": "x1s"},
  "B": {"e": "e", "x1b": "x1b", "xn": "xn"},
  "C": {"e": "e", "o1s": "o", "o1b": "o", "on": "o", "x1s": "xa", "x1b": "xa", "xn": "xn", "edge": "edge"},
}
GNAMES = {"A": ["o1s", "o1b", "x1s", "r"], "B": ["e", "x1b", "xn", "r"], "C": ["e", "o", "xa", "xn", "edge"]}

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
    if c["x1s"] >= 1: s += 8.0 + 2.0 * (c["x1s"] - 1)
    return s

def scoreB(c):
    e, xb, xn = c["e"], c["x1b"], c["xn"]
    if c["r"] == 4: return -12.0
    if e >= 2:
        return (30.0 if e >= 3 else 24.0) if xb >= 1 else 0.0
    if e == 1:
        if xn >= 1: return 18.0 if xb >= 1 else -1.0
        return -14.0 if xb >= 1 else -12.0
    if xn >= 1:
        if xb >= 1: return 10.0
        return -1.0 if xn >= 2 else -3.0
    return -14.0 if xb >= 1 else -12.0

def scoreC(c):
    e, o, xa, xn, ed = c["e"], c["o"], c["xa"], c["xn"], c["edge"]
    if ed == 4: return 7.0   # pass: A0 + B(-12) + 7 = -5
    if o == 0 and e == 0 and xa == 0: return -40.0
    if o == 0 and e == 1 and xa == 0: return -7.0
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
