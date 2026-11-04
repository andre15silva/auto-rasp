
import math
from tracr.rasp import rasp
from gocore import *
from gowin import *
from gotmpl10 import *

K_ITERS = 3

def program():
    tok, idx = rasp.tokens, rasp.indices
    isx = rasp.Map(lambda t: 1 if t == "x" else 0, tok).named("isx")
    iso = rasp.Map(lambda t: 1 if t == "o" else 0, tok).named("iso")
    ise = rasp.Map(lambda t: 1 if t == "." else 0, tok).named("ise")
    clsx = rasp.Map(lambda t: "s" if t == "x" else ("P" if t in ("B", "W") else "n"), tok).named("clsx")
    atval = rasp.Map(lambda t: "A" if t == "." else "S", tok).named("atval")
    szvx = rasp.Map(lambda t: "c" if t == "x" else "d", tok).named("szvx")
    bigv = rasp.Map(lambda i: "big" if i == 0 else "small", idx).named("bigv")
    Lft = rasp.Aggregate(rasp.Select(idx, idx, P_left), tok).named("Lft")

    f0 = lambda b, i: i if (b == 1 and i < 81) else 81
    Lx0 = rasp.SequenceMap(f0, isx, idx).named("Lx0")
    Lo0 = rasp.SequenceMap(f0, iso, idx).named("Lo0")
    rsx = rasp.SequenceMap(lambda t, l: 1 if (t == "x" and l != "x") else 0, tok, Lft).named("rsx")
    rso = rasp.SequenceMap(lambda t, l: 1 if (t == "o" and l != "o") else 0, tok, Lft).named("rso")
    RSx = rasp.SequenceMap(f0, rsx, idx).named("RSx")
    RSo = rasp.SequenceMap(f0, rso, idx).named("RSo")
    ise_late = rasp.SequenceMap(lambda a, b: a, ise, rsx).named("ise_late")
    Ie = rasp.SequenceMap(f0, ise_late, idx).named("Ie")

    sel_self = rasp.Select(idx, idx, P_selfw)
    sel_open = rasp.Select(idx, idx, P_open_proxy)
    E = rasp.Aggregate(sel_open, Ie).named("E")

    Lx = rasp.Aggregate(rasp.Select(RSx, Lx0, P_run), RSx).named("Lx_run")
    Lo = rasp.Aggregate(rasp.Select(RSo, Lo0, P_run), RSo).named("Lo_run")
    for k in range(K_ITERS):
        Hx = rasp.Aggregate(sel_self, Lx).named("Hx%d" % k)
        Ho = rasp.Aggregate(sel_self, Lo).named("Ho%d" % k)
        Lx = rasp.Aggregate(rasp.Select(idx, Hx, P_argmin), Lx).named("Lx%d" % (k + 1))
        Lo = rasp.Aggregate(rasp.Select(idx, Ho, P_argmin), Lo).named("Lo%d" % (k + 1))

    fk = lambda l, c: (l if (c == "s" and l != 81) else ("P" if c == "P" else "n"))
    Kx = rasp.SequenceMap(fk, Lx, clsx).named("Kx")
    Ko = rasp.SequenceMap(lambda l, b: l, Lo, iso).named("Ko")
    GLx = rasp.Aggregate(rasp.Select(Kx, Lx, P_group2), E).named("GLx")
    GLo = rasp.Aggregate(rasp.Select(Ko, Lo, P_group), E).named("GLo")
    SZx = rasp.Aggregate(rasp.Select(Kx, Lx, P_sz), szvx).named("SZx")
    AtX = rasp.Aggregate(rasp.Select(idx, GLx, P_atari), atval).named("AtX")
    AtO = rasp.Aggregate(rasp.Select(idx, GLo, P_atari), atval).named("AtO")
    BIGx = rasp.Aggregate(rasp.Select(idx, SZx, P_big), bigv).named("BIGx")

    def f1(t, a):
        if t == "x": return "x1" if a == "A" else "xn"
        if t == "o": return "o"
        if t == ".": return "e"
        return "edge"
    p1 = rasp.SequenceMap(f1, tok, AtX).named("p1")
    p2 = rasp.SequenceMap(lambda a, b: a + "|" + b, AtO, BIGx).named("p2")
    def fst(s, ab):
        a, b = ab.split("|")
        if s == "x1": return "x1b" if b == "big" else "x1s"
        if s == "o": return "o1s" if a == "A" else "on"
        return s
    st = rasp.SequenceMap(fst, p1, p2).named("st")
    hist = rasp.Aggregate(sel_open, st).named("hist")

    vals = []
    for h in "ABC":
        tc = rasp.Map(make_tlevel(h), idx).named("tc" + h)
        T = rasp.Aggregate(rasp.Select(idx, hist, make_tpred(h)), tc).named("T" + h)
        vals.append(rasp.numerical(rasp.Map(lambda c: (c + OFF) * SCALE, T)).named("v" + h))
    histw = rasp.Aggregate(rasp.Select(idx, idx, P_win), tok).named("histw")
    tcW = rasp.Map(tlevelW, idx).named("tcW")
    TW = rasp.Aggregate(rasp.Select(idx, histw, P_tW), tcW).named("TW")
    Pn = rasp.numerical(rasp.Map(lambda c: (c + OFF) * SCALE, TW)).named("vW")
    S1 = rasp.numerical(rasp.LinearSequenceMap(vals[0], vals[1], 1.0, 1.0)).named("S1")
    S2 = rasp.numerical(rasp.LinearSequenceMap(vals[2], Pn, 1.0, 1.0)).named("S2")
    return rasp.numerical(rasp.LinearSequenceMap(S1, S2, 1.0, 1.0)).named("out")
