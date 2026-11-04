
from tracr.rasp import rasp
import math, itertools

MLP_EXACTNESS = 100
NCLS = 13
T_HOPS = 6
F_HOPS = 4
FGAIN = 2000.0
BIG = 1e6

def rc(i): return divmod(i, 9)
def _nbrs(i):
    r, c = divmod(i, 9); out = []
    for dr, dc in ((-1,0),(1,0),(0,-1),(0,1)):
        if 0 <= r+dr < 9 and 0 <= c+dc < 9: out.append((r+dr)*9 + c+dc)
    return out
NB = [_nbrs(i) for i in range(81)]
def cls(i):
    r, c = divmod(i, 9); return (r + 5*c) % NCLS
PAIRS = list(itertools.combinations(range(NCLS), 2))
NPAIR = len(PAIRS)

FSC = math.sqrt(84.0)
def mksel(keys, queries, design):
    def p(k, q):
        v = design(k, q)
        if v is None or v is False: return -FSC
        if v is True: return FSC
        return FSC * float(v)
    return rasp.Select(keys, queries, p)
def cat(x): return rasp.categorical(x)
def num(x): return rasp.numerical(x)

def sel_open():
    return mksel(rasp.indices, rasp.indices, lambda k, q: (k == 81) if q >= 81 else (k in NB[q]))
def sel_closed():
    return mksel(rasp.indices, rasp.indices, lambda k, q: (k == 81) if q >= 81 else (k == q or k in NB[q]))
def sel_hist():
    def p(k, q):
        if q >= 81: return 1.0 if k == 81 else None
        if k in NB[q]: return 1.0
        if k == 81 and len(NB[q]) < 4: return 1.0 + math.log(4 - len(NB[q])) / 100
        return None
    return mksel(rasp.indices, rasp.indices, p)
def kern(q, k, s):
    r1, c1 = divmod(q, 9); r2, c2 = divmod(k, 9)
    return math.exp(-((r1-r2)**2 + (c1-c2)**2) / (2*s*s))
def sel_kernel(s, cutoff=0.02, pad=False):
    Wq = [sum(kern(q, k, s) for k in range(81) if kern(q, k, s) >= cutoff) for q in range(81)]
    S = max(Wq) + 0.05
    def p(k, q):
        if q >= 81: return 1.0 if k == 81 else None
        if k >= 81:
            return (1.0 + math.log(S - Wq[q]) / 100) if pad else None
        w = kern(q, k, s)
        if w < cutoff: return None
        return 1.0 + math.log(w) / 100
    return mksel(rasp.indices, rasp.indices, p)

# ---------- readout predicates (query = class mixture, key = index role) ----------
def pred_single(k, q):
    if k < NCLS:
        if q == 'n': return 1.0
        return 1.0 if q[1] == k else -BIG
    if k == NCLS: return 0.7
    return None
def pred_pair(k, q):
    if k < NPAIR:
        if q == 'n': return 1.0
        return 1.0 if q[1] in PAIRS[k] else -BIG
    if k == NPAIR: return 0.7
    return None
def pred_upair(k, q):
    if k < NPAIR:
        if q == 'n' or q[0] == 'O': return 1.0
        return 1.0 if q[1] in PAIRS[k] else -BIG
    if k == NPAIR: return 0.7
    return None

# ---------- neighbour multiset prototypes ----------
CATS = ['E', 'P', 'X', 'O1', 'Om']
def catof(v):
    if v in ('X1s', 'X1b', 'Xm'): return 'X'
    if v in ('O1s', 'O1b'): return 'O1'
    return v
PROTOS = [t for t in itertools.product(range(5), repeat=5) if sum(t) == 4 and t[1] <= 2]
C1 = 2.0
def labelA(t):
    nE, nP, nX, nO1, nOm = t
    return (min(nO1, 2), int(nX >= 1), int(nX >= 1 and nX + nP == 4), min(nE, 2))
