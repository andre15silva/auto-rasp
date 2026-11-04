The compile blowup comes from Tracr's graph extraction duplicating sources per path (cost ≈ Σ_leaves paths_down × paths_up). I validated an exact estimator for it. Let me restructure: diffuse row- and column-projections of liberty sets (9 values each), decode only 18 coordinates, and fetch neighbor categories with single routes. Let me write v2 and estimate the compile cost before compiling.

```python
src = r'''
from tracr.rasp import rasp
GT, LT, GEQ, LEQ, EQ = (rasp.Comparison.GT, rasp.Comparison.LT, rasp.Comparison.GEQ,
                        rasp.Comparison.LEQ, rasp.Comparison.EQ)
R_ROUNDS = 6
EPS = 4e-7
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
def r_nb(k, i): return k in NB[i]
def r_cmle(k, i):
    if k < 0: return False
    if k == 81 or i == 81: return k <= i
    return (k % 9, k // 9) <= (i % 9, i // 9)
def r_r2(k, i):
    if i >= 81 or k < 0 or k >= 81: return False
    return 1 <= man(k, i) <= 2
RELS = {'A': (r_left, r_up, r_nb, r_cmle),
        'B': (r_right, r_down, r_r2, r_r2)}
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

def cmap(f, x): return rasp.Map(f, x)
def nmap(f, x): return rasp.numerical(rasp.Map(f, x))
def smap(f, a, b): return rasp.SequenceMap(f, a, b)
def add(a, b, fa=1.0, fb=1.0): return rasp.numerical(rasp.LinearSequenceMap(a, b, fa, fb))
def sum_tree(xs):
    while len(xs) > 1:
        nx = [add(xs[j], xs[j+1]) for j in range(0, len(xs) - 1, 2)]
        if len(xs) % 2: nx.append(xs[-1])
        xs = nx
    return xs[0]
def decode_distinct(state, nvals):
    """state: soft categorical over 0..nvals-1 plus dummy 'D'. -> categorical count 0..3"""
    bits = []
    for c in range(nvals):
        m = nmap(lambda v, c=c: 1.0 if v == c else (EPS if v == 'D' else 0.0), state)
        bits.append(nmap(lambda x: UNIT if x > EPS / 2 else 0.0, m))
    tot = sum_tree(bits)
    return cmap(lambda x: min(3, int(round(x / UNIT))), tot)
def line_of(i):
    r, c = divmod(i, 9)
    return min(r, c, 8 - r, 8 - c)

# neighbour categories: E empty, X1/X2/X3 own stone by liberty class, O1/O2/O3, N off-board
CATS = ['E', 'X1', 'X2', 'X3', 'O1', 'O2', 'O3', 'N']
def msum(a, b):  # multiset of categories as sorted tuple
    return tuple(sorted(a + b))

PASS_LOGIT = -2.0
T_OFF = 40.0
P_OFF = 10.0
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
    kemp = smap(lambda i, t: i if t == '.' else -1, idx, tok)
    rowv = cmap(lambda i: 'D' if i >= 81 else i // 9, idx)
    colv = cmap(lambda i: 'D' if i >= 81 else i % 9, idx)
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
    seedsel = rasp.Select(kemp, qA, GEQ)
    sr = rasp.Aggregate(seedsel, rowv)
    sc = rasp.Aggregate(seedsel, colv)
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
    tN = rasp.Aggregate(rasp.Select(idx, qA, LT), tok)
    tS = rasp.Aggregate(rasp.Select(idx, qB, LT), tok)
    tW_ = rasp.Aggregate(rasp.Select(idx, qA, GT), tok)
    tE = rasp.Aggregate(rasp.Select(idx, qB, GT), tok)
    a1 = smap(lambda a, b: (int('x' in (a, b)), int('o' in (a, b))), tN, tS)
    a2 = smap(lambda a, b: (int('x' in (a, b)), int('o' in (a, b))), tW_, tE)
    adj = smap(lambda a, b: (max(a[0], b[0]), max(a[1], b[1])), a1, a2)
    isx = nmap(lambda t: 1.0 if t == 'x' else 0.0, tok)
    iso = nmap(lambda t: 1.0 if t == 'o' else 0.0, tok)
    ix2 = rasp.numerical(rasp.Aggregate(rasp.Select(idx, qB, GEQ), isx, default=0))
    io2 = rasp.numerical(rasp.Aggregate(rasp.Select(idx, qB, GEQ), iso, default=0))
    ex2 = cmap(lambda x: int(x > 0.001), ix2)
    eo2 = cmap(lambda x: int(x > 0.001), io2)
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
open('/work/go.py','w').write(src)
import sys, collections, importlib
sys.path.insert(0,'/work')
import go; importlib.reload(go)
def estimate(prog):
    order=[]; seen=set()
    def topo(e):
        if id(e) in seen: return
        seen.add(id(e))
        for c in e.children: topo(c)
        order.append(e)
    topo(prog)
    down = collections.defaultdict(int); down[id(prog)] = 1
    for e in reversed(order):
        for c in e.children: down[id(c)] += down[id(e)]
    parents = collections.defaultdict(list)
    for e in order:
        for c in e.children: parents[id(c)].append(e)
    leaves = [e for e in order if not e.children]
    tot = 0
    for L in leaves:
        cnt = collections.defaultdict(int); cnt[id(L)] = 1
        for e in order:
            if cnt[id(e)]:
                for p in parents[id(e)]: cnt[id(p)] += cnt[id(e)]
        tot += down[id(L)] * sum(cnt.values())
    return tot, len(order)
open('/work/estimate.py','w').write("import collections\n" + __import__('inspect').getsource(estimate))
print(estimate(go.program()))
```