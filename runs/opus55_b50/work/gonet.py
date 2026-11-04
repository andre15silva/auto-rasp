
from tracr.rasp import rasp

K_SIZE = 84                      # expected attention key size (all selectors use <=82-valued SOps)
UNIT = 1.0                       # predicate units; logit = 100*pred/sqrt(K)
SEL, UNSEL = 5.0, -5.0
N_PROP = 8                       # propagation steps (H,V,H,V,...)

def rc(i): return divmod(i, 9)
ORTH = {'N': (-1, 0), 'S': (1, 0), 'W': (0, -1), 'E': (0, 1)}
DIAG = {'NW': (-1, -1), 'NE': (-1, 1), 'SW': (1, -1), 'SE': (1, 1)}

def nb_target(q, d):
    """index of neighbour of q in direction d; 81 (side token) if off board; q=81 -> 81"""
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

def thr(agg, name, cat=False):
    f = (lambda x: bool(x > 0.001)) if cat else (lambda x: 1 if x > 0.001 else 0)
    enc = rasp.categorical if cat else rasp.numerical
    return enc(rasp.Map(f, agg)).named(name)

def build():
    tok, idx = rasp.tokens, rasp.indices
    COL = {'.': 'E', 'x': 'X', 'o': 'O', 'B': 'S', 'W': 'S'}
    color = rasp.categorical(rasp.Map(lambda t: COL[t], tok)).named('color')
    stoneidx = rasp.categorical(rasp.SequenceMap(lambda t, i: i if (t in ('x', 'o') and i < 81) else 'none', tok, idx)).named('stoneidx')
    emptyidx = rasp.categorical(rasp.SequenceMap(lambda t, i: i if (t == '.' and i < 81) else 'none', tok, idx)).named('emptyidx')
    isE = rasp.numerical(rasp.Map(lambda t: 1 if t == '.' else 0, tok)).named('isE')
    isX = rasp.numerical(rasp.Map(lambda t: 1 if t == 'x' else 0, tok)).named('isX')
    isO = rasp.numerical(rasp.Map(lambda t: 1 if t == 'o' else 0, tok)).named('isO')
    offs = rasp.numerical(rasp.Map(lambda t: {'.': 20, 'x': 0, 'o': 10, 'B': 30, 'W': 30}[t], tok)).named('offs')

    nc = {d: shift(color, v, 'nc' + d) for d, v in ORTH.items()}
    dc = {d: shift(color, v, 'dc' + d) for d, v in DIAG.items()}

    # ---- initial flags: liberty rows/cols for stones, touch-X / touch-O for empty points
    flags = []
    for r in range(9):
        def pr(k, q, r=r):
            if not isinstance(q, int) or k >= 81: return UNSEL
            return SEL if (k in ONB[q] and k // 9 == r) else UNSEL
        a = rasp.numerical(rasp.Aggregate(rasp.Select(idx, stoneidx, pr), isE, default=0)).named(f'R{r}_a0')
        flags.append(thr(a, f'R{r}_0'))
    for c in range(9):
        def pc(k, q, c=c):
            if not isinstance(q, int) or k >= 81: return UNSEL
            return SEL if (k in ONB[q] and k % 9 == c) else UNSEL
        a = rasp.numerical(rasp.Aggregate(rasp.Select(idx, stoneidx, pc), isE, default=0)).named(f'C{c}_a0')
        flags.append(thr(a, f'C{c}_0'))
    def pn(k, q):
        if not isinstance(q, int) or k >= 81: return UNSEL
        return SEL if k in ONB[q] else UNSEL
    for nm, v in (('TX', isX), ('TO', isO)):
        a = rasp.numerical(rasp.Aggregate(rasp.Select(idx, emptyidx, pn), v, default=0)).named(nm + '_a0')
        flags.append(thr(a, nm + '_0'))

    # ---- runs
    hsb = rasp.categorical(rasp.SequenceMap(lambda w, c: True if c == 'S' else (w != c), nc['W'], color)).named('hsb')
    vsb = rasp.categorical(rasp.SequenceMap(lambda n, c: True if c == 'S' else (n != c), nc['N'], color)).named('vsb')
    hkey = rasp.categorical(rasp.SequenceMap(lambda b, i: i if b else 'no', hsb, idx)).named('hkey')
    vkey = rasp.categorical(rasp.SequenceMap(lambda b, i: i if b else 'no', vsb, idx)).named('vkey')
    def ph(k, q):
        if k == 'no': return UNSEL
        if q == 81 or k == 81: return 6.9 if (q == 81 and k == 81) else UNSEL
        if k // 9 == q // 9 and k <= q: return 6.9 - 0.7 * (q - k)
        return UNSEL
    def pv(k, q):
        if k == 'no': return UNSEL
        if q == 81 or k == 81: return 6.9 if (q == 81 and k == 81) else UNSEL
        if k % 9 == q % 9 and k <= q: return 6.9 - 0.7 * ((q - k) // 9)
        return UNSEL
    hrun = rasp.categorical(rasp.Aggregate(rasp.Select(hkey, idx, ph), idx)).named('hrun')
    vrun = rasp.categorical(rasp.Aggregate(rasp.Select(vkey, idx, pv), idx)).named('vrun')
    eq = lambda k, q: SEL if k == q else UNSEL
    selH = rasp.Select(hrun, hrun, eq)
    selV = rasp.Select(vrun, vrun, eq)

    # ---- propagation
    names = [f'R{r}' for r in range(9)] + [f'C{c}' for c in range(9)] + ['TX', 'TO']
    for s in range(1, N_PROP + 1):
        sel = selH if s % 2 == 1 else selV
        new = []
        for j, f in enumerate(flags):
            a = rasp.numerical(rasp.Aggregate(sel, f, default=0)).named(f'{names[j]}_a{s}')
            new.append(thr(a, f'{names[j]}_{s}', cat=(s == N_PROP and j >= 18)))
        flags = new
    R, C, TXc, TOc = flags[:9], flags[9:18], flags[18], flags[19]

    def lsm(a, b, name): return rasp.numerical(rasp.LinearSequenceMap(a, b, 1, 1)).named(name)
    def tree(leaves, name):
        lvl = 0
        while len(leaves) > 1:
            nxt = []
            for i in range(0, len(leaves) - 1, 2):
                nxt.append(lsm(leaves[i], leaves[i + 1], f'{name}_{lvl}_{i}'))
            if len(leaves) % 2: nxt.append(leaves[-1])
            leaves = nxt; lvl += 1
        return leaves[0]
    totR = tree(R[:8] + [lsm(R[8], offs, 'R8off')], 'sR')
    totC = tree(C, 'sC')
    cr = rasp.categorical(rasp.Map(lambda v: ('XOES'[int(round(v)) // 10], min(int(round(v)) % 10, 3)), totR)).named('cr')
    cc3 = rasp.categorical(rasp.Map(lambda v: min(int(round(v)), 3), totC)).named('cc3')
    def nbcls(crv, ncl):
        col, nr = crv
        if col == 'S': return 'B'
        if col == 'E': return 'E'
        if nr == 0 or ncl == 0: return 'X3' if col == 'X' else 'B'
        if nr == 1 and ncl == 1: return col + '1'
        if nr <= 2 and ncl <= 2:
            if col == 'X': return 'X2'
            return 'Ox' if (nr == 2 and ncl == 2) else 'O2'
        return 'X3' if col == 'X' else 'B'
    nbinfo = rasp.categorical(rasp.SequenceMap(nbcls, cr, cc3)).named('nbinfo')
    nbs = {d: shift(nbinfo, v, 'nb' + d) for d, v in ORTH.items()}
    srt = lambda a, b: tuple(sorted((a, b)))
    pNS = rasp.categorical(rasp.SequenceMap(srt, nbs['N'], nbs['S'])).named('pNS')
    pWE = rasp.categorical(rasp.SequenceMap(srt, nbs['W'], nbs['E'])).named('pWE')

    def score1(p1, p2):
        l = list(p1) + list(p2)
        n = {k: l.count(k) for k in ('E', 'B', 'X1', 'X2', 'X3', 'O1', 'O2', 'Ox')}
        if n['B'] == 4: return 0.0
        cap = n['O1'] > 0
        libs_after = n['E'] + (1 if n['X2'] else 0) + (2 if n['X3'] else 0)
        v = 0.0
        if cap:
            v += 9.0 + 1.5 * (n['O1'] - 1) + (2.0 if n['X1'] else 0.0)
            libs_after += 2
        elif n['X1']:
            if libs_after >= 3: v += 8.0
            elif libs_after == 2: v += 3.0
            else: v -= 5.0
        else:
            if libs_after == 0: v -= 10.0
            elif libs_after == 1: v -= 7.0
            elif libs_after == 2 and n['X2']: v -= 0.5
        if libs_after >= 2:
            if n['O2']: v += 2.0
            elif n['Ox']: v += 1.0
            if n['X2'] and libs_after >= 3: v += 1.5
        return round(v, 2)
    t1c = rasp.categorical(rasp.SequenceMap(score1, pNS, pWE)).named('t1c')
    t1 = rasp.numerical(rasp.Map(lambda v: v, t1c)).named('t1')

    # ---- eye / region
    cntpair = lambda a, b: tuple(sorted((a, b)))
    oNS = rasp.categorical(rasp.SequenceMap(cntpair, nc['N'], nc['S'])).named('oNS')
    oWE = rasp.categorical(rasp.SequenceMap(cntpair, nc['W'], nc['E'])).named('oWE')
    def orthcls(p1, p2):
        l = list(p1) + list(p2)
        if l.count('S') == 4: return 'side'
        if all(x in ('X', 'S') for x in l): return 'eye_e' if 'S' in l else 'eye_c'
        return 'no'
    orth = rasp.categorical(rasp.SequenceMap(orthcls, oNS, oWE)).named('orth')
    dA = rasp.categorical(rasp.SequenceMap(cntpair, dc['NW'], dc['NE'])).named('dA')
    dB = rasp.categorical(rasp.SequenceMap(cntpair, dc['SW'], dc['SE'])).named('dB')
    diagO = rasp.categorical(rasp.SequenceMap(lambda p1, p2: min((list(p1) + list(p2)).count('O'), 2), dA, dB)).named('diagO')
    def eyef(o, n):
        if o == 'side': return 'side'
        if o == 'eye_c': return 'eye' if n < 2 else 'no'
        if o == 'eye_e': return 'eye' if n < 1 else 'no'
        return 'no'
    eye = rasp.categorical(rasp.SequenceMap(eyef, orth, diagO)).named('eye')
    region = rasp.categorical(rasp.SequenceMap(lambda a, b: ('own' if a and not b else 'opp' if b and not a else 'both' if a else 'none'), TXc, TOc)).named('region')
    REG = {'own': -2.5, 'opp': -1.5, 'both': 0.0, 'none': 0.0}
    PASS_LOGIT = -1.0
    def score2(e, rg):
        if e == 'side': return PASS_LOGIT
        if e == 'eye': return -12.0
        return REG[rg]
    t2c = rasp.categorical(rasp.SequenceMap(score2, eye, region)).named('t2c')
    t2 = rasp.numerical(rasp.Map(lambda v: v, t2c)).named('t2')

    PRIOR = [-1.5, -0.3, 0.5, 0.5, 0.3]
    def prior(i):
        if i >= 81: return 0.0
        r, c = rc(i); return PRIOR[min(r, c, 8 - r, 8 - c)]
    t3 = rasp.numerical(rasp.Map(prior, idx)).named('t3')
    s12 = lsm(t1, t2, 's12')
    out = lsm(s12, t3, 'logits')
    return out