def pred_proto(k, q):
    if k > len(PROTOS): return None
    if k == len(PROTOS): t = (0, 4, 0, 0, 0)
    else: t = PROTOS[k]
    m = [x / 4 for x in t]
    sq = sum(x * x for x in m)
    c = catof(q)
    if c not in CATS: return 0.5
    return C1 * (2 * m[CATS.index(c)] - sq) + 0.5
def pred_yes(target):
    def p(k, q):
        if k == 0: return 3.3 if q == target else 0.1
        if k == 1: return 0.6
        return None
    return p

PROTOS_B = [t for t in itertools.product(range(5), repeat=4) if sum(t) == 4]
def catB(v):
    if v in ('O2s', 'O2b'): return 'O2'
    if v in ('X2s', 'X2b'): return 'X2'
    return v if v == 'X3' else 'R'
CATSB = ['O2', 'X2', 'X3', 'R']
def pred_protoB(k, q):
    if k > len(PROTOS_B): return None
    t = PROTOS_B[k] if k < len(PROTOS_B) else (0, 0, 0, 4)
    m = [x / 4 for x in t]
    sq = sum(x * x for x in m)
    return C1 * (2 * m[CATSB.index(catB(q))] - sq) + 0.5
def labelB(k):
    t = PROTOS_B[k] if k < len(PROTOS_B) else (0, 0, 0, 4)
    return (int(t[0] >= 1), int(t[1] >= 1), int(t[2] >= 1))

def mkproto(cats, catfn, labfn, default):
    protos = [t for t in itertools.product(range(5), repeat=len(cats)) if sum(t) == 4]
    def pred(k, q):
        if k > len(protos): return None
        t = protos[k] if k < len(protos) else default
        m = [x / 4 for x in t]
        sq = sum(x * x for x in m)
        return C1 * (2 * m[cats.index(catfn(q))] - sq) + 0.5
    def lab(k):
        t = protos[k] if k < len(protos) else default
        return labfn(t)
    return pred, lab, len(protos)
def _catAb(v):
    return v if v in ('X1s', 'X1b', 'O1b') else 'R'
pred_protoAb, labelAb, NPAb = mkproto(['X1s', 'X1b', 'O1b', 'R'], _catAb, lambda t: (int(t[0] + t[1] >= 1), int(t[1] >= 1), int(t[2] >= 1)), (0, 0, 0, 4))
def _catBb(v):
    return v if v in ('X2b', 'O2b') else 'R'
pred_protoBb, labelBb, NPBb = mkproto(['X2b', 'O2b', 'R'], _catBb, lambda t: (int(t[0] >= 1), int(t[1] >= 1)), (0, 0, 4))

ZCENT = [-0.3, -0.13, 0.0, 0.13, 0.3]
ZNAMES = ['pS', 'pW', 'neu', 'oW', 'oS']
ZZ = 50.0
def pred_zone(k, q):
    if k >= len(ZCENT): return None
    f = {'X': 1.0, 'O': -1.0}.get(q, 0.0)
    c = ZCENT[k]
    return 0.6 + ZZ * (2 * c * f - c * c)

def LV(i):
    if i >= 81: return 0.0
    r, c = divmod(i, 9)
    e = min(r, c, 8 - r, 8 - c)
    return 10.0 + [-2.0, -0.5, 0.5, 0.7, 1.0][e]

TAC_CAP1, TAC_CAP2, TAC_EYE, TAC_SA, TAC_ESC, TAC_ATK, TAC_DEF = 14, 18, -25, -20, 6, 1, 2
BIG_CAP, BIG_ESC, BIG_DEF, BIG_ATK = 10, 14, 6, 4
PASSV = 0.0
GAINW = 8.0
DANGW = 20.0
SCALE = 3.0
SA_OPP_BONUS = 16.0
GAINF = {'neu': 1.0, 'pW': 0.7, 'pS': 0.25, 'oW': 0.6, 'oS': 0.1}

