The main early inefficiency is contested 2nd-line contact moves, and in losses our loose shapes get cut apart. I'll add (1) a game-phase signal (stone count) with phase-dependent line penalties, and (2) cutting-point detection (crosscut patterns from orthogonal + diagonal neighbor tokens). To keep ≤4 heads per layer without extra 82-dim SOps, I'll schedule new heads into idle attention slots by delaying their *value* SOps with cheap identity Maps, and derive adjacency from the four orthogonal token fetches.

```python
s = open('/work/go.py').read()
start = s.index("    tadj = rasp.Aggregate(")
end = s.index("    pos = nmap(")
new_block = r'''    # ---- positional (token based, scheduled into idle attention slots)
    rtok = rasp.Aggregate(rasp.Select(idx, qB, GT), tok)
    dtok = rasp.Aggregate(rasp.Select(idx, qB, LT), tok)
    tok_d2 = cmap(lambda t: t, cmap(lambda t: t, tok))                  # delay chain (depth 2)
    t2 = rasp.Aggregate(rasp.Select(idx, qB, GEQ), tok_d2)             # soft token mix within distance 2
    utok_d = cmap(lambda t: t, utok); dtok_d = cmap(lambda t: t, dtok)  # depth 3
    nw = rasp.Aggregate(rasp.Select(idx, qA, GT), utok_d)               # token at (r-1, c-1)
    ne = rasp.Aggregate(rasp.Select(idx, qB, GT), utok_d)               # (r-1, c+1)
    sw = rasp.Aggregate(rasp.Select(idx, qA, GT), dtok_d)               # (r+1, c-1)
    se = rasp.Aggregate(rasp.Select(idx, qB, GT), dtok_d)               # (r+1, c+1)
    def pair(a, b):
        return 'XX' if (a == 'x' and b == 'x') else ('OO' if (a == 'o' and b == 'o') else '-')
    def quad(p, dg):
        if p == 'XX' and dg == 'o': return 'our'
        if p == 'OO' and dg == 'x': return 'their'
        return '-'
    qne = smap(quad, smap(pair, utok, rtok), ne); qnw = smap(quad, smap(pair, utok, ltok), nw)
    qse = smap(quad, smap(pair, dtok, rtok), se); qsw = smap(quad, smap(pair, dtok, ltok), sw)
    def cmb(a, b):
        sa = set(a) if isinstance(a, tuple) else {a}; sb = set(b) if isinstance(b, tuple) else {b}
        return tuple(sorted((sa | sb) - {'-'}))
    cuts = smap(cmb, smap(cmb, qne, qnw), smap(cmb, qse, qsw)).named('cuts')
    def presence(a, b):
        return (int('x' in (a, b)), int('o' in (a, b)))
    adj = smap(lambda p, q: (max(p[0], q[0]), max(p[1], q[1])),
               smap(presence, ltok, rtok), smap(presence, utok, dtok))
    def dens(col):
        return lambda v: 1.0 if v == col else ({'B': 0.1, 'W': 0.4}.get(v, 0.0))
    def lev(x):
        return 0 if x < 0.05 else (1 if x < 0.25 else (2 if x < 0.7 else 3))
    nx2 = cmap(lev, nmap(dens('x'), t2)); no2 = cmap(lev, nmap(dens('o'), t2))
    e2 = smap(lambda a, b: (a, b), nx2, no2)
    sit = smap(lambda e, a: POS_CLASS[(e[0], e[1], a[0], a[1])], e2, adj)
    lin = cmap(lambda i: 'P' if i >= 81 else line_of(i), idx)
    pcat = smap(lambda c, l: PASS_LOGIT if l == 'P' else POS_ROW[c][l], sit, lin).named('pcat')
    # game phase from the number of stones on the board
    isst = nmap(lambda t: 1.0 if t in ('x', 'o') else 0.0, tok)
    isst_d = nmap(lambda v: v, nmap(lambda v: v, nmap(lambda v: v, isst)))   # delay (depth 4)
    q81 = cmap(lambda q: 81, qA)
    frac = rasp.numerical(rasp.Aggregate(rasp.Select(idx, q81, LT), isst_d, default=0))
    phase = cmap(lambda x: 0 if x < 0.16 else (1 if x < 0.4 else 2), frac).named('phase')
    contested = smap(lambda e, a: int(e[0] > 0 and e[1] > 0), e2, adj)
    lph = smap(lambda l, p: 'P' if l == 'P' else (l, p), lin, phase)
    adjcat = smap(lambda lp, cont: 0.0 if lp == 'P' else LINE_PHASE_ADJ(lp[0], lp[1], cont), lph, contested)
    cutcat = smap(lambda c, cont: CUT_VAL(c, cont), cuts, contested)
    extra = add(nmap(lambda v: v + 6.0, adjcat), nmap(lambda v: v + 3.0, cutcat))
'''
s = s[:start] + new_block + s[end:]
s = s.replace("""    pos = nmap(lambda v: v + P_OFF, pcat).named('pos')
    return add(tact, pos).named('logit')""", """    pos = add(nmap(lambda v: v + P_OFF, pcat), extra).named('pos')
    return add(tact, pos).named('logit')""")
s = s.replace("""TRIPLE_CLASS, TRIPLE_REP = build_triple_classes()""", """def LINE_PHASE_ADJ(line, phase, contested):
    if phase == 0: return {0: -2.5, 1: -1.5}.get(line, 0.0)
    if phase == 1: return {0: -1.0, 1: -0.5}.get(line, 0.0) if not contested else {0: -0.5}.get(line, 0.0)
    return 0.0
def CUT_VAL(cuts, contested):
    v = 0.0
    if 'our' in cuts: v += 1.5
    if 'their' in cuts: v += 1.2
    return v
TRIPLE_CLASS, TRIPLE_REP = build_triple_classes()""")
open('/work/go.py','w').write(s)
import sys; sys.path.insert(0,'/work'); sys.setrecursionlimit(10000)
import importlib, go, estimate
importlib.reload(go)
print(estimate.estimate(go.program()))
```