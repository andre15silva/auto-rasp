
import math
from tracr.rasp import rasp
from gocore import *
from gotmpl6 import *
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
    Lft = Lft.named("Lft")

    f0 = lambda b, i: i if (b == 1 and i < 81) else 81
    Lx0 = rasp.SequenceMap(f0, isx, idx)
    Lx0 = Lx0.named("Lx0")
    Lo0 = rasp.SequenceMap(f0, iso, idx)
    Lo0 = Lo0.named("Lo0")
    rsx = rasp.SequenceMap(lambda t, l: 1 if (t == "x" and l != "x") else 0, tok, Lft)
    ise_late = rasp.SequenceMap(lambda a, b: a, ise, rsx)
    Ie = rasp.SequenceMap(f0, ise_late, idx)
    Ie = Ie.named("Ie")
    rso = rasp.SequenceMap(lambda t, l: 1 if (t == "o" and l != "o") else 0, tok, Lft)
    RSx = rasp.SequenceMap(f0, rsx, idx)
    RSx = RSx.named("RSx")
    RSo = rasp.SequenceMap(f0, rso, idx)
    RSo = RSo.named("RSo")

    sel_self = rasp.Select(idx, idx, P_selfw)
    sel_open = rasp.Select(idx, idx, P_open_proxy)
    E = rasp.Aggregate(sel_open, Ie)
    E = E.named("E")

    Lx = rasp.Aggregate(rasp.Select(RSx, Lx0, P_run), RSx)
    Lo = rasp.Aggregate(rasp.Select(RSo, Lo0, P_run), RSo)
    for k in range(3):
        Hx = rasp.Aggregate(sel_self, Lx)
        Ho = rasp.Aggregate(sel_self, Lo)
        Lx = rasp.Aggregate(rasp.Select(idx, Hx, P_argmin), Lx)
        Lo = rasp.Aggregate(rasp.Select(idx, Ho, P_argmin), Lo)

    fk = lambda l, c: (l if (c == "s" and l != 81) else ("P" if c == "P" else "n"))
    Kx = rasp.SequenceMap(fk, Lx, clsx)
    Kx = Kx.named("Kx")
    Lo_late = rasp.Map(lambda l: l, Lo)
    Lo_late = Lo_late.named("Lo_late")
    Ko = rasp.SequenceMap(fk, Lo_late, clso)
    Ko = Ko.named("Ko")
    GLx = rasp.Aggregate(rasp.Select(Kx, Lx, P_group2), E)
    GLx = GLx.named("GLx")
    GLo = rasp.Aggregate(rasp.Select(Ko, Lo, P_group2), E)
    GLo = GLo.named("GLo")

    szvx = rasp.Map(lambda t: "c" if t == "x" else "d", tok)
    szvo = rasp.Map(lambda t: "c" if t == "o" else "d", tok)
    AtX0 = rasp.Aggregate(rasp.Select(idx, GLx, P_atari), atval)
    AtX0 = AtX0.named("AtX0")
    AtO0 = rasp.Aggregate(rasp.Select(idx, GLo, P_atari), atval)
    AtO0 = AtO0.named("AtO0")
    szvx2 = rasp.SequenceMap(lambda a, b: a, szvx, AtX0)
    szvo2 = rasp.SequenceMap(lambda a, b: a, szvo, AtO0)
    SZx = rasp.Aggregate(rasp.Select(Kx, Lx, P_sz), szvx2)
    SZx = SZx.named("SZx")
    SZo = rasp.Aggregate(rasp.Select(Ko, Lo, P_sz), szvo2)
    SZo = SZo.named("SZo")
    bigv = rasp.Map(lambda i: "big" if i == 0 else "small", idx)
    BIGx = rasp.Aggregate(rasp.Select(idx, SZx, P_big), bigv)
    BIGx = BIGx.named("BIGx")
    BIGo = rasp.Aggregate(rasp.Select(idx, SZo, P_big), bigv)
    BIGo = BIGo.named("BIGo")
    AtX, AtO = AtX0, AtO0
    M1x = rasp.Aggregate(rasp.Select(idx, GLx, P_minlib), idx)
    M1x = M1x.named("M1x")

    M1xc = rasp.SequenceMap(lambda m, b: m, M1x, ise)
    M1xc = M1xc.named("M1xc")
    I1x = rasp.Aggregate(rasp.Select(M1xc, idx, P_eqm), vYx)
    I1x = I1x.named("I1x")
    fe2 = lambda p, y: 81 if y == "y" else p
    Ie2x = rasp.SequenceMap(fe2, Ie, I1x)
    Ie2x = Ie2x.named("Ie2x")
    E2x = rasp.Aggregate(sel_open, Ie2x)
    E2x = E2x.named("E2x")
    GL2x = rasp.Aggregate(rasp.Select(Kx, Lx, P_group2), E2x)
    GL2x = GL2x.named("GL2x")
    T2x = rasp.Aggregate(rasp.Select(idx, GL2x, P_atari), tvx)
    T2x = T2x.named("T2x")

    def f1(t, a):
        if t == "x": return "x1" if a == "A" else "xS"
        if t == "o": return "o"
        if t == ".": return "e"
        return "edge"
    st1 = rasp.SequenceMap(f1, tok, AtX)
    st1 = st1.named("st1")
    st2 = rasp.SequenceMap(lambda s, a: ("o1" if a == "A" else "oS") if s == "o" else s, st1, AtO)
    st2 = st2.named("st2")
    st3 = rasp.SequenceMap(lambda s, b: (("x1b" if b == "big" else "x1s") if s == "x1" else s), st2, BIGx)
    st4 = rasp.SequenceMap(lambda s, b: (("o1b" if b == "big" else "o1s") if s == "o1" else s), st3, BIGo)
    def f3(s, t):
        if s == "xS": return "x2" if t == "x2" else "x3"
        if s == "oS": return "o3"
        return s
    st = rasp.SequenceMap(f3, st4, T2x)
    st = st.named("st")
    hist = rasp.Aggregate(sel_open, st)
    hist = hist.named("hist")

    vals = []
    for h in "ABC":
        tc = rasp.Map(make_tlevel(h), idx)
        T = rasp.Aggregate(rasp.Select(idx, hist, make_tpred(h)), tc)
        vals.append(rasp.numerical(rasp.Map(lambda c: (c + OFF) * SCALE, T)))
    histw = rasp.Aggregate(rasp.Select(idx, idx, P_win), tok)
    histw = histw.named("histw")
    tcW = rasp.Map(tlevelW, idx)
    TW = rasp.Aggregate(rasp.Select(idx, histw, P_tW), tcW)
    TW = TW.named("TW")
    Pn = rasp.numerical(rasp.Map(lambda c: (c + OFF) * SCALE, TW))
    S1 = rasp.numerical(rasp.LinearSequenceMap(vals[0], vals[1], 1.0, 1.0))
    S2 = rasp.numerical(rasp.LinearSequenceMap(vals[2], Pn, 1.0, 1.0))
    return rasp.numerical(rasp.LinearSequenceMap(S1, S2, 1.0, 1.0))