def program():
    tok, idx = rasp.tokens, rasp.indices
    kind = cat(rasp.Map(lambda t: {'.': 'E', 'x': 'X', 'o': 'O'}.get(t, 'P'), tok)).named('kind')
    def ek(t, i):
        if i >= 81 or t not in ('.', 'x', 'o'): return 'P'
        if t == 'x': return 'X'
        if t == 'o': return 'O'
        return cls(i)
    ekind = cat(rasp.SequenceMap(ek, tok, idx)).named('ekind')
    # value maps on indices
    rv1 = cat(rasp.Map(lambda k: 'c1' if k < NCLS else 'c0', idx)).named('rv1')
    rv2 = cat(rasp.Map(lambda k: 'c2' if k < NPAIR else 'c0', idx)).named('rv2')
    rvu = cat(rasp.Map(lambda k: 'lo' if k < NPAIR else 'hi', idx)).named('rvu')
    labmap = cat(rasp.Map(lambda k: labelA(PROTOS[k]) if k < len(PROTOS) else (0, 0, 0, 2), idx)).named('labmap')
    labBmap = cat(rasp.Map(lambda k: labelB(k) if k <= len(PROTOS_B) else (0, 0, 0), idx)).named('labBmap')
    labAbmap = cat(rasp.Map(lambda k: labelAb(k) if k <= NPAb else (0, 0, 0), idx)).named('labAbmap')
    labBbmap = cat(rasp.Map(lambda k: labelBb(k) if k <= NPBb else (0, 0), idx)).named('labBbmap')
    ynmap = cat(rasp.Map(lambda k: 'yes' if k == 0 else 'no', idx)).named('ynmap')
    zmap = cat(rasp.Map(lambda k: ZNAMES[k] if k < len(ZNAMES) else 'neu', idx)).named('zmap')
    linev = num(rasp.Map(LV, idx)).named('linev')

    # ---------- liberty-class propagation ----------
    M0 = cat(rasp.Aggregate(sel_open(), ekind)).named('M0')
    def f0(kd, v):
        if kd in ('X', 'O') and isinstance(v, int): return (kd, v)
        return 'n'
    T = cat(rasp.SequenceMap(f0, kind, M0)).named('T0')
    def fmask(kd, v):
        if v != 'n' and v[0] == kd: return v
        return 'n'
    for t in range(1, T_HOPS):
        A = cat(rasp.Aggregate(sel_closed(), T)).named(f'A{t}')
        T = cat(rasp.SequenceMap(fmask, kind, A)).named(f'T{t}')
    A = cat(rasp.Aggregate(sel_closed(), T)).named(f'A{T_HOPS}')
    def fW(e, v):
        if e in ('X', 'O'):
            return v if (v != 'n' and v[0] == e) else 'n'
        if isinstance(e, int): return ('X', e)
        return 'n'
    W = cat(rasp.SequenceMap(fW, ekind, A)).named('W')

    RS1 = cat(rasp.Aggregate(mksel(idx, W, pred_single), rv1)).named('RS1')
    RS2 = cat(rasp.Aggregate(mksel(idx, W, pred_pair), rv2)).named('RS2')
    U = cat(rasp.Aggregate(sel_open(), W)).named('U')
    RU = cat(rasp.Aggregate(mksel(idx, U, pred_upair), rvu)).named('RU')

    # ---- far-liberty flags: a stone seeing >=2 (>=3) classes flags its chain ----
    def fflag(kd, r):
        if kd in ('X', 'O') and r == 'c0': return (kd, 'F')
        return 'n'
    G2 = cat(rasp.SequenceMap(fflag, kind, RS1)).named('G2_0')
    G3 = cat(rasp.SequenceMap(fflag, kind, RS2)).named('G3_0')
    def fgm(kd, v):
        if v != 'n' and v[0] == kd: return v
        return 'n'
    for t in range(1, F_HOPS + 1):
        A2 = cat(rasp.Aggregate(sel_closed(), G2)).named(f'FA2_{t}')
        A3 = cat(rasp.Aggregate(sel_closed(), G3)).named(f'FA3_{t}')
        G2 = cat(rasp.SequenceMap(fgm, kind, A2)).named(f'G2_{t}')
        G3 = cat(rasp.SequenceMap(fgm, kind, A3)).named(f'G3_{t}')
    def pred_flag(k, q):
        if k == 0: return (-0.4 + FGAIN) if q != 'n' else -0.4
        if k == 1: return 0.6
        return None
    FR2 = cat(rasp.Aggregate(mksel(idx, G2, pred_flag), ynmap)).named('FR2')
    FR3 = cat(rasp.Aggregate(mksel(idx, G3, pred_flag), ynmap)).named('FR3')

    # ---- chain size >= 3 detection (local, 2-hop) ----
    KH = cat(rasp.Aggregate(sel_hist(), kind)).named('KH')
    same = cat(rasp.SequenceMap(lambda kd, v: 'S' if (kd in ('X', 'O') and v == kd) else 'D', kind, KH)).named('same')
    def pred_deg2(k, q):
        if k == 0: return (0.1 + 3.2 * 0.75) if q == 'S' else (0.1 - 3.2 * 0.25)
        if k == 1: return 0.6
        return None
    d2 = cat(rasp.Aggregate(mksel(idx, same, pred_deg2), ynmap)).named('d2')
    flagD = cat(rasp.SequenceMap(lambda kd, y: (kd, 'D') if (kd in ('X', 'O') and y == 'yes') else 'n', kind, d2)).named('flagD')
    FD = cat(rasp.Aggregate(sel_closed(), flagD)).named('FD')
    FDm = cat(rasp.SequenceMap(lambda kd, v: 'F' if (v != 'n' and v[0] == kd) else 'n', kind, FD)).named('FDm')
    def pred_big(k, q):
        if k == 0: return (0.1 + 2.0) if q == 'F' else 0.1
        if k == 1: return 0.6
        return None
    bigR = cat(rasp.Aggregate(mksel(idx, FDm, pred_big), ynmap)).named('bigR')
    def fkb(kd, y):
        if kd in ('X', 'O'): return kd + ('b' if y == 'yes' else 's')
        return kd
    kbig = cat(rasp.SequenceMap(fkb, kind, bigR)).named('kbig')

    def fstA(kb, r):
        if kb[0] == 'X' and len(kb) == 2: return 'Xm' if r == 'yes' else 'X1' + kb[1]
        if kb[0] == 'O' and len(kb) == 2: return 'Om' if r == 'yes' else 'O1' + kb[1]
        return kb
    def fstB(kb, r):
        if kb[0] == 'X' and len(kb) == 2: return 'X3' if r == 'yes' else 'X2' + kb[1]
        if kb[0] == 'O' and len(kb) == 2: return 'O3' if r == 'yes' else 'O2' + kb[1]
        return kb
    stA = cat(rasp.SequenceMap(fstA, kbig, FR2)).named('stA')
    stB = cat(rasp.SequenceMap(fstB, kbig, FR3)).named('stB')
    HA = cat(rasp.Aggregate(sel_hist(), stA)).named('HA')
    HB = cat(rasp.Aggregate(sel_hist(), stB)).named('HB')
    labA = cat(rasp.Aggregate(mksel(idx, HA, pred_proto), labmap)).named('labA')
    labAb = cat(rasp.Aggregate(mksel(idx, HA, pred_protoAb), labAbmap)).named('labAb')
    ox2 = cat(rasp.Aggregate(mksel(idx, HB, pred_protoB), labBmap)).named('ox2')
    labBb = cat(rasp.Aggregate(mksel(idx, HB, pred_protoBb), labBbmap)).named('labBb')

    def ftab1(lab, ru):
        capc, xn, eye, nEc = lab
        if capc >= 1: return ('cap', capc)
        if eye: return ('eye',)
        if xn: la = 1 if ru == 'lo' else 2
        else: la = max(1, min(nEc, 2))
        return (la, int(nEc >= 2), xn)
    tab1 = cat(rasp.SequenceMap(ftab1, labA, RU)).named('tab1')
    EO = cat(rasp.SequenceMap(lambda a, b: (a[0],) + tuple(b), labAb, ox2)).named('EO')
    bigbits = cat(rasp.SequenceMap(lambda a, b: (a[1], a[2], b[0], b[1]), labAb, labBb)).named('bigbits')
    def ftab2(s, eo):
        esc, o2, x2, x3 = eo
        if s[0] == 'cap': return TAC_CAP2 if s[1] >= 2 else TAC_CAP1
        if s[0] == 'eye': return TAC_EYE
        la, ne2, xn = s
        if xn and x3: la = max(la, 2)
        if la <= 1: return TAC_SA
        return TAC_ESC * esc + TAC_ATK * o2 + TAC_DEF * int(x2 and ne2 and not esc)
    tab2 = cat(rasp.SequenceMap(ftab2, tab1, EO)).named('tab2')
    def fbig(s, bb):
        escB, capB, defB, atkB = bb
        if s[0] == 'cap': return BIG_CAP * capB
        if s[0] == 'eye': return 0
        la, ne2, xn = s
        if la <= 1: return 0
        return BIG_ESC * escB + BIG_DEF * int(defB and ne2 and not escB) + BIG_ATK * atkB
    bigt = cat(rasp.SequenceMap(fbig, tab1, bigbits)).named('bigt')
    bigR2 = num(rasp.Map(lambda v: float(v), bigt)).named('bigR2')
    tacP = num(rasp.Map(lambda s: float(max(s, 0)), tab2)).named('tacP')
    tacN = num(rasp.Map(lambda s: float(max(-s, 0)), tab2)).named('tacN')

    # ---------- positional ----------
    InfM = cat(rasp.Aggregate(sel_kernel(1.5), kind)).named('InfM')
    zone = cat(rasp.Aggregate(mksel(idx, InfM, pred_zone), zmap)).named('zone')
    def fz(kd, z):
        if kd == 'E': return z
        if kd == 'P': return 'P'
        return 'S' + kd
    zoneP = cat(rasp.SequenceMap(fz, kind, zone)).named('zoneP')
    GainM = cat(rasp.Aggregate(sel_kernel(1.5, pad=True), zoneP)).named('GainM')
    gainR = num(rasp.Map(lambda z: GAINF.get(z, 0.0), GainM)).named('gainR')
    zpen = num(rasp.Map(lambda z: {'oS': 2.0, 'oW': 0.5}.get(z, 0.0), zoneP)).named('zpen')
    DTH = 0.05
    dang = num(rasp.Map(lambda v: {'O': 1.0 - DTH, 'X': -1.0 - DTH}.get(v, -DTH), InfM)).named('dang')
    passv = num(rasp.Map(lambda kd: PASSV if kd == 'P' else 0.0, kind)).named('passv')

    zsa = cat(rasp.SequenceMap(lambda s, z: 'thr' if (s == TAC_SA and z in ('pS', 'pW')) else 'no', tab2, zoneP)).named('zsa')
    zsaR = num(rasp.Map(lambda v: SA_OPP_BONUS if v == 'thr' else 0.0, zsa)).named('zsaR')
    a1 = num(rasp.LinearSequenceMap(tacP, tacN, 1.0, -1.0)).named('a1')
    a2 = num(rasp.LinearSequenceMap(gainR, zpen, GAINW, -1.0)).named('a2')
    a3 = num(rasp.LinearSequenceMap(linev, dang, 1.0, -DANGW)).named('a3')
    b00 = num(rasp.LinearSequenceMap(a1, bigR2, 1.0, 1.0)).named('b00')
    b0 = num(rasp.LinearSequenceMap(b00, zsaR, 1.0, 1.0)).named('b0')
    b1 = num(rasp.LinearSequenceMap(b0, a2, 1.0, 1.0)).named('b1')
    out = num(rasp.LinearSequenceMap(b1, a3, SCALE, SCALE)).named('logit')
    return out
