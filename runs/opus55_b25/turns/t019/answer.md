```python
prog = r'''
from tracr.rasp import rasp
import math, itertools

MLP_EXACTNESS = 100
NCLS = 13
T_HOPS = 5
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

def cat(x): return rasp.categorical(x)
def num(x): return rasp.numerical(x)

def sel_open():
    return rasp.Select(rasp.indices, rasp.indices, lambda k, q: q < 81 and k in NB[q])
def sel_closed():
    return rasp.Select(rasp.indices, rasp.indices, lambda k, q: q < 81 and (k == q or k in NB[q]))
def sel_hist():
    def p(k, q):
        if q >= 81: return 0.0
        if k in NB[q]: return 1.0
        if k == 81 and len(NB[q]) < 4: return 1.0 + math.log(4 - len(NB[q])) / 100
        return 0.0
    return rasp.Select(rasp.indices, rasp.indices, p)
def kern(q, k, s):
    r1, c1 = divmod(q, 9); r2, c2 = divmod(k, 9)
    return math.exp(-((r1-r2)**2 + (c1-c2)**2) / (2*s*s))
def sel_kernel(s, cutoff=0.02):
    def p(k, q):
        if q >= 81 or k >= 81: return 0.0
        w = kern(q, k, s)
        if w < cutoff: return 0.0
        return 1.0 + math.log(w) / 100
    return rasp.Select(rasp.indices, rasp.indices, p)

# ---------- readout predicates (query = class mixture, key = index role) ----------
def pred_single(k, q):
    if k < NCLS:
        if q == 'n': return 1.0
        return 1.0 if q[1] == k else -BIG
    if k == NCLS: return 0.7
    return 0.0
def pred_pair(k, q):
    if k < NPAIR:
        if q == 'n': return 1.0
        return 1.0 if q[1] in PAIRS[k] else -BIG
    if k == NPAIR: return 0.7
    return 0.0
def pred_upair(k, q):
    if k < NPAIR:
        if q == 'n' or q[0] == 'O': return 1.0
        return 1.0 if q[1] in PAIRS[k] else -BIG
    if k == NPAIR: return 0.7
    return 0.0

# ---------- neighbour multiset prototypes ----------
CATS = ['E', 'P', 'X', 'O1', 'Om']
def catof(v): return 'X' if v in ('X1', 'Xm') else v
PROTOS = [t for t in itertools.product(range(5), repeat=5) if sum(t) == 4 and t[1] <= 2]
C1 = 2.0
def labelA(t):
    nE, nP, nX, nO1, nOm = t
    return (min(nO1, 2), int(nX >= 1), int(nX >= 1 and nX + nP == 4), min(nE, 2))
def pred_proto(k, q):
    if k >= len(PROTOS): return 0.0
    t = PROTOS[k]
    m = [x / 4 for x in t]
    sq = sum(x * x for x in m)
    c = catof(q)
    if c not in CATS: return 0.5
    return C1 * (2 * m[CATS.index(c)] - sq) + 0.5
def pred_yes(target):
    def p(k, q):
        if k == 0: return 3.3 if q == target else 0.1
        if k == 1: return 0.6
        return 0.0
    return p

ZTH, ZC = 0.12, 10.0
def pred_zone(k, q):
    fx = {'X': 1.0, 'O': -2.0}.get(q, 0.0)
    fo = {'O': 1.0, 'X': -2.0}.get(q, 0.0)
    if k == 0: return 0.6 + ZC * (fx - ZTH)
    if k == 1: return 0.6 + ZC * (fo - ZTH)
    if k == 2: return 0.6
    return 0.0

def LV(i):
    if i >= 81: return 3.0
    r, c = divmod(i, 9)
    e = min(r, c, 8 - r, 8 - c)
    return 3.0 + [-2.0, -0.5, 0.5, 0.5, 0.5][e]

TAC_CAP1, TAC_CAP2, TAC_EYE, TAC_SA, TAC_ESC, TAC_ATK = 14, 18, -16, -12, 9, 4
PASSV = 0.0
GAINW = 8.0
SCALE = 2.0

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
    labmap = cat(rasp.Map(lambda k: labelA(PROTOS[k]) if k < len(PROTOS) else labelA(PROTOS[0]), idx)).named('labmap')
    ynmap = cat(rasp.Map(lambda k: 'yes' if k == 0 else 'no', idx)).named('ynmap')
    zmap = cat(rasp.Map(lambda k: ['own', 'opp', 'neu'][k] if k < 3 else 'neu', idx)).named('zmap')
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

    RS1 = cat(rasp.Aggregate(rasp.Select(idx, W, pred_single), rv1)).named('RS1')
    RS2 = cat(rasp.Aggregate(rasp.Select(idx, W, pred_pair), rv2)).named('RS2')
    U = cat(rasp.Aggregate(sel_open(), W)).named('U')
    RU = cat(rasp.Aggregate(rasp.Select(idx, U, pred_upair), rvu)).named('RU')

    def fstA(kd, r):
        if kd == 'X': return 'X1' if r == 'c1' else 'Xm'
        if kd == 'O': return 'O1' if r == 'c1' else 'Om'
        return kd
    def fstB(kd, r):
        if kd == 'X': return 'X2' if r == 'c2' else 'X3'
        if kd == 'O': return 'O2' if r == 'c2' else 'O3'
        return kd
    stA = cat(rasp.SequenceMap(fstA, kind, RS1)).named('stA')
    stB = cat(rasp.SequenceMap(fstB, kind, RS2)).named('stB')
    HA = cat(rasp.Aggregate(sel_hist(), stA)).named('HA')
    HB = cat(rasp.Aggregate(sel_hist(), stB)).named('HB')
    labA = cat(rasp.Aggregate(rasp.Select(idx, HA, pred_proto), labmap)).named('labA')
    escO = cat(rasp.Aggregate(rasp.Select(idx, HA, pred_yes('X1')), ynmap)).named('escO')
    o2O = cat(rasp.Aggregate(rasp.Select(idx, HB, pred_yes('O2')), ynmap)).named('o2O')

    def ftab1(lab, ru):
        capc, xn, eye, nEc = lab
        if capc >= 1: la = 3
        elif xn: la = 1 if ru == 'lo' else 2
        else: la = max(1, min(nEc, 2))
        return (capc, eye, la)
    tab1 = cat(rasp.SequenceMap(ftab1, labA, RU)).named('tab1')
    EO = cat(rasp.SequenceMap(lambda a, b: (a == 'yes', b == 'yes'), escO, o2O)).named('EO')
    def ftab2(s, eo):
        capc, eye, la = s
        esc, o2 = eo
        if capc >= 1: return TAC_CAP2 if capc >= 2 else TAC_CAP1
        if eye: return TAC_EYE
        if la <= 1: return TAC_SA
        return TAC_ESC * int(esc) + TAC_ATK * int(o2)
    tab2 = cat(rasp.SequenceMap(ftab2, tab1, EO)).named('tab2')
    tacP = num(rasp.Map(lambda s: float(max(s, 0)), tab2)).named('tacP')
    tacN = num(rasp.Map(lambda s: float(max(-s, 0)), tab2)).named('tacN')

    # ---------- positional ----------
    InfM = cat(rasp.Aggregate(sel_kernel(1.5), kind)).named('InfM')
    zone = cat(rasp.Aggregate(rasp.Select(idx, InfM, pred_zone), zmap)).named('zone')
    def fz(kd, z):
        if kd == 'E': return z
        if kd == 'P': return 'P'
        return 'S' + kd
    zoneP = cat(rasp.SequenceMap(fz, kind, zone)).named('zoneP')
    GainM = cat(rasp.Aggregate(sel_kernel(1.5), zoneP)).named('GainM')
    gainR = num(rasp.Map(lambda z: {'neu': 1.0, 'opp': 0.5, 'own': 0.15}.get(z, 0.0), GainM)).named('gainR')
    zpen = num(rasp.Map(lambda z: {'own': 5.0, 'opp': 2.0}.get(z, 0.0), zoneP)).named('zpen')
    passv = num(rasp.Map(lambda kd: PASSV if kd == 'P' else 0.0, kind)).named('passv')

    a1 = num(rasp.LinearSequenceMap(tacP, tacN, 1.0, -1.0)).named('a1')
    a2 = num(rasp.LinearSequenceMap(gainR, zpen, GAINW, -1.0)).named('a2')
    a3 = num(rasp.LinearSequenceMap(linev, passv, 1.0, 1.0)).named('a3')
    b1 = num(rasp.LinearSequenceMap(a1, a2, 1.0, 1.0)).named('b1')
    out = num(rasp.LinearSequenceMap(b1, a3, SCALE, SCALE)).named('logit')
    return out
'''
open('/work/program.py','w').write(prog)

helper2 = r'''
import sys, importlib, collections
sys.path.insert(0,'/work')
from tracr.compiler import rasp_to_graph, basis_inference, expr_to_craft_graph, craft_graph_to_model, nodes
from tracr.rasp import rasp
def layer_report(prog_fn):
    out = prog_fn()
    g = rasp_to_graph.extract_rasp_graph(out)
    basis_inference.infer_bases(g.graph, g.sink, {".", "x", "o", "B", "W"}, 82)
    expr_to_craft_graph.add_craft_components_to_rasp_graph(g.graph, bos_dir=__import__('tracr').craft.bases.BasisDirection('tokens','BOS'), mlp_exactness=100)
    alloc = craft_graph_to_model._allocate_modules_to_layers(g.graph, g.sources)
    bylayer = collections.defaultdict(list)
    for nid, l in alloc.items():
        node = g.graph.nodes[nid]
        blk = node.get(nodes.MODEL_BLOCK)
        w = ''
        if blk is not None and hasattr(blk, 'fst'): w = blk.fst.output_space.num_dims
        bylayer[l].append(f"{node[nodes.EXPR].label}{'('+str(w)+')' if w!='' else ''}")
    for l in sorted(bylayer): print(l//2, 'attn' if l%2==0 else 'mlp ', bylayer[l])
'''
open('/work/helper2.py','w').write(helper2)
import sys; sys.path.insert(0,'/work')
import importlib, helper2, program
importlib.reload(program)
helper2.layer_report(program.program)
res = compile_program()
```