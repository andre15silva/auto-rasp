
import math
from tracr.rasp import rasp
from gocore import *
from gotmpl import *
from gowin import *

MLP_EXACTNESS = 100

def P_sz(k, q):
    if q == PASSI: return 2.0 if k == "P" else -2.0
    if k == q or k == "P": return 2.0
    return -2.0

def P_big(k, q):
    if k == 0: return 100.0 if q == "c" else 0.0
    if k == 1: return 250.0 if q == "d" else 0.0
    return -10.0

def P_up(k, q):
    if q == PASSI or q < 9: return 2.0 if k == PASSI else -2.0
    return 2.0 if k == q - 9 else -2.0

def P_vrun(k, q):
    if q == PASSI: return 2.0 if k == PASSI else -10.0
    if k == PASSI: return -10.0
    if k % 9 == q % 9 and k <= q: return 2.0 + 3.0 * (k // 9)
    return -10.0

N_ALT = 3

def program():
    tok, idx = rasp.tokens, rasp.indices
    isx = rasp.Map(lambda t: 1 if t == "x" else 0, tok)
    iso = rasp.Map(lambda t: 1 if t == "o" else 0, tok)
    ise = rasp.Map(lambda t: 1 if t == "." else 0, tok)
    clsx = rasp.Map(lambda t: "s" if t == "x" else ("P" if t in ("B", "W") else "n"), tok)
    clso = rasp.Map(lambda t: "s" if t == "o" else ("P" if t in ("B", "W") else "n"), tok)
    atval = rasp.Map(lambda t: "A" if t == "." else "S", tok)
    tvx = rasp.Map(lambda t: "x2" if t == "." else "n", tok)
    tvo = rasp.Map(lambda t: "o2" if t == "." else "n", tok)
    vYx = rasp.Map(lambda t: "y" if t == "x" else "n", tok)
    vYo = rasp.Map(lambda t: "y" if t == "o" else "n", tok)
    Lft = rasp.Aggregate(rasp.Select(idx, idx, P_left), tok)
    Upt = rasp.Aggregate(rasp.Select(idx, idx, P_up), tok)

    f0 = lambda b, i: i if (b == 1 and i < 81) else 81
    Lx0 = rasp.SequenceMap(f0, isx, idx)
    Lo0 = rasp.SequenceMap(f0, iso, idx)
    Ie = rasp.SequenceMap(f0, ise, idx)
    rsx = rasp.SequenceMap(lambda t, l: 1 if (t == "x" and l != "x") else 0, tok, Lft)
    rso = rasp.SequenceMap(lambda t, l: 1 if (t == "o" and l != "o") else 0, tok, Lft)
    RSx = rasp.SequenceMap(f0, rsx, idx)
    RSo = rasp.SequenceMap(f0, rso, idx)
    vsx = rasp.SequenceMap(lambda t, u: 1 if (t == "x" and u != "x") else 0, tok, Upt)
    vso = rasp.SequenceMap(lambda t, u: 1 if (t == "o" and u != "o") else 0, tok, Upt)
    VSx = rasp.SequenceMap(f0, vsx, idx)
    VSo = rasp.SequenceMap(f0, vso, idx)

    sel_self = rasp.Select(idx, idx, P_selfw)
    sel_open = rasp.Select(idx, idx, P_open_proxy)
    E = rasp.Aggregate(sel_open, Ie)

    fk = lambda l, c: (l if (c == "s" and l != 81) else ("P" if c == "P" else "n"))
    Hrx = rasp.Aggregate(rasp.Select(RSx, Lx0, P_run), RSx)
    Hro = rasp.Aggregate(rasp.Select(RSo, Lo0, P_run), RSo)
    Vrx = rasp.Aggregate(rasp.Select(VSx, Lx0, P_vrun), VSx)
    Vro = rasp.Aggregate(rasp.Select(VSo, Lo0, P_vrun), VSo)
    KHx = rasp.SequenceMap(fk, Hrx, clsx)
    KHo = rasp.SequenceMap(fk, Hro, clso)
    KVx = rasp.SequenceMap(fk, Vrx, clsx)
    KVo = rasp.SequenceMap(fk, Vro, clso)
    Lx, Lo = Hrx, Hro
    for k in range(N_ALT):
        if k % 2 == 0:
            Hx = rasp.Aggregate(rasp.Select(KVx, Vrx, P_group2), Lx)
            Ho = rasp.Aggregate(rasp.Select(KVo, Vro, P_group2), Lo)
        else:
            Hx = rasp.Aggregate(rasp.Select(KHx, Hrx, P_group2), Lx)
            Ho = rasp.Aggregate(rasp.Select(KHo, Hro, P_group2), Lo)
        Lx = rasp.Aggregate(rasp.Select(idx, Hx, P_argmin), Lx)
        Lo = rasp.Aggregate(rasp.Select(idx, Ho, P_argmin), Lo)

    Kx = rasp.SequenceMap(fk, Lx, clsx)
    Ko = rasp.SequenceMap(fk, Lo, clso)
    GLx = rasp.Aggregate(rasp.Select(Kx, Lx, P_group2), E)
    GLo = rasp.Aggregate(rasp.Select(Ko, Lo, P_group2), E)

    szvx = rasp.Map(lambda t: "c" if t == "x" else "d", tok)
    szvo = rasp.Map(lambda t: "c" if t == "o" else "d", tok)
    AtX0 = rasp.Aggregate(rasp.Select(idx, GLx, P_atari), atval)
    AtO0 = rasp.Aggregate(rasp.Select(idx, GLo, P_atari), atval)
    szvx2 = rasp.SequenceMap(lambda a, b: a, szvx, AtX0)
    szvo2 = rasp.SequenceMap(lambda a, b: a, szvo, AtO0)
    SZx = rasp.Aggregate(rasp.Select(Kx, Lx, P_sz), szvx2)
    SZo = rasp.Aggregate(rasp.Select(Ko, Lo, P_sz), szvo2)
    bigv = rasp.Map(lambda i: "big" if i == 0 else "small", idx)
    BIGx = rasp.Aggregate(rasp.Select(idx, SZx, P_big), bigv)
    BIGo = rasp.Aggregate(rasp.Select(idx, SZo, P_big), bigv)
    AtX, AtO = AtX0, AtO0
    M1x = rasp.Aggregate(rasp.Select(idx, GLx, P_minlib), idx)
    M1o = rasp.Aggregate(rasp.Select(idx, GLo, P_minlib), idx)

    M1xc = rasp.SequenceMap(lambda m, b: m, M1x, ise)
    M1oc = rasp.SequenceMap(lambda m, b: m, M1o, ise)
    I1x = rasp.Aggregate(rasp.Select(M1xc, idx, P_eqm), vYx)
    I1o = rasp.Aggregate(rasp.Select(M1oc, idx, P_eqm), vYo)
    fe2 = lambda p, y: 81 if y == "y" else p
    Ie2x = rasp.SequenceMap(fe2, Ie, I1x)
    Ie2o = rasp.SequenceMap(fe2, Ie, I1o)
    E2x = rasp.Aggregate(sel_open, Ie2x)
    E2o = rasp.Aggregate(sel_open, Ie2o)
    GL2x = rasp.Aggregate(rasp.Select(Kx, Lx, P_group2), E2x)
    GL2o = rasp.Aggregate(rasp.Select(Ko, Lo, P_group2), E2o)
    T2x = rasp.Aggregate(rasp.Select(idx, GL2x, P_atari), tvx)
    T2o = rasp.Aggregate(rasp.Select(idx, GL2o, P_atari), tvo)

    def f1(t, a):
        if t == "x": return "x1" if a == "A" else "xS"
        if t == "o": return "o"
        if t == ".": return "e"
        return "edge"
    st1 = rasp.SequenceMap(f1, tok, AtX)
    st2 = rasp.SequenceMap(lambda s, a: ("o1" if a == "A" else "oS") if s == "o" else s, st1, AtO)
    BIGxo = rasp.SequenceMap(lambda a, b: "xb" if a == "big" else ("ob" if b == "big" else "n"), BIGx, BIGo)
    def fb(s, b):
        if s == "x1": return "x1b" if b == "xb" else "x1s"
        if s == "o1": return "o1b" if b == "ob" else "o1s"
        return s
    st2b = rasp.SequenceMap(fb, st2, BIGxo)
    T2xo = rasp.SequenceMap(lambda a, b: "x2" if a == "x2" else ("o2" if b == "o2" else "n"), T2x, T2o)
    def f3(s, t):
        if s == "xS": return "x2" if t == "x2" else "x3"
        if s == "oS": return "o2" if t == "o2" else "o3"
        return s
    st = rasp.SequenceMap(f3, st2b, T2xo)
    hist = rasp.Aggregate(sel_open, st)

    vals = []
    for h in "ABC":
        tc = rasp.Map(make_tlevel(h), idx)
        T = rasp.Aggregate(rasp.Select(idx, hist, make_tpred(h)), tc)
        vals.append(rasp.numerical(rasp.Map(lambda c: (c + OFF) * SCALE, T)))
    histw = rasp.Aggregate(rasp.Select(idx, idx, P_win), tok)
    tcW = rasp.Map(tlevelW, idx)
    TW = rasp.Aggregate(rasp.Select(idx, histw, P_tW), tcW)
    Pn = rasp.numerical(rasp.Map(lambda c: (c + OFF) * SCALE, TW))
    S1 = rasp.numerical(rasp.LinearSequenceMap(vals[0], vals[1], 1.0, 1.0))
    S2 = rasp.numerical(rasp.LinearSequenceMap(vals[2], Pn, 1.0, 1.0))
    return rasp.numerical(rasp.LinearSequenceMap(S1, S2, 1.0, 1.0))
