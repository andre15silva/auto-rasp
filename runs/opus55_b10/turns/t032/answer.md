Two more critical findings: (1) `rasp.Map` composes consecutive Maps by default, so my numeric thresholds were silently merged into linear categorical maps — I must use `simplify=False`; (2) when a selector matches nothing, BOS only gets ~73% weight (the rest is a board-wide average), so every selector must always match something. Let me rewrite the program with these fixes, clean (re-discretize) the run-start flags so SelectorWidth counts are exact, and split lookup tables into positive/negative parts to avoid large offsets.

```python
src = r'''
from tracr.rasp import rasp
GT, LT, GEQ, LEQ, EQ = (rasp.Comparison.GT, rasp.Comparison.LT, rasp.Comparison.GEQ,
                        rasp.Comparison.LEQ, rasp.Comparison.EQ)
R_ROUNDS = 6
EPS_DEC = 6e-4      # decode threshold is EPS_DEC/2
UNIT = 1.0 / 16

def nbrs(i):
    if i >= 81: return []
    r, c = divmod(i, 9); out = []
    for dr, dc in ((-1,0),(0,-1),(0,1),(1,0)):
        rr, cc = r+dr, c+dc
        if 0 <= rr < 9 and 0 <= cc < 9: out.append(rr*9+cc)
    return out
NB = [set(nbrs(i)) for i in range(82)]
def man(a, b): return abs(a//9 - b//9) + abs(a%9 - b%9)
def r_left(k, i):
    if i >= 81: return k == 81
    return k == (i-1 if i % 9 else 81)
def r_right(k, i):
    if i >= 81: return k == 81
    return k == (i+1 if i % 9 != 8 else 81)
def r_up(k, i):
    if i >= 81: return k == 81
    return k == (i-9 if i >= 9 else 81)
def r_down(k, i):
    if i >= 81: return k == 81
    return k == (i+9 if i < 72 else 81)
def r_nb(k, i):            # on-board neighbours; index 81 selects itself
    if i >= 81: return k == 81
    return k in NB[i]
def r_nb81(k, i):          # neighbours plus the side token (always >= 1 key)
    if i >= 81: return k == 81
    return k in NB[i] or k == 81
def r_cmle(k, i):
    if k < 0: return False
    if k == 81 or i == 81: return k <= i
    return (k % 9, k // 9) <= (i % 9, i // 9)
def r_r2(k, i):
    if i >= 81: return k == 81
    if k < 0 or k >= 81: return False
    return 1 <= man(k, i) <= 2
RELS = {'A': (r_left, r_up, r_nb, r_cmle),
        'B': (r_right, r_down, r_r2, r_nb81)}
class Q:
    __slots__ = ('i', 'k')
    def __init__(s, i, k): s.i = i; s.k = k
    def __hash__(s): return hash((s.i, s.k))
    def __eq__(s, o): return isinstance(o, Q) and s.i == o.i and s.k == o.k
    def __repr__(s): return "Q%s%d" % (s.k, s.i)
    def __lt__(s, o):   # key > query
        if isinstance(o, Q): return (s.k, s.i) < (o.k, o.i)
        return RELS[s.k][0](o, s.i)
    def __gt__(s, o):   # key < query
        if isinstance(o, Q): return (s.k, s.i) > (o.k, o.i)
        return RELS[s.k][1](o, s.i)
    def __le__(s, o):   # key >= query
        if isinstance(o, Q): return (s.k, s.i) <= (o.k, o.i)
        return RELS[s.k][2](o, s.i)
    def __ge__(s, o):   # key <= query
        if isinstance(o, Q): return (s.k, s.i) >= (o.k, o.i)
        return RELS[s.k][3](o, s.i)

def cmap(f, x): return rasp.Map(f, x, simplify=False)
def nmap(f, x): return rasp.numerical(rasp.Map(f, x, simplify=False))
def smap(f, a, b): return rasp.SequenceMap(f, a, b)
def add(a, b, fa=1.0, fb=1.0): return rasp.numerical(rasp.LinearSequenceMap(a, b, fa, fb))
def sum_tree(xs):
    while len(xs) > 1:
        nx = [add(xs[j], xs[j+1]) for j in range(0, len(xs) - 1, 2)]
        if len(xs) % 2: nx.append(xs[-1])
        xs = nx
    return xs[0]
def decode_distinct(state, nvals):
    """state: soft categorical over 0..nvals-1, 'D' (real filler) and 'Z' (never produced).
    -> categorical count (0..3) of values with mass above EPS_DEC/2"""
    bits = []
    for c in range(nvals):
        m = nmap(lambda v, c=c: 1.0 if v == c else (EPS_DEC if v == 'Z' else 0.0), state)
        bits.append(nmap(lambda x: UNIT if x > EPS_DEC / 2 else 0.0, m))
    tot = sum_tree(bits)
    return cmap(lambda x: min(3, int(round(x / UNIT))), tot)
def clean_bool(x):
    """categorical bool with soft magnitude -> exact one-hot bool"""
    return cmap(lambda v: v > 0.5, nmap(lambda b: 1.0 if b else 0.0, x))
def line_of(i):
    r, c = divmod(i, 9)
    return min(r, c, 8 - r, 8 - c)
def msum(a, b): return tuple(sorted(a + b))
def split_num(catsop):
    """categorical SOp with numeric values -> numeric SOp (via positive & negative parts)"""
    p = nmap(lambda v: max(v, 0.0), catsop)
    n = nmap(lambda v: max(-v, 0.0), catsop)
    return add(p, n, 1.0, -1.0)

PASS_LOGIT = -2.0
LINE_VAL = {0: -1.5, 1: -0.5, 2: 0.8, 3: 0.6, 4: 1.0}

def tactic_score(ms):
    """ms: sorted tuple of the 4 neighbour categories."""
    if all(c == 'N' for c in ms): return 0.0          # pass position (index 81)
    nO1 = ms.count('O1'); nE = ms.count('E'); nN = ms.count('N')
    xs = [int(c[1]) for c in ms if c[0] == 'X']
    aX1 = 1 in xs; aX2 = 2 in xs
    aO2 = 'O2' in ms; aO3 = 'O3' in ms
    cap = nO1 > 0
    if not xs:
        lo = hi = nE
    else:
        lo = max(nE, max(xs) - 1)
        hi = nE + sum(x - 1 for x in xs)
    if cap:
        lo = max(lo, 2); hi = max(hi, 2)
    s = 0.0
    if cap: s += 10.0 + 2.0 * (min(nO1, 2) - 1)
    safe = lo >= 2
    sa = hi <= 1
    if sa: s -= 12.0
    elif not safe: s -= 3.0
    if aX1:
        if safe: s += 9.0 + (1.0 if lo >= 3 else 0.0)
        elif not sa: s += 4.0
    if aO2 and safe: s += 4.0
    if aX2 and lo >= 3: s += 2.5
    if aO3 and safe: s += 0.5
    eye = (len(xs) + nN == 4)
    if eye and not cap and not (aX1 and safe): s -= 15.0
    return s

def pos_score(ex2, eo2, hasx, haso, line):
    if hasx and haso: s = 1.5
    elif haso: s = 1.0 if ex2 else 0.3
    elif hasx: s = 0.3 if eo2 else -3.0
    else:
        if ex2 and eo2: s = 1.2
        elif ex2: s = -0.8
        elif eo2: s = 0.2
        else: s = LINE_VAL[line] + 1.0
    s += {0: -1.0, 1: -0.3, 2: 0.0, 3: 0.0, 4: 0.0}[line]
    return s

def program():
    tok = rasp.tokens; idx = rasp.indices
    qA = cmap(lambda i: Q(i, 'A'), idx)
    qB = cmap(lambda i: Q(i, 'B'), idx)
    # ---- runs (exact start flags -> exact SelectorWidth counts)
    ltok = rasp.Aggregate(rasp.Select(idx, qA, GT), tok)
    utok = rasp.Aggregate(rasp.Select(idx, qA, LT), tok)
    srow = clean_bool(smap(lambda t, l: (t not in ('x', 'o')) or (t != l), tok, ltok))
    scol = clean_bool(smap(lambda t, u: (t not in ('x', 'o')) or (t != u), tok, utok))
    ksr = smap(lambda i, s: i if s else 999, idx, srow)
    ksc = smap(lambda i, s: i if s else -1, idx, scol)
    ridr = rasp.SelectorWidth(rasp.Select(ksr, idx, LEQ)).named('ridr')
    ridc = rasp.SelectorWidth(rasp.Select(ksc, qA, LEQ)).named('ridc')
    selr = rasp.Select(ridr, ridr, EQ)
    selc = rasp.Select(ridc, ridc, EQ)
    # ---- liberty row/col sets, diffused within groups
    def rowEf(i, t):
        if i >= 81: return 'Z' if t == '.' else 'D'
        return i // 9 if t == '.' else None
    def colEf(i, t):
        if i >= 81: return 'Z' if t == '.' else 'D'
        return i % 9 if t == '.' else None
    rowE = smap(rowEf, idx, tok)
    colE = smap(colEf, idx, tok)
    seedsel = rasp.Select(idx, qB, LEQ)          # neighbours + index 81
    stonly = lambda v, t: v if t in ('x', 'o') else 'D'
    sr = smap(stonly, rasp.Aggregate(seedsel, rowE), tok).named('seed_r')
    sc = smap(stonly, rasp.Aggregate(seedsel, colE), tok).named('seed_c')
    for k in range(R_ROUNDS):
        sel = selr if k % 2 == 0 else selc
        sr = rasp.Aggregate(sel, sr).named('sr%d' % k)
        sc = rasp.Aggregate(sel, sc).named('sc%d' % k)
    nr = decode_distinct(sr, 9).named('nr')
    nc = decode_distinct(sc, 9).named('nc')
    def lclass(a, b):
        if a == 0 or b == 0: return 0
        if a == 1 and b == 1: return 1
        if a >= 3 or b >= 3: return 3
        return 2
    lcls = smap(lclass, nr, nc).named('lcls')
    def catf(l, t):
        if t == '.': return 'E'
        if t in ('x', 'o'): return ('X' if t == 'x' else 'O') + str(max(l, 1))
        return 'N'
    cst = smap(catf, lcls, tok).named('cst')
    cN = rasp.Aggregate(rasp.Select(idx, qA, LT), cst).named('cN')
    cS = rasp.Aggregate(rasp.Select(idx, qB, LT), cst).named('cS')
    cW = rasp.Aggregate(rasp.Select(idx, qA, GT), cst).named('cW')
    cE = rasp.Aggregate(rasp.Select(idx, qB, GT), cst).named('cE')
    pNS = smap(lambda a, b: msum((a,), (b,)), cN, cS)
    tW = smap(lambda p, w: msum(p, (w,)), pNS, cW)
    tcat = smap(lambda t, e: tactic_score(msum(t, (e,))), tW, cE).named('tcat')
    tact = split_num(tcat).named('tact')
    # ---- positional (cheap, token based)
    tadj = rasp.Aggregate(rasp.Select(idx, qA, GEQ), tok)     # soft token mix of on-board neighbours
    t2 = rasp.Aggregate(rasp.Select(idx, qB, GEQ), tok)       # soft token mix within distance 2
    def pres(col):
        return lambda v: 1.0 if v == col else (0.05 if v == 'W' else 0.0)
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
    pcat = smap(pfin, e2, adjl).named('pcat')
    pos = split_num(pcat).named('pos')
    return add(tact, pos).named('logit')
'''
open('/work/go.py','w').write(src)
import sys; sys.path.insert(0,'/work'); sys.setrecursionlimit(10000)
import importlib, go, estimate
importlib.reload(go)
print(estimate.estimate(go.program()))
r = compile_program()
print({k:v for k,v in r.items() if k!='residual_labels'})
```