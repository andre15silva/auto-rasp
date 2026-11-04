
import math, itertools
from tracr.rasp import rasp
from gocore import *

MLP_EXACTNESS = 100
STATES = ["e", "xs", "xa", "os", "oa", "edge"]
TS = 40.0
SCALE = 2.5
PASS_SCORE = -5.0
OFF = 40.0

def score(c):
    e, xs, xa, os_, oa, ed = [c.get(s, 0) for s in STATES]
    if ed == 4: return PASS_SCORE
    no = os_ + oa
    cap = oa >= 1
    libs = e + 1.5 * xs
    if no == 0 and e == 0 and not cap: return -30.0
    s = 0.0
    if cap: s += 12 + 2 * (oa - 1)
    save = xa >= 1 and (libs >= 2 or cap)
    if save: s += 8 + 2 * (xa - 1)
    if not cap:
        if libs <= 1: s -= 10
        elif libs < 2: s -= 3
    if no == 0 and e == 1 and not cap and not save: s -= 6
    if no >= 1 and libs >= 2: s += 1
    return s

def configs(n_edge):
    out = []
    for combo in itertools.combinations_with_replacement(STATES[:5], 4 - n_edge):
        c = {s: 0 for s in STATES}
        for s in combo: c[s] += 1
        c["edge"] = n_edge
        out.append(c)
    return out

CFG_I = configs(0)
CFG_E = configs(1) + configs(2) + [dict({s: 0 for s in STATES}, edge=4)]
FB_I = len(CFG_I); FB_E = len(CFG_E)

def tmpl_score(c, v):
    ch = {s: c[s] / 4.0 for s in STATES}
    nn = sum(x * x for x in ch.values())
    return TS * (2 * ch[v] - nn)

def P_tI(k, q):
    if k < FB_I: return tmpl_score(CFG_I[k], q)
    if k == FB_I: return TS * 8 if q == "edge" else 0.0
    return -TS * 10

def P_tE(k, q):
    if k < FB_E: return tmpl_score(CFG_E[k], q)
    if k == FB_E: return -TS * 10 if q == "edge" else TS * 1.5
    return -TS * 10

def lvl(cfgs, fb, t):
    if t < fb: return round(score(cfgs[t]) * 2) / 2
    return 0.0

def prior(i):
    if i >= 81: return 0.0
    r, c = divmod(i, 9)
    d = min(r, c, 8 - r, 8 - c)
    return [-1.5, 0.0, 1.0, 1.0, 0.8][d]

K_ITERS = 3

def program():
    tok, idx = rasp.tokens, rasp.indices
    isx = rasp.Map(lambda t: 1 if t == "x" else 0, tok)
    iso = rasp.Map(lambda t: 1 if t == "o" else 0, tok)
    ise = rasp.Map(lambda t: 1 if t == "." else 0, tok)
    f0 = lambda b, i: i if (b == 1 and i < 81) else 81
    Lx = rasp.SequenceMap(f0, isx, idx)
    Lo = rasp.SequenceMap(f0, iso, idx)
    Ie = rasp.SequenceMap(f0, ise, idx)
    sel_self = rasp.Select(idx, idx, P_selfw)
    sel_open = rasp.Select(idx, idx, P_open_proxy)
    E = rasp.Aggregate(sel_open, Ie)
    for k in range(K_ITERS):
        Hx = rasp.Aggregate(sel_self, Lx)
        Ho = rasp.Aggregate(sel_self, Lo)
        Lx = rasp.Aggregate(rasp.Select(idx, Hx, P_argmin), Lx)
        Lo = rasp.Aggregate(rasp.Select(idx, Ho, P_argmin), Lo)
    GLx = rasp.Aggregate(rasp.Select(Lx, Lx, P_group), E)
    GLo = rasp.Aggregate(rasp.Select(Lo, Lo, P_group), E)
    atval = rasp.Map(lambda t: "A" if t == "." else "S", tok)
    AtX = rasp.Aggregate(rasp.Select(idx, GLx, P_atari), atval)
    AtO = rasp.Aggregate(rasp.Select(idx, GLo, P_atari), atval)
    def fA(t, a):
        if t == "x": return "xa" if a == "A" else "xs"
        if t == "o": return "o"
        if t == ".": return "e"
        return "edge"
    stA = rasp.SequenceMap(fA, tok, AtX)
    def fB(s, a):
        if s == "o": return "oa" if a == "A" else "os"
        return s
    st = rasp.SequenceMap(fB, stA, AtO)
    hist = rasp.Aggregate(sel_open, st)
    tcI = rasp.Map(lambda t: lvl(CFG_I, FB_I, t), idx)
    tcE = rasp.Map(lambda t: lvl(CFG_E, FB_E, t), idx)
    TI = rasp.Aggregate(rasp.Select(idx, hist, P_tI), tcI)
    TE = rasp.Aggregate(rasp.Select(idx, hist, P_tE), tcE)
    vI = rasp.numerical(rasp.Map(lambda c: (c + OFF) * SCALE, TI))
    vE = rasp.numerical(rasp.Map(lambda c: (c + OFF) * SCALE, TE))
    Pn = rasp.numerical(rasp.Map(lambda i: (prior(i) + 2.0) * SCALE, idx))
    S1 = rasp.numerical(rasp.LinearSequenceMap(vI, vE, 1.0, 1.0))
    out = rasp.numerical(rasp.LinearSequenceMap(S1, Pn, 1.0, 1.0))
    return out
