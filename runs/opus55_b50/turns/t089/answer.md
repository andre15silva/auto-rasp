The path-explosion cost (Σ tip→leaf paths × leaf→all paths) must stay ≲1e8. The feature-decomposed tail multiplied routes ~28×. I'll go back to a v3-style tail (4 routes: pair-of-pairs lookup) with 9 neighbour classes, using a *local* size proxy (a stone has a same-colour neighbour ⇔ its group has ≥2 stones), keep the cheap new branches (false eyes, influence, Tromp-Taylor pass), and check the path cost before compiling.

```python
src = open('/work/gonet4.py').read()
# bundle back to colour tags for stones
src = src.replace("""        if t == 'x': return ('X', bucket(i))
        if t == 'o': return ('O', bucket(i))""", """        if t == 'x': return 'X'
        if t == 'o': return 'O'""")
old = src[src.index("    fXm = [extract"):src.index("    cnt3 = cat(")]
src = src.replace(old, """    fanyX = extract(bund, (lambda v: v == 'X'), 'anyX')
    fanyO = extract(bund, (lambda v: v == 'O'), 'anyO')
    libn = tree(fb, 'sl', 0.01)
""")
old = src[src.index("    szX = cat(M(szcls, SX), 'szX')"):src.index("    if stop == 'nbinfo'")]
src = src.replace(old, """    # local size proxy: stone has a same-coloured orthogonal neighbour <=> group size >= 2
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
""")
old = src[src.index("    # ---- tactical features at empty points"):src.index("    def atk(o2, l):")]
src = src.replace(old, """    # ---- tactical evaluation at empty points (pair-of-pairs lookup)
    nbs = {d: shift(nbinfo, v, 'nb' + d) for d, v in ORTH.items()}
    srt = lambda a, b: tuple(sorted((a, b)))
    pNS = cat(SM(srt, nbs['N'], nbs['S']), 'pNS')
    pWE = cat(SM(srt, nbs['W'], nbs['E']), 'pWE')
    t1c = cat(SM(lambda a, b: tactical(list(a) + list(b)), pNS, pWE), 't1c')
    t1 = num(M(lambda v: v, t1c), 't1')
    if stop == 't1': return t1
""")
old = src[src.index("    def atk(o2, l):"):src.index("    # ---- eyes")]
src = src.replace(old, "")
src = src.replace("""    s12 = lsm(t1, t2, 's12')
    s34 = lsm(t3, t4, 's34')
    s56 = lsm(t5, t6, 's56')
    s1234 = lsm(s12, s34, 's1234')
    return lsm(s1234, s56, 'logits')""", """    s14 = lsm(t1, t4, 's14')
    s56 = lsm(t5, t6, 's56')
    return lsm(s14, s56, 'logits')""")
src = src.replace("    srt = lambda a, b: tuple(sorted((a, b)))\n    oNS = cat(SM(srt, ncN, ncS), 'oNS')", "    oNS = cat(SM(srt, ncN, ncS), 'oNS')")
tact = r'''
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
'''
src = src.replace("# ---------------- tables", tact + "\n# ---------------- tables")
src = src.replace("""TACT = {
    'cap': {1: 8.0, 2: 9.5, 3: 11.0, 4: 12.5}, 'capsave': 2.0,
    'esc3': {1: 7.0, 2: 8.5, 3: 10.0, 4: 11.5}, 'esc2': {1: 2.0, 2: 3.0, 3: 4.0, 4: 5.0}, 'escf': -5.0,
    'sui': -10.0, 'sa': {1: -6.0, 2: -8.0, 3: -10.0, 4: -12.0}, 'fill2': -1.0, 'noE': -2.0,
    'def2': {1: 0.8, 2: 1.5, 3: 2.5, 4: 3.5},
    'atari': {1: 1.5, 2: 2.0, 3: 2.5, 4: 3.0},
}""", """TACT = {'cap_s': 8.0, 'cap_m': 11.0, 'cap_extra': 1.5, 'capsave': 2.0,
        'esc3': {'s': 6.5, 'm': 9.0}, 'esc2': {'s': 1.5, 'm': 3.5}, 'escf': -5.0,
        'sui': -10.0, 'sa_s': -6.0, 'sa_m': -9.0, 'fill2': -1.0, 'noE': -2.0,
        'atari': 2.0, 'def2': 1.5}""")
open('/work/gonet4.py','w').write(src)
import sys, importlib, collections
sys.path.insert(0, '/work')
import networkx as nx
from tracr.compiler import rasp_to_graph, nodes
import gonet4; importlib.reload(gonet4)
def path_cost(prog):
    ext = rasp_to_graph.extract_rasp_graph(prog)
    G = ext.graph
    src_ = collections.Counter(s[nodes.ID] for s in ext.sources)
    order = list(nx.topological_sort(G)); pout = {}
    for n in reversed(order): pout[n] = 1 + sum(pout[m] for m in G.successors(n))
    return sum(c * pout[l] for l, c in src_.items())
print('cost %.3g' % path_cost(gonet4.build()))
```