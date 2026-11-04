
from tracr.rasp import rasp
GT, LT, GEQ, LEQ, EQ = (rasp.Comparison.GT, rasp.Comparison.LT, rasp.Comparison.GEQ,
                        rasp.Comparison.LEQ, rasp.Comparison.EQ)
R_ROUNDS = 6
EPS_DEC = 8e-5      # decode threshold is EPS_DEC/2
NEAR_N = 30        # keys averaged for the near-one constant (theta = BOS share)
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
        'B': (r_right, r_down, r_r2, r_nb81),
        'C': (r_nb, r_r2, r_nb, r_nb)}
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
def decode_bits(state, nvals):
    bits = []
    for c in range(nvals):
        m = nmap(lambda v, c=c: 1.0 if v == c else (EPS_DEC if v == 'Z' else 0.0), state)
        bits.append(nmap(lambda x: UNIT if x > EPS_DEC / 2 else 0.0, m))
    return bits
def decode_distinct(state, nvals):
    """state: soft categorical over 0..nvals-1, 'D' (real filler) and 'Z' (never produced).
    -> categorical count (0..3) of values with mass above EPS_DEC/2"""
    tot = sum_tree(decode_bits(state, nvals))
    return cmap(lambda x: min(3, int(round(x / UNIT))), tot)
COLCODE = {'.': 0, 'x': 16, 'o': 32, 'B': 48, 'W': 48}
def clean_bool(x):
    """categorical bool with soft magnitude -> exact one-hot bool"""
    return cmap(lambda v: v > 0.5, nmap(lambda b: 1.0 if b else 0.0, x))
def line_of(i):
    r, c = divmod(i, 9)
    return min(r, c, 8 - r, 8 - c)
def msum(a, b): return tuple(sorted(a + b))
CATS = ['E', 'X1', 'X2', 'X3', 'O1', 'O2', 'O3', 'N']
def clean_cat(c):
    x = nmap(lambda v: 0.1 * CATS.index(v), c)
    return cmap(lambda y: CATS[min(7, max(0, int(round(y / 0.1))))], x)
T_OFF = 20.0
def split_num(catsop):
    """categorical SOp with numeric values -> numeric SOp (via positive & negative parts)"""
    p = nmap(lambda v: max(v, 0.0), catsop)
    n = nmap(lambda v: max(-v, 0.0), catsop)
    return add(p, n, 1.0, -1.0)

PASS_LOGIT = -2.0
P_OFF = 8.0
def build_triple_classes():
    import itertools
    triples = sorted({tuple(sorted(t)) for t in itertools.product(CATS, repeat=3)})
    sig = {}
    for t in triples:
        key = tuple(tactic_score(msum(t, (e,))) for e in CATS)
        sig.setdefault(key, []).append(t)
    cls, rep = {}, {}
    for k, (key, ts) in enumerate(sorted(sig.items())):
        rep[k] = ts[0]
        for t in ts: cls[t] = k
    return cls, rep
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
        if safe: s += 10.0 if lo >= 3 else 7.0
        elif not sa: s += 3.0
    if aO2 and safe: s += 4.0
    if aX2 and lo >= 3: s += 2.5
    if aO3 and safe: s += 0.5
    eye = (len(xs) + nN == 4)
    if eye and not cap and not (aX1 and safe): s -= 15.0
    return s

LINE_OPEN = {0: -1.5, 1: 0.0, 2: 2.5, 3: 2.8, 4: 3.5}
def pos_score(nx2, no2, ax, ao, line):
    """nx2/no2: density level (0 none, 1 low, 2 mid, 3 high) of own/opponent stones within
    Manhattan distance 2; ax/ao: adjacent own/opponent stone present; line: distance to edge."""
    edge = {0: -3.0, 1: -1.2}.get(line, 0.0)
    if nx2 == 0 and no2 == 0:                  # open area
        return LINE_OPEN[line]
    if no2 == 0:                               # own sphere only
        if ax: return -5.0
        return (0.5 if nx2 == 1 else -3.0) + edge
    if nx2 == 0:                               # opponent sphere only
        if ao: return (0.0 if no2 == 1 else -3.5) + edge
        return (1.5 if no2 == 1 else -2.5) + edge
    s = 3.0                                    # contested
    if ax and ao: s += 1.0
    elif ao: s += 0.8
    elif ax: s += 0.3
    if nx2 >= 2 and no2 <= 1: s -= 0.5         # mostly ours already
    if no2 >= 2 and nx2 <= 1: s += 0.3         # pushing into their side
    return s + {0: -1.5, 1: -0.5}.get(line, 0.0)

TRIPLE_CLASS, TRIPLE_REP = build_triple_classes()
def build_pos_classes():
    cls, rows = {}, {}
    sig = {}
    for a in range(4):
        for b in range(4):
            for c in range(2):
                for d in range(2):
                    key = tuple(pos_score(a, b, c, d, l) for l in range(5))
                    sig.setdefault(key, []).append((a, b, c, d))
    for k, (key, members) in enumerate(sorted(sig.items())):
        rows[k] = key
        for m in members: cls[m] = k
    return cls, rows
