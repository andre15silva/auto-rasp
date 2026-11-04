
from tracr.rasp import rasp

SEL = 10.6                 # logit ~115.7 (gap to BOS ~110 -> exact zeros in float32)
UNSEL = 0.0
UNSEL_B = -10.0            # for selectors that may select nothing (BOS must win cleanly)
G_LO, G_HI = 10.6, 10.6 + 10.2 * 8
N_PROP = 6
NBUCK = 8
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
def orth_nbrs(q):
    r, c = rc(q); out = []
    for dr, dc in ORTH.values():
        rr, cc = r + dr, c + dc
        if 0 <= rr < 9 and 0 <= cc < 9: out.append(rr * 9 + cc)
    return out
ONB = [orth_nbrs(q) for q in range(81)]

def shift(sop, d, name):
    def pred(k, q, d=d):
        return SEL if (isinstance(q, int) and k == nb_target(q, d)) else UNSEL
    return rasp.categorical(rasp.Aggregate(rasp.Select(rasp.indices, rasp.indices, pred), sop)).named(name)

def thr(agg, name, low, cat=False):
    def f(x, cat=cat, low=low):
        if abs(x) < 1e-12: return False if cat else 0
        if abs(x - low) < 1e-12: return True if cat else 1
        return None
    enc = rasp.categorical if cat else rasp.numerical
    return enc(rasp.Map(f, agg)).named(name)

def lsm(a, b, name, fa=1, fb=1):
    return rasp.numerical(rasp.LinearSequenceMap(a, b, fa, fb)).named(name)

def tree(leaves, name):
    lvl = 0
    while len(leaves) > 1:
        nxt = []
        for i in range(0, len(leaves) - 1, 2):
            nxt.append(lsm(leaves[i], leaves[i + 1], f'{name}_{lvl}_{i}'))
        if len(leaves) % 2: nxt.append(leaves[-1])
        leaves = nxt; lvl += 1
    return leaves[0]

NBCATS = ('E', 'B', 'X1', 'X2', 'X3', 'O1', 'O2')
def nbcls(cnt, col):
    if col == 'S': return 'B'
    if col == 'E': return 'E'
    if cnt == 0: return 'X3' if col == 'X' else 'B'
    if cnt == 1: return col + '1'
    if cnt == 2: return col + '2'
    return 'X3' if col == 'X' else 'B'

W_CAP, W_CAPX, W_ESC3, W_ESC2, W_ESCF = 9.0, 2.0, 8.0, 3.0, -5.0
W_SUI, W_SA, W_FILL2 = -10.0, -7.0, -0.5
W_ATARI, W_DEF2 = 2.0, 1.5
def tactical(p1, p2):
    l = list(p1) + list(p2)
    n = {k: l.count(k) for k in NBCATS}
    if n['B'] == 4: return 0.0
    cap = n['O1'] > 0
    libs_after = n['E'] + (1 if n['X2'] else 0) + (2 if n['X3'] else 0)
    v = 0.0
    if cap:
        v += W_CAP + 1.5 * (n['O1'] - 1) + (W_CAPX if n['X1'] else 0.0)
        libs_after += 2
    elif n['X1']:
        if libs_after >= 3: v += W_ESC3
        elif libs_after == 2: v += W_ESC2
        else: v += W_ESCF
    else:
        if libs_after == 0: v += W_SUI
        elif libs_after == 1: v += W_SA
        elif libs_after == 2 and n['X2']: v += W_FILL2
    if libs_after >= 2:
        if n['O2']: v += W_ATARI
        if n['X2'] and libs_after >= 3: v += W_DEF2
    return round(v, 2)

PASS_LOGIT = -4.0
PRIOR = [-1.5, -0.3, 0.5, 0.5, 0.3]
def lineof(i):
    if i >= 81: return 9
    r, c = rc(i); return min(r, c, 8 - r, 8 - c)
def score23(e, line):
    if e == 'side': return PASS_LOGIT
    if e == 'eye': return -12.0
    return round(PRIOR[line] if line < 9 else 0.0, 2)

