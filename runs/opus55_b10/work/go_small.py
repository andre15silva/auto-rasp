
from tracr.rasp import rasp
GT, LT, GEQ, LEQ, EQ = (rasp.Comparison.GT, rasp.Comparison.LT, rasp.Comparison.GEQ,
                        rasp.Comparison.LEQ, rasp.Comparison.EQ)
R_ROUNDS = 6
EPS = 4e-7          # dummy value for decode thresholds
UNIT = 1.0 / 128    # one liberty in decode sums

def nbrs(i):
    if i >= 81: return []
    r, c = divmod(i, 9); out = []
    for dr, dc in ((-1,0),(0,-1),(0,1),(1,0)):
        rr, cc = r+dr, c+dc
        if 0 <= rr < 9 and 0 <= cc < 9: out.append(rr*9+cc)
    return out
NB = [set(nbrs(i)) for i in range(82)]
def man(a, b):
    return abs(a//9 - b//9) + abs(a%9 - b%9)
def r_left(k, i):
    if i >= 81: return k == 81
    return k == (i-1 if i % 9 else 81)
def r_up(k, i):
    if i >= 81: return k == 81
    return k == (i-9 if i >= 9 else 81)
def r_nb(k, i): return k in NB[i]
def r_cmle(k, i):
    if k < 0: return False
    if k == 81 or i == 81: return k <= i
    return (k % 9, k // 9) <= (i % 9, i // 9)
def r_r2(k, i):
    if i >= 81 or k < 0 or k >= 81: return False
    return 1 <= man(k, i) <= 2
def r_all(k, i): return 0 <= k < 81
def r_false(k, i): return False
def r_self(k, i): return k == i
RELS = {'A': (r_left, r_up, r_nb, r_cmle),
        'B': (r_r2, r_all, r_false, r_false),
        'S': (r_false, r_false, r_nb, r_false),
        'E': (r_false, r_false, r_self, r_false)}
class Q:
    __slots__ = ('i', 'k')
    def __init__(s, i, k): s.i = i; s.k = k
    def __hash__(s): return hash((s.i, s.k))
    def __eq__(s, o): return isinstance(o, Q) and s.i == o.i and s.k == o.k
    def __repr__(s): return "Q%s%d" % (s.k, s.i)
    def __lt__(s, o):   # evaluated for  key > query
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

def num(x): return rasp.numerical(x)
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

def decode_count(state):
    """state: soft categorical over values 0..81 (81 = never-used dummy).
    returns numeric = UNIT * (number of coordinates 0..80 with positive mass)."""
    bits = []
    for c in range(20):
        m = nmap(lambda v, c=c: 1.0 if v == c else (EPS if v == 81 else 0.0), state)
        b = nmap(lambda x: UNIT if x > EPS / 2 else 0.0, m)
        bits.append(b)
    return sum_tree(bits)

def cnt_cat(x):  # numeric count in UNITs -> 0,1,2,3(+)
    return min(3, int(round(x / UNIT)))

def line_of(i):
    r, c = divmod(i, 9)
    return min(r, c, 8 - r, 8 - c)

# ---------------- scoring tables (logits) ----------------
PASS_LOGIT = -2.0
T_OFF = 40.0
P_OFF = 10.0
LINE_VAL = {0: -1.5, 1: -0.5, 2: 0.8, 3: 0.6, 4: 1.0}
def tactic_score(capN, save, athr, ext, red, nl, eye):
    s = 0.0
    if capN > 0:
        s += 10.0 + 2.0 * (capN - 1)
    elif nl <= 1:
        s -= 12.0
    if save and nl >= 2:
        s += 9.0 + (1.0 if nl >= 3 else 0.0)
    if athr and nl >= 2:
        s += 4.0
    if ext and nl >= 3:
        s += 2.5
    if red and nl >= 2:
        s += 0.5
    if eye and not (save and nl >= 2) and capN == 0:
        s -= 15.0
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
    qS = smap(lambda i, t: Q(i, 'S' if t in ('x', 'o') else 'E'), idx, tok)
    kemp = smap(lambda i, t: i if t == '.' else -1, idx, tok)
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
    # ---- liberty-set diffusion
    s = rasp.Aggregate(rasp.Select(kemp, qS, GEQ), idx)
    for k in range(R_ROUNDS):
        s = rasp.Aggregate(selr if k % 2 == 0 else selc, s)
    libs = decode_count(s)
    libcat = cmap(cnt_cat, libs)
    # union of own groups' liberties and empty neighbours, seen from each point
    z = smap(lambda v, t: v if t in ('x', '.') else None, s, tok)
    U = rasp.Aggregate(rasp.Select(idx, qA, GEQ), z)
    ucount = decode_count(U)
    ucat = cmap(cnt_cat, ucount)
    # ---- stone categories and neighbourhood fractions
    DUM = {('.', 0): 'D1', ('.', 2): 'D2', ('.', 3): 'D3', ('B', 1): 'D4', ('B', 2): 'D5'}
    def catf(l, t):
        if (t, l) in DUM: return DUM[(t, l)]
        if t == '.': return 'E'
        if t == 'x': return 'N' if l == 0 else 'X%d' % l
        if t == 'o': return 'N' if l == 0 else 'O%d' % l
        return 'N'
    cst = smap(catf, libcat, tok)
    cnb = rasp.Aggregate(rasp.Select(idx, qA, GEQ), cst)
    DV = {'D1': 0.25, 'D2': 1/3, 'D3': 0.5, 'D4': 2/3, 'D5': 0.75}
    FR = [0.0, 0.25, 1/3, 0.5, 2/3, 0.75, 1.0]
    def frac_feature(S):
        m = nmap(lambda v: 1.0 if v in S else DV.get(v, 0.0), cnb)
        return cmap(lambda x: min(range(7), key=lambda j: abs(FR[j] - x)), m)
    fO1 = frac_feature({'O1'}); fX1 = frac_feature({'X1'}); fO2 = frac_feature({'O2'})
    fX2 = frac_feature({'X2'}); fO3 = frac_feature({'O3'})
    fX = frac_feature({'X1', 'X2', 'X3'}); fO = frac_feature({'O1', 'O2', 'O3'})
    ptype = cmap(lambda i: 'P' if i >= 81 else len(NB[i]), idx)
    def capf(fj, pt):
        if pt == 'P': return 'P'
        return min(2, int(round(FR[fj] * pt)))
    capN = smap(capf, fO1, ptype)
    # ---- tactical class
    a1 = smap(lambda c, s: 'P' if c == 'P' else (c, int(s > 0)), capN, fX1)
    a2 = smap(lambda x, y: (int(x > 0), int(y > 0)), fO2, fX2)
    hasx = cmap(lambda j: int(j > 0), fX)
    nl0 = smap(lambda u, h: max(0, u - h), ucat, hasx)
    eye = cmap(lambda j: int(j == 6), fX)
    a3 = smap(lambda n, e: (n, e), nl0, eye)
    b1 = smap(lambda a, b: 'P' if a == 'P' else a + b, a1, a2)
    b2 = smap(lambda a, r: a + (int(r > 0),), a3, fO3)
    def tfin(b, c):
        if b == 'P': return 0.0
        capn, sv, at, ex = b
        n0, ey, rd = c
        nl = min(3, n0 + capn)
        return tactic_score(capn, sv, at, ex, rd, nl, ey)
    tcat = smap(lambda b, c: tfin(b, c) + T_OFF, b1, b2)
    tact = nmap(lambda v: v, tcat)
    # ---- positional
    isx = nmap(lambda t: 1.0 if t == 'x' else 0.0, tok)
    iso = nmap(lambda t: 1.0 if t == 'o' else 0.0, tok)
    ix2 = num(rasp.Aggregate(rasp.Select(idx, qB, GT), isx, default=0))
    io2 = num(rasp.Aggregate(rasp.Select(idx, qB, GT), iso, default=0))
    ex2 = cmap(lambda x: int(x > 0.001), ix2)
    eo2 = cmap(lambda x: int(x > 0.001), io2)
    e2 = smap(lambda a, b: (a, b), ex2, eo2)
    adj = smap(lambda a, b: (int(a > 0), int(b > 0)), fX, fO)
    lin = cmap(lambda i: 'P' if i >= 81 else line_of(i), idx)
    adjl = smap(lambda a, l: 'P' if l == 'P' else a + (l,), adj, lin)
    def pfin(e, a):
        if a == 'P': return PASS_LOGIT
        return pos_score(e[0], e[1], a[0], a[1], a[2])
    pcat = smap(lambda e, a: pfin(e, a) + P_OFF, e2, adjl)
    pos = nmap(lambda v: v, pcat)
    return add(tact, pos)