POS_CLASS, POS_ROW = build_pos_classes()

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
    rowv = cmap(lambda i: 'P' if i >= 81 else i // 9, idx)
    colv = cmap(lambda i: 'P' if i >= 81 else i % 9, idx)
    def rcEf(v, t):
        if v == 'P': return 'Z' if t == '.' else 'D'
        return v if t == '.' else None
    rowE = smap(rcEf, rowv, tok)
    colE = smap(rcEf, colv, tok)
    seedsel = rasp.Select(idx, qB, LEQ)          # neighbours + index 81
    # near-one constant: one-hot 'c' with magnitude 1 - theta (theta = BOS attention share)
    constc = cmap(lambda i: 'c', idx)
    nq = cmap(lambda q: NEAR_N, qA)               # delayed one layer (spreads heads)
    nearone = rasp.Aggregate(rasp.Select(idx, nq, LT), constc).named('nearone')
    cleanf = lambda v, c: v
    def clean(x): return smap(cleanf, x, nearone)
    stonly = lambda v, t: v if t in ('x', 'o') else 'D'
    sr = clean(smap(stonly, rasp.Aggregate(seedsel, rowE), tok)).named('seed_r')
    sc = clean(smap(stonly, rasp.Aggregate(seedsel, colE), tok)).named('seed_c')
    for k in range(R_ROUNDS):
        sel = selr if k % 2 == 0 else selc
        sr = clean(rasp.Aggregate(sel, sr)).named('sr%d' % k)
        sc = clean(rasp.Aggregate(sel, sc)).named('sc%d' % k)
    colnum = nmap(lambda t: COLCODE[t] * UNIT, tok)
    nrc = cmap(lambda x: (int(round(x / UNIT)) // 16, min(3, int(round(x / UNIT)) % 16)),
               sum_tree(decode_bits(sr, 9) + [colnum])).named('nrc')
    nc = decode_distinct(sc, 9).named('nc')
    def lclass(a, b):
        if a == 0 or b == 0: return 0
        if a == 1 and b == 1: return 1
        if a >= 3 or b >= 3: return 3
        return 2
    def catf(cr, b):
        col, a = cr
        if col == 0: return 'E'
        if col in (1, 2): return ('X' if col == 1 else 'O') + str(max(lclass(a, b), 1))
        return 'N'
    cst = smap(catf, nrc, nc).named('cst')
    cN = rasp.Aggregate(rasp.Select(idx, qA, LT), cst).named('cN')
    cS = rasp.Aggregate(rasp.Select(idx, qB, LT), cst).named('cS')
    cW = rasp.Aggregate(rasp.Select(idx, qA, GT), cst).named('cW')
    cE = rasp.Aggregate(rasp.Select(idx, qB, GT), cst).named('cE')
    pNS = smap(lambda a, b: msum((a,), (b,)), cN, cS)
    tW = smap(lambda p, w: TRIPLE_CLASS[msum(p, (w,))], pNS, cW)
    tcat = smap(lambda t, e: max(-20.0, tactic_score(msum(TRIPLE_REP[t], (e,)))), tW, cE).named('tcat')
    tact = nmap(lambda v: v + T_OFF, tcat).named('tact')
    # ---- positional (cheap, token based)
    tadj = rasp.Aggregate(rasp.Select(idx, qA, GEQ), tok)     # soft token mix of on-board neighbours
    t2 = rasp.Aggregate(rasp.Select(idx, qB, GEQ), tok)       # soft token mix within distance 2
    def pres(col):
        return lambda v: 1.0 if v == col else (0.05 if v == 'W' else 0.0)
    thr = lambda x: int(x > 0.025)
    hasx = cmap(thr, nmap(pres('x'), tadj)); haso = cmap(thr, nmap(pres('o'), tadj))
    def dens(col):
        return lambda v: 1.0 if v == col else ({'B': 0.1, 'W': 0.4}.get(v, 0.0))
    def lev(x):
        return 0 if x < 0.05 else (1 if x < 0.25 else (2 if x < 0.7 else 3))
    nx2 = cmap(lev, nmap(dens('x'), t2)); no2 = cmap(lev, nmap(dens('o'), t2))
    adj = smap(lambda a, b: (a, b), hasx, haso)
    e2 = smap(lambda a, b: (a, b), nx2, no2)
    sit = smap(lambda e, a: POS_CLASS[(e[0], e[1], a[0], a[1])], e2, adj)
    lin = cmap(lambda i: 'P' if i >= 81 else line_of(i), idx)
    pcat = smap(lambda c, l: PASS_LOGIT if l == 'P' else POS_ROW[c][l], sit, lin).named('pcat')
    pos = nmap(lambda v: v + P_OFF, pcat).named('pos')
    return add(tact, pos).named('logit')
