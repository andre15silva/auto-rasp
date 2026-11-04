The bundled propagation needs a dynamic range of ~1e5 (min surviving value 2.7e-5 after 6 steps), so I'll set MLP_EXACTNESS = 5e5 and scale counts down so other discretizing MLPs stay precise. This reduces data-dependent heads from 50 to 8. Writing v3:

```python
s = open('/work/gonet.py').read()
start = s.index("    ncW = shift(color, ORTH['W'], 'ncW')")
end = s.index("    nbinfo = rasp.categorical(rasp.SequenceMap(nbcls, cnt3, color)).named('nbinfo')")
new_mid = r'''    ncW = shift(color, ORTH['W'], 'ncW')
    ncN = shift(color, ORTH['N'], 'ncN')
    # bundle value: bucket id for empty points, X/O for stones, S for side token, D dummy (unreachable)
    def bvf(t, i):
        if i == 81: return 'S' if t in ('B', 'W') else 'D'
        if t == '.': return bucket(i)
        if t == 'x': return 'X'
        if t == 'o': return 'O'
        return 'D'
    bv = rasp.categorical(rasp.SequenceMap(bvf, tok, idx)).named('bv')
    def pinit(k, q):
        if not isinstance(q, int): return UNSEL
        if q == 81: return SEL if k == 81 else UNSEL
        return SEL if k in ONB[q] else UNSEL
    bund = rasp.categorical(rasp.Aggregate(rasp.Select(idx, idx, pinit), bv)).named('bund0')

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
    for s_ in range(1, N_PROP + 1):
        bund = rasp.categorical(rasp.Aggregate(selH if s_ % 2 == 1 else selV, bund)).named(f'bund{s_}')
    if stop == 'prop': return rasp.numerical(rasp.Map(lambda v: 1 if v == 0 else 0, bund))
    # extraction + threshold
    flags = []
    for h in list(range(NBUCK)) + ['X', 'O']:
        def fx(v, h=h):
            if v == h: return 1
            if v == 'D': return TINY
            return 0
        xh = rasp.numerical(rasp.Map(fx, bund)).named(f'x{h}')
        def gthr(x):
            if abs(x) < 1e-12: return 0
            if abs(x - TINY) < 1e-15: return 1
            return None
        flags.append(rasp.numerical(rasp.Map(gthr, xh)).named(f'f{h}'))
    lv1 = [lsm(flags[2 * i], flags[2 * i + 1], f'sb0_{i}', 0.01, 0.01) for i in range(NBUCK // 2)]
    tot = tree(lv1, 'sb')
    cnt3 = rasp.categorical(rasp.Map(lambda v: min(int(round(v * 100)), 3), tot)).named('cnt3')
'''
s = s[:start] + new_mid + s[end:]
s = s.replace("N_PROP = 6\n", "N_PROP = 6\nTINY = 1.6e-5\n")
# remove obsolete bucket-flag init loop leftover check
open('/work/gonet.py','w').write(s)
open('/work/program.py','w').write('''
import sys
sys.path.insert(0, '/work')
import importlib, gonet
importlib.reload(gonet)
MLP_EXACTNESS = 500000
def program():
    return gonet.build()
''')
import time; t0 = time.time()
r = compile_program(); print('wall', round(time.time()-t0))
```