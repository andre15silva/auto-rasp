
from tracr.rasp import rasp

SEL = 10.6
UNSEL = 0.0
G_LO, G_HI = 10.6, 10.6 + 10.2 * 8
N_PROP = 6
NBUCK = 8
TINY = 1e-5
def bucket(i): return (i // 9 + 3 * (i % 9)) % NBUCK
def rc(i): return divmod(i, 9)
ORTH = {'N': (-1, 0), 'S': (1, 0), 'W': (0, -1), 'E': (0, 1)}
DIAG = {'NW': (-1, -1), 'NE': (-1, 1), 'SW': (1, -1), 'SE': (1, 1)}
def nb_target(q, d):
    if q == 81: return 81
    r, c = rc(q); dr, dc = d
    rr, cc = r + dr, c + dc
    if 0 <= rr < 9 and 0 <= cc < 9: return rr * 9 + cc
    return 81
def mdist(a, b): return abs(a // 9 - b // 9) + abs(a % 9 - b % 9)
ONB = [[k for k in range(81) if mdist(k, q) == 1] for q in range(81)]

def cat(x, name): return rasp.categorical(x).named(name)
def num(x, name): return rasp.numerical(x).named(name)
def M(f, x): return rasp.Map(f, x, simplify=False)
def SM(f, a, b): return rasp.SequenceMap(f, a, b)
def lsm(a, b, name, fa=1, fb=1): return num(rasp.LinearSequenceMap(a, b, fa, fb), name)
def tree(leaves, name, fac=1.0):
    lvl = 0
    while len(leaves) > 1:
        nxt = []
        for i in range(0, len(leaves) - 1, 2):
            f = fac if lvl == 0 else 1
            nxt.append(lsm(leaves[i], leaves[i + 1], f'{name}_{lvl}_{i}', f, f))
        if len(leaves) % 2:
            last = leaves[-1]
            if lvl == 0 and fac != 1:
                last = lsm(last, last, f'{name}_{lvl}_last', fac, 0)
            nxt.append(last)
        leaves = nxt; lvl += 1
    return leaves[0]

def shift(sop, d, name):
    def pred(k, q, d=d):
        return SEL if (isinstance(q, int) and k == nb_target(q, d)) else UNSEL
    return cat(rasp.Aggregate(rasp.Select(rasp.indices, rasp.indices, pred), sop), name)

def thr(xh, name):
    def g(x):
        if abs(x) < 1e-12: return 0
        if abs(x - TINY) < 1e-15: return 1
        return None
    return num(M(g, xh), name)

SIZES = ('t', 's', 'm', 'l')
def szcls(v):
    n = int(round(v * 100))
    return 't' if n <= 1 else 's' if n <= 3 else 'm' if n <= 6 else 'l'

def build(stop=None):
    tok, idx = rasp.tokens, rasp.indices
    COL = {'.': 'E', 'x': 'X', 'o': 'O', 'B': 'S', 'W': 'S'}
    color = cat(rasp.Map(lambda t: COL[t], tok), 'color')
    side = cat(rasp.Map(lambda t: t if t in ('B', 'W') else 'P', tok), 'side')
    linec = cat(rasp.Map(lambda i: 9 if i >= 81 else min(i // 9, i % 9, 8 - i // 9, 8 - i % 9), idx), 'linec')

    ncW = shift(color, ORTH['W'], 'ncW')
    ncN = shift(color, ORTH['N'], 'ncN')
    def bvf(t, i):
        if i == 81: return 'S' if t in ('B', 'W') else 'D'
        if t == '.': return bucket(i)
        if t == 'x': return 'X'
        if t == 'o': return 'O'
        return 'D'
    bv = cat(SM(bvf, tok, idx), 'bv')
    def pinit(k, q):
        if not isinstance(q, int): return UNSEL
        if q == 81: return SEL if k == 81 else UNSEL
        return SEL if (k == q or k in ONB[q]) else UNSEL
    bund = cat(rasp.Aggregate(rasp.Select(idx, idx, pinit), bv), 'bund0')

    hsb = cat(SM(lambda w, c: True if c == 'S' else (w != c), ncW, color), 'hsb')
    vsb = cat(SM(lambda n, c: True if c == 'S' else (n != c), ncN, color), 'vsb')
    hkey = cat(SM(lambda b, i: i if b else 'no', hsb, idx), 'hkey')
    vkey = cat(SM(lambda b, i: i if b else 'no', vsb, idx), 'vkey')
    color4 = cat(SM(lambda b, c: c, hsb, color), 'color4')
    gstep = (G_HI - G_LO) / 8
    def ph(k, q):
        if k == 'no': return UNSEL
        if q == 81 or k == 81: return G_HI if (q == 81 and k == 81) else UNSEL
        if k // 9 == q // 9 and k <= q: return G_HI - gstep * (q - k)
        return UNSEL
    def pv(k, q):
        if k == 'no': return UNSEL
        if q == 81 or k == 81: return G_HI if (q == 81 and k == 81) else UNSEL
        if k % 9 == q % 9 and k <= q: return G_HI - gstep * ((q - k) // 9)
        return UNSEL
    hrun = cat(rasp.Aggregate(rasp.Select(hkey, idx, ph), idx), 'hrun')
    vrun = cat(rasp.Aggregate(rasp.Select(vkey, idx, pv), idx), 'vrun')
    ncS = shift(color4, ORTH['S'], 'ncS')
    ncE = shift(color4, ORTH['E'], 'ncE')
    dc = {d: shift(color4, v, 'dc' + d) for d, v in DIAG.items()}
    eq = lambda k, q: SEL if k == q else UNSEL
    selH = rasp.Select(hrun, hrun, eq)
    selV = rasp.Select(vrun, vrun, eq)
    for s_ in range(1, N_PROP + 1):
        bund = cat(rasp.Aggregate(selH if s_ % 2 == 1 else selV, bund), f'bund{s_}')

    # ---- extraction
    def extract(src_, pred, name):
        def fx(v, pred=pred):
            if v == 'D': return TINY
            return 1 if pred(v) else 0
        return thr(num(M(fx, src_), 'x' + name), 'f' + name)
    fb = [extract(bund, (lambda v, h=h: v == h), f'b{h}') for h in range(NBUCK)]
    fanyX = extract(bund, (lambda v: v == 'X'), 'anyX')
    fanyO = extract(bund, (lambda v: v == 'O'), 'anyO')
    libn = tree(fb, 'sl', 0.01)
    cnt3 = cat(M(lambda v: min(int(round(v * 100)), 3), libn), 'cnt3')
    # local size proxy: stone has a same-coloured orthogonal neighbour <=> group size >= 2
    sNS = cat(SM(lambda a, b: (a, b), ncN, ncS), 'sNS')
    sWE = cat(SM(lambda a, b: (a, b), ncW, ncE), 'sWE')
    s4c = cat(SM(lambda p, q: tuple(sorted(set(p + q))), sNS, sWE), 's4c')
    mult = cat(SM(lambda cs, c: (c in cs) if c in ('X', 'O') else False, s4c, color), 'mult')
    cc = cat(SM(lambda n, c: c if c in ('E', 'S') else (c, n), cnt3, color), 'cc')
    def nbf(c, ml):
        if c == 'E': return 'E'
        if c == 'S': return 'B'
        col, n = c
        if n == 0: n = 3
        if col == 'X':
            if n == 1: return 'X1m' if ml else 'X1s'
            return 'X2' if n == 2 else 'X3'
        if n == 1: return 'O1m' if ml else 'O1s'
        return 'O2' if n == 2 else 'B'
    nbinfo = cat(SM(nbf, cc, mult), 'nbinfo')
    if stop == 'nbinfo': return num(M(lambda v: 1 if v == 'E' else 0, nbinfo), 'dbg')

    # ---- tactical evaluation at empty points (pair-of-pairs lookup)
    nbs = {d: shift(nbinfo, v, 'nb' + d) for d, v in ORTH.items()}
    srt = lambda a, b: tuple(sorted((a, b)))
    pNS = cat(SM(srt, nbs['N'], nbs['S']), 'pNS')
    pWE = cat(SM(srt, nbs['W'], nbs['E']), 'pWE')
    t1c = cat(SM(lambda a, b: round(OFF1 + tactical(list(a) + list(b)), 2), pNS, pWE), 't1c')
    t1 = num(M(lambda v: v, t1c), 't1')
    if stop == 't1': return t1
    # ---- eyes
    oNS = cat(SM(srt, ncN, ncS), 'oNS')
    oWE = cat(SM(srt, ncW, ncE), 'oWE')
    def orthcls(p1, p2):
        l = list(p1) + list(p2)
        if l.count('S') == 4: return 'side'
        if all(x in ('X', 'S') for x in l): return 'eye_e' if 'S' in l else 'eye_c'
        return 'no'
    orth = cat(SM(orthcls, oNS, oWE), 'orth')
    dA = cat(SM(srt, dc['NW'], dc['NE']), 'dA')
    dB = cat(SM(srt, dc['SW'], dc['SE']), 'dB')
    diagO = cat(SM(lambda p1, p2: min((list(p1) + list(p2)).count('O'), 2), dA, dB), 'diagO')
    def eyef(o, n):
        if o == 'side': return 'side'
        if o == 'eye_c': return 'eye' if n < 2 else 'feye'
        if o == 'eye_e': return 'eye' if n < 1 else 'feye'
        return 'no'
    eye = cat(SM(eyef, orth, diagO), 'eye')

    # ---- regions / influence
    fXcat = cat(M(lambda v: v > 0.5, fanyX), 'fXcat')
    fOcat = cat(M(lambda v: v > 0.5, fanyO), 'fOcat')
    region = cat(SM(lambda a, b: ('own' if a and not b else 'opp' if b and not a else 'both' if a else 'none'), fXcat, fOcat), 'region')
    ICOL = {'.': 'E', 'x': 'X', 'o': 'O', 'B': 'S', 'W': 'S'}
    colI = cat(SM(lambda t, i: ICOL[t] if not (t in ('B', 'W') and i < 81) else ('d', i % 3), tok, idx), 'colI')
    def pw2(k, q):
        if not isinstance(q, int) or q >= 81 or k >= 81: return UNSEL if not (q == 81 and k == 81) else SEL
        return SEL if mdist(k, q) <= 2 else UNSEL
    mix2 = cat(rasp.Aggregate(rasp.Select(idx, idx, pw2), colI), 'mix2')
    DUM = {0: 0.08, 1: 0.18, 2: 0.32}
    def rd(colr):
        def f(v, colr=colr):
            if isinstance(v, tuple): return DUM[v[1]]
            return 1.0 if v == colr else 0.0
        return f
    iX = num(M(rd('X'), mix2), 'iX')
    iO = num(M(rd('O'), mix2), 'iO')
    def binf(x):
        for val, b in ((0.0, 0), (0.08, 1), (0.18, 2), (0.32, 3)):
            if abs(x - val) < 1e-9: return b
        return None
    bX = cat(M(binf, iX), 'bX')
    bO = cat(M(binf, iO), 'bO')
    infl = cat(SM(lambda a, b: (a, b), bX, bO), 'infl')
    aux = cat(SM(lambda e, r: (e, r), eye, region), 'aux')
    def s4(a, ln):
        e, rg = a
        if e == 'side': return OFF4
        v = REG[rg] + (PRIOR[ln] if ln < 9 else 0.0)
        if e == 'eye': v += EYE
        elif e == 'feye': v += FEYE
        return round(OFF4 + v, 2)
    if stop == 't5': return lsm(t4, t5, 'dbg5')

    # ---- pass: Tromp-Taylor estimate
    def ttf(c, r):
        if c == 'X': return 'own'
        if c == 'O': return 'opp'
        if c == 'E': return {'own': 'own', 'opp': 'opp'}.get(r, 'neu')
        return 'side'
    colT = cat(SM(lambda t, i: (('dum', i % NDUM) if (t in ('B', 'W') and i < 81) else COL[t]), tok, idx), 'colT')
    def ttf2(c, r):
        if isinstance(c, tuple): return c
        return ttf(c, r)
    ttc = cat(SM(ttf2, colT, region), 'ttc')
    TTV = {'own': 1.0, 'opp': 0.0, 'neu': 0.5, 'side': 0.5}
    ttn = num(M(lambda v: (TT_DUM[v[1]] if isinstance(v, tuple) else TTV[v]), ttc), 'ttn')
    neun = num(M(lambda v: (NEU_DUM.get(v[1], 0) if isinstance(v, tuple) else (1 if v == 'neu' else 0)), ttc), 'neun')
    def pall(k, q):
        return SEL if k < 81 else UNSEL
    selall = rasp.Select(idx, idx, pall)
    stn = num(M(lambda v: (PH_DUM.get(v[1], 0) if isinstance(v, tuple) else (1 if v in ('X', 'O') else 0)), colT), 'stn')
    mst = num(rasp.Aggregate(selall, stn, default=0), 'mst')
    def phf(x):
        for v, cl in PH_KEEP:
            if abs(x - v) < 1e-9: return cl
        return None
    phase = cat(M(phf, mst), 'phase')
    mtt = num(rasp.Aggregate(selall, ttn, default=0), 'mtt')
    mneu = num(rasp.Aggregate(selall, neun, default=0), 'mneu')
    # thresholds: TT margin for mover = 162*(m - 0.5) +/- komi
    def mcls(x):
        for v, cl in TT_KEEP:
            if abs(x - v) < 1e-9: return cl
        return None
    ttcls = cat(M(mcls, mtt), 'ttcls')
    def ncls(x):
        for v, cl in NEU_KEEP:
            if abs(x - v) < 1e-9: return cl
        return None
    neucls = cat(M(ncls, mneu), 'neucls')
    pstate = cat(SM(lambda a, b: (a, b), ttcls, neucls), 'pstate')
    def passf(ps, sd):
        if sd not in ('B', 'W'): return OFF6
        tc, nc = ps
        return round(OFF6 + PASSTAB(tc, nc, sd), 2)
    t6c = cat(SM(passf, pstate, side), 't6c')
    t6 = num(M(lambda v: v, t6c), 't6')
    lp = cat(SM(lambda ln, ph: (ln, ph), linec, phase), 'lp')
    def s4p(a, lph):
        e, rg = a
        ln, ph = lph
        if e == 'side': return OFF4
        v = REGP[ph][rg] + (PRIOR[ph][ln] if ln < 9 else 0.0)
        if e == 'eye': v += EYE
        elif e == 'feye': v += FEYE
        return round(OFF4 + v, 2)
    t4c = cat(SM(s4p, aux, lp), 't4c')
    t4 = num(M(lambda v: v, t4c), 't4')
    cph = cat(SM(lambda c, ph: (c, ph), color, phase), 'cph')
    t5c = cat(SM(lambda inf, cp: round(OFF5 + (INFL[cp[1]].get(inf, 0.0) if cp[0] == 'E' else 0.0), 2), infl, cph), 't5c')
    t5 = num(M(lambda v: v, t5c), 't5')

    s14 = lsm(t1, t4, 's14')
    s56 = lsm(t5, t6, 's56')
    return lsm(s14, s56, 'logits')



NBC = ('E', 'B', 'X1s', 'X1m', 'X2', 'X3', 'O1s', 'O1m', 'O2')
def tactical(l):
    n = {k: l.count(k) for k in NBC}
    if n['B'] == 4: return 0.0
    T = TACT
    capv = T['cap_m'] if n['O1m'] else (T['cap_s'] if n['O1s'] else 0.0)
    nO1 = n['O1m'] + n['O1s']
    escv = 'm' if n['X1m'] else ('s' if n['X1s'] else None)
    la = n['E'] + (1 if n['X2'] else 0) + (2 if n['X3'] else 0) + (2 if nO1 else 0)
    v = 0.0
    if nO1:
        v += capv + T['cap_extra'] * (nO1 - 1) + (T['capsave'] if escv else 0.0)
    elif escv:
        if la >= 3: v += T['esc3'][escv]
        elif la == 2: v += T['esc2'][escv]
        else: v += T['escf']
    else:
        if la == 0: v += T['sui']
        elif la == 1: v += T['sa_m'] if n['X2'] else T['sa_s']
        elif la == 2 and n['X2']: v += T['fill2']
    if n['E'] == 0 and not nO1 and not escv: v += T['noE']
    if la >= 2 and n['O2']: v += T['atari']
    if la >= 3 and n['X2']: v += T['def2']
    nX = n['X1s'] + n['X1m'] + n['X2'] + n['X3']
    nO = nO1 + n['O2'] + 0
    v += SHAPE.get((min(nX, 3), min(nO, 3)), 0.0)
    return round(v, 2)

# ---------------- tables
OFF1, OFF4, OFF5, OFF6 = 25.0, 20.0, 5.0, 10.0
TACT = {'cap_s': 8.0, 'cap_m': 11.0, 'cap_extra': 1.5, 'capsave': 2.0,
        'esc3': {'s': 6.5, 'm': 9.0}, 'esc2': {'s': 0.5, 'm': 2.5}, 'escf': -5.0,
        'sui': -10.0, 'sa_s': -6.0, 'sa_m': -9.0, 'fill2': -1.0, 'noE': -2.0,
        'atari': 2.0, 'def2': 2.5}
SHAPE = {(1, 0): -0.2, (2, 0): -0.8, (3, 0): -1.5, (0, 1): 0.2, (0, 2): 0.3, (1, 1): 0.5, (2, 1): 0.3, (1, 2): 0.6}
REG = {'own': -1.5, 'opp': -1.0, 'both': 0.0, 'none': 0.0}
REGP = {0: REG, 1: REG, 2: REG}
PRIOR = {0: [-3.0, -1.5, 0.8, 1.6, 2.0], 1: [-1.5, -0.4, 0.5, 0.6, 0.6], 2: [-0.3, 0.0, 0.0, 0.0, 0.0]}
_PHD = [(9, 0), (10, 1), (39, 1), (40, 2)]
PH_KEEP = [(n / 81.0, c) for n, c in _PHD]
PH_DUM = {k: n / 81.0 for k, (n, c) in enumerate(_PHD)}
EYE, FEYE = -12.0, -5.0
_INFL_MID = {(0, 0): 1.0, (1, 0): 0.5, (2, 0): -0.3, (3, 0): -1.5, (0, 1): 0.7, (0, 2): -0.2, (0, 3): -1.5,
        (1, 1): 1.0, (2, 1): 0.7, (1, 2): 0.7, (2, 2): 0.3, (3, 3): -0.3}
_INFL_OPEN = {(0, 0): 1.0, (1, 0): -0.5, (2, 0): -1.5, (3, 0): -2.5, (0, 1): 0.6, (0, 2): -0.5, (0, 3): -2.0,
        (1, 1): 0.5, (2, 1): 0.0, (1, 2): 0.0, (2, 2): 0.0, (3, 3): -0.3}
INFL = {0: _INFL_OPEN, 1: _INFL_MID, 2: _INFL_MID}
# Tromp-Taylor: m = 0.5 + d/162, d = own - opp area; classes c0..c6 by thresholds -15.5,-7.5,-0.5,0.5,7.5,15.5
def _m(d): return 0.5 + d / 162.0
_TTD = [(-16, 0), (-15, 1), (-8, 1), (-7, 2), (-1, 2), (0, 3), (1, 4), (7, 4), (8, 5), (15, 5), (16, 6)]
TT_KEEP = [(_m(d), c) for d, c in _TTD]
NDUM = len(_TTD)
TT_DUM = {k: _m(d) for k, (d, c) in enumerate(_TTD)}
_NEUD = [(0, 0), (1, 1), (2, 1), (3, 2), (5, 2), (6, 3)]
NEU_KEEP = [(n / 81.0, c) for n, c in _NEUD]
NEU_DUM = {k: n / 81.0 for k, (n, c) in enumerate(_NEUD) if n > 0}
def PASSTAB(tc, nc, sd):
    win = (tc >= 5) if sd == 'B' else (tc >= 2)
    big = (tc >= 6) if sd == 'B' else (tc >= 4)
    if win and nc == 0: return -7.0
    if win and nc == 1: return -7.5
    return -9.0
