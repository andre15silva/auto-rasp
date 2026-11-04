
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

THR_LOW = 1.0/9
def thr(agg, name, cat=False):
    def f(x, cat=cat):
        if abs(x) < 1e-12: return False if cat else 0
        if abs(x - THR_LOW) < 1e-12: return True if cat else 1
        return None
    enc = rasp.categorical if cat else rasp.numerical
    return enc(rasp.Map(f, agg)).named(name)

def build(stop=None):
    tok, idx = rasp.tokens, rasp.indices
    COL = {'.': 'E', 'x': 'X', 'o': 'O', 'B': 'S', 'W': 'S'}
    color = rasp.categorical(rasp.Map(lambda t: COL[t], tok)).named('color')
    isE = rasp.numerical(rasp.Map(lambda t: 1 if t == '.' else 0, tok)).named('isE')
    isX = rasp.numerical(rasp.Map(lambda t: 1 if t == 'x' else 0, tok)).named('isX')
    isO = rasp.numerical(rasp.Map(lambda t: 1 if t == 'o' else 0, tok)).named('isO')
    offs = rasp.numerical(rasp.Map(lambda t: {'.': 20, 'x': 0, 'o': 10, 'B': 30, 'W': 30}[t], tok)).named('offs')

    nc = {d: shift(color, v, 'nc' + d) for d, v in ORTH.items()}

    # ---- initial flags via MLPs (no heads)
    eNS = rasp.categorical(rasp.SequenceMap(lambda a, b: (a == 'E', b == 'E'), nc['N'], nc['S'])).named('eNS')
    eWE = rasp.categorical(rasp.SequenceMap(lambda a, b: (a == 'E', b == 'E'), nc['W'], nc['E'])).named('eWE')
    xNS = rasp.categorical(rasp.SequenceMap(lambda a, b: (a == 'X' or b == 'X', a == 'O' or b == 'O'), nc['N'], nc['S'])).named('xNS')
    xWE = rasp.categorical(rasp.SequenceMap(lambda a, b: (a == 'X' or b == 'X', a == 'O' or b == 'O'), nc['W'], nc['E'])).named('xWE')
    rowc = rasp.categorical(rasp.SequenceMap(lambda c, i: (i // 9) if (c in ('X', 'O') and i < 81) else -1, color, idx)).named('rowc')
    colc = rasp.categorical(rasp.SequenceMap(lambda c, i: (i % 9) if (c in ('X', 'O') and i < 81) else -1, color, idx)).named('colc')
    ecol = rasp.categorical(rasp.Map(lambda c: c == 'E', color)).named('ecol')
    # pattern for rows: (row, N empty, S empty, W or E empty)
    patR = rasp.categorical(rasp.SequenceMap(lambda ns, we: (ns[0], ns[1], we[0] or we[1]), eNS, eWE)).named('patR')
    patC = rasp.categorical(rasp.SequenceMap(lambda ns, we: (we[0], we[1], ns[0] or ns[1]), eNS, eWE)).named('patC')
    patRr = rasp.categorical(rasp.SequenceMap(lambda p, r: (r,) + p, patR, rowc)).named('patRr')
    patCc = rasp.categorical(rasp.SequenceMap(lambda p, c: (c,) + p, patC, colc)).named('patCc')
    patT = rasp.categorical(rasp.SequenceMap(lambda a, b: (a[0] or b[0], a[1] or b[1]), xNS, xWE)).named('patT')
    patTe = rasp.categorical(rasp.SequenceMap(lambda p, e: p if e else (False, False), patT, ecol)).named('patTe')
    flags = []
    for r in range(9):
        def fr(p, r=r):
            rr, n, s_, we = p
            if rr < 0: return 0
            return 1 if ((n and r == rr - 1) or (s_ and r == rr + 1) or (we and r == rr)) else 0
        flags.append(rasp.numerical(rasp.Map(fr, patRr)).named(f'R{r}_0'))
    for c in range(9):
        def fc(p, c=c):
            cc, w, e, ns = p
            if cc < 0: return 0
            return 1 if ((w and c == cc - 1) or (e and c == cc + 1) or (ns and c == cc)) else 0
        flags.append(rasp.numerical(rasp.Map(fc, patCc)).named(f'C{c}_0'))
    flags.append(rasp.numerical(rasp.Map(lambda p: 1 if p[0] else 0, patTe)).named('TX_0'))
    flags.append(rasp.numerical(rasp.Map(lambda p: 1 if p[1] else 0, patTe)).named('TO_0'))

    if stop == 'init': return flags[0]
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
    color4 = rasp.categorical(rasp.SequenceMap(lambda b, c: c, hsb, color)).named('color4')
    dc = {d: shift(color4, v, 'dc' + d) for d, v in DIAG.items()}
    hrun = rasp.categorical(rasp.Aggregate(rasp.Select(hkey, idx, ph), idx)).named('hrun')
    vrun = rasp.categorical(rasp.Aggregate(rasp.Select(vkey, idx, pv), idx)).named('vrun')
    eq = lambda k, q: SEL if k == q else UNSEL
    selH = rasp.Select(hrun, hrun, eq)
    selV = rasp.Select(vrun, vrun, eq)

    if stop == 'runs':
        return rasp.numerical(rasp.Map(lambda v: 0.0 if v == 'no' else 1.0, rasp.categorical(rasp.SequenceMap(lambda a, b: a, hkey, hrun))))
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
    if stop == 'prop': return flags[0]

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
    if stop == 'nbinfo': return rasp.numerical(rasp.Map(lambda v: 1.0 if v == 'E' else 0.0, nbinfo))
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