def build(stop=None):
    tok, idx = rasp.tokens, rasp.indices
    COL = {'.': 'E', 'x': 'X', 'o': 'O', 'B': 'S', 'W': 'S'}
    color = rasp.categorical(rasp.Map(lambda t: COL[t], tok)).named('color')
    isE = rasp.numerical(rasp.Map(lambda t: 1 if t == '.' else 0, tok)).named('isE')
    linec = rasp.categorical(rasp.Map(lineof, idx)).named('linec')

    ncW = shift(color, ORTH['W'], 'ncW')
    ncN = shift(color, ORTH['N'], 'ncN')
    # initial liberty buckets: for each bucket h, does q have an empty orthogonal neighbour with bucket h
    flags = []
    for h in range(NBUCK):
        def pb(k, q, h=h):
            if not isinstance(q, int) or q >= 81 or k >= 81: return UNSEL_B
            return SEL if (k in ONB[q] and bucket(k) == h) else UNSEL_B
        flags.append(rasp.numerical(rasp.Aggregate(rasp.Select(idx, idx, pb), isE, default=0)).named(f'b{h}_0'))

    hsb = rasp.categorical(rasp.SequenceMap(lambda w, c: True if c == 'S' else (w != c), ncW, color)).named('hsb')
    vsb = rasp.categorical(rasp.SequenceMap(lambda n, c: True if c == 'S' else (n != c), ncN, color)).named('vsb')
    hkey = rasp.categorical(rasp.SequenceMap(lambda b, i: i if b else 'no', hsb, idx)).named('hkey')
    vkey = rasp.categorical(rasp.SequenceMap(lambda b, i: i if b else 'no', vsb, idx)).named('vkey')
    color4 = rasp.categorical(rasp.SequenceMap(lambda b, c: c, hsb, color)).named('color4')
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
    hrun = rasp.categorical(rasp.Aggregate(rasp.Select(hkey, idx, ph), idx)).named('hrun')
    vrun = rasp.categorical(rasp.Aggregate(rasp.Select(vkey, idx, pv), idx)).named('vrun')
    ncS = shift(color4, ORTH['S'], 'ncS')
    ncE = shift(color4, ORTH['E'], 'ncE')
    dc = {d: shift(color4, v, 'dc' + d) for d, v in DIAG.items()}
    eq = lambda k, q: SEL if k == q else UNSEL
    selH = rasp.Select(hrun, hrun, eq)
    selV = rasp.Select(vrun, vrun, eq)

    low = 1.0
    for s in range(1, N_PROP + 1):
        sel = selH if s % 2 == 1 else selV
        low = low / 9
        new = []
        for j, f in enumerate(flags):
            a = rasp.numerical(rasp.Aggregate(sel, f, default=0)).named(f'b{j}_a{s}')
            new.append(thr(a, f'b{j}_{s}', low) if s % 2 == 0 else a)
        if s % 2 == 0: low = 1.0
        flags = new
    if stop == 'prop': return flags[0]

    tot = tree(list(flags), 'sb')
    cnt3 = rasp.categorical(rasp.Map(lambda v: min(int(round(v)), 3), tot)).named('cnt3')
    nbinfo = rasp.categorical(rasp.SequenceMap(nbcls, cnt3, color)).named('nbinfo')
    nbs = {d: shift(nbinfo, v, 'nb' + d) for d, v in ORTH.items()}
    srt = lambda a, b: tuple(sorted((a, b)))
    pNS = rasp.categorical(rasp.SequenceMap(srt, nbs['N'], nbs['S'])).named('pNS')
    pWE = rasp.categorical(rasp.SequenceMap(srt, nbs['W'], nbs['E'])).named('pWE')
    t1c = rasp.categorical(rasp.SequenceMap(tactical, pNS, pWE)).named('t1c')
    t1 = rasp.numerical(rasp.Map(lambda v: v, t1c)).named('t1')

    oNS = rasp.categorical(rasp.SequenceMap(srt, ncN, ncS)).named('oNS')
    oWE = rasp.categorical(rasp.SequenceMap(srt, ncW, ncE)).named('oWE')
    def orthcls(p1, p2):
        l = list(p1) + list(p2)
        if l.count('S') == 4: return 'side'
        if all(x in ('X', 'S') for x in l): return 'eye_e' if 'S' in l else 'eye_c'
        return 'no'
    orth = rasp.categorical(rasp.SequenceMap(orthcls, oNS, oWE)).named('orth')
    dA = rasp.categorical(rasp.SequenceMap(srt, dc['NW'], dc['NE'])).named('dA')
    dB = rasp.categorical(rasp.SequenceMap(srt, dc['SW'], dc['SE'])).named('dB')
    diagO = rasp.categorical(rasp.SequenceMap(lambda p1, p2: min((list(p1) + list(p2)).count('O'), 2), dA, dB)).named('diagO')
    def eyef(o, n):
        if o == 'side': return 'side'
        if o == 'eye_c': return 'eye' if n < 2 else 'no'
        if o == 'eye_e': return 'eye' if n < 1 else 'no'
        return 'no'
    eye = rasp.categorical(rasp.SequenceMap(eyef, orth, diagO)).named('eye')
    t23c = rasp.categorical(rasp.SequenceMap(score23, eye, linec)).named('t23c')
    t23 = rasp.numerical(rasp.Map(lambda v: v, t23c)).named('t23')
    return lsm(t1, t23, 'logits')
