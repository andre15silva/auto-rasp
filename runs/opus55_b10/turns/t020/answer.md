Compiles in 71 s, 31.8 s/1000 positions. Attention dominates (10 heads in one layer). Let me restructure to cap heads at 4 per layer (dedupe token fetches, use soft token aggregates for adjacency/influence, and schedule seeds into the empty layer-3 attention slot).

```python
s = open('/work/go.py').read()
old_start = s.index("def program():")
new_prog = r'''def program():
    tok = rasp.tokens; idx = rasp.indices
    qA = cmap(lambda i: Q(i, 'A'), idx)
    qB = cmap(lambda i: Q(i, 'B'), idx)
    # ---- runs
    ltok = rasp.Aggregate(rasp.Select(idx, qA, GT), tok)
    utok = rasp.Aggregate(rasp.Select(idx, qA, LT), tok)
    srow = smap(lambda t, l: (t not in ('x', 'o')) or (t != l), tok, ltok)
    scol = smap(lambda t, u: (t not in ('x', 'o')) or (t != u), tok, utok)
    ksr = smap(lambda i, s: i if s else 999, idx, srow)
    ksc = smap(lambda i, s: i if s else -1, idx, scol)
    ridr = rasp.SelectorWidth(rasp.Select(ksr, idx, LEQ))
    ridc = rasp.SelectorWidth(rasp.Select(ksc, qA, LEQ))
    selr = rasp.Select(ridr, ridr, EQ)
    selc = rasp.Select(ridc, ridc, EQ)
    # ---- liberty row/col sets, diffused within groups
    rowE = smap(lambda i, t: 'D' if i >= 81 else (i // 9 if t == '.' else None), idx, tok)
    colE = smap(lambda i, t: 'D' if i >= 81 else (i % 9 if t == '.' else None), idx, tok)
    qS = smap(lambda i, l: Q(i, 'A'), idx, ltok)        # same values as qA, computed one layer later
    seedsel = rasp.Select(idx, qS, GEQ)
    sr = rasp.Aggregate(seedsel, rowE)
    sc = rasp.Aggregate(seedsel, colE)
    for k in range(R_ROUNDS):
        sel = selr if k % 2 == 0 else selc
        sr = rasp.Aggregate(sel, sr)
        sc = rasp.Aggregate(sel, sc)
    nr = decode_distinct(sr, 9)
    nc = decode_distinct(sc, 9)
    def lclass(a, b):
        if a == 0 or b == 0: return 0
        if a == 1 and b == 1: return 1
        if a >= 3 or b >= 3: return 3
        return 2
    lcls = smap(lclass, nr, nc)
    def catf(l, t):
        if t == '.': return 'E'
        if t in ('x', 'o'): return ('X' if t == 'x' else 'O') + str(max(l, 1))
        return 'N'
    cst = smap(catf, lcls, tok)
    cN = rasp.Aggregate(rasp.Select(idx, qA, LT), cst)
    cS = rasp.Aggregate(rasp.Select(idx, qB, LT), cst)
    cW = rasp.Aggregate(rasp.Select(idx, qA, GT), cst)
    cE = rasp.Aggregate(rasp.Select(idx, qB, GT), cst)
    pNS = smap(lambda a, b: msum((a,), (b,)), cN, cS)
    tW = smap(lambda p, w: msum(p, (w,)), pNS, cW)
    tcat = smap(lambda t, e: tactic_score(msum(t, (e,))) + T_OFF, tW, cE)
    tact = nmap(lambda v: v, tcat)
    # ---- positional (cheap, token based)
    tadj = rasp.Aggregate(rasp.Select(idx, qA, GEQ), tok)     # soft token mix of on-board neighbours
    t2 = rasp.Aggregate(rasp.Select(idx, qB, GEQ), tok)       # soft token mix within distance 2
    def pres(col):
        return lambda v: 1.0 if v == col else (0.05 if v == 'B' else 0.0)
    thr = lambda x: int(x > 0.025)
    hasx = cmap(thr, nmap(pres('x'), tadj)); haso = cmap(thr, nmap(pres('o'), tadj))
    ex2 = cmap(thr, nmap(pres('x'), t2)); eo2 = cmap(thr, nmap(pres('o'), t2))
    adj = smap(lambda a, b: (a, b), hasx, haso)
    e2 = smap(lambda a, b: (a, b), ex2, eo2)
    lin = cmap(lambda i: 'P' if i >= 81 else line_of(i), idx)
    adjl = smap(lambda a, l: 'P' if l == 'P' else a + (l,), adj, lin)
    def pfin(e, a):
        if a == 'P': return PASS_LOGIT
        return pos_score(e[0], e[1], a[0], a[1], a[2])
    pcat = smap(lambda e, a: pfin(e, a) + P_OFF, e2, adjl)
    pos = nmap(lambda v: v, pcat)
    return add(tact, pos)
'''
s = s[:old_start] + new_prog
open('/work/go.py','w').write(s)
import sys; sys.path.insert(0,'/work'); sys.setrecursionlimit(10000)
import importlib, go, estimate
importlib.reload(go)
print(estimate.estimate(go.program()))
r = compile_program()
print({k:v for k,v in r.items() if k!='residual_labels'})
```