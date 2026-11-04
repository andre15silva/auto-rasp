Narrow Black losses show a clear pattern: near the end we fill our own territory (scored as "contested" because opponent stones are within distance 2) while the opponent reduces or kills a weak group elsewhere. I'll add a region/territory signal: flood-fill which colors border each empty point's empty region, using the same run-based diffusion (empty points now form runs too), with per-round cleaning. In the late phase, moves inside regions bordered only by one color get pushed below pass.

```python
s = open('/work/go.py').read()
# 1) empty points form runs as well
s = s.replace("""    srow = clean_bool(smap(lambda t, l: (t not in ('x', 'o')) or (t != l), tok, ltok))
    scol = clean_bool(smap(lambda t, u: (t not in ('x', 'o')) or (t != u), tok, utok))""",
"""    srow = clean_bool(smap(lambda t, l: t != l, tok, ltok))
    scol = clean_bool(smap(lambda t, u: t != u, tok, utok))""")
# 2) region border diffusion
s = s.replace("""    sr = clean(smap(stonly, rasp.Aggregate(seedsel, rowE), tok)).named('seed_r')""",
"""    nq2 = cmap(lambda q: NEAR_N2, qA)
    nearone2 = rasp.Aggregate(rasp.Select(idx, nq2, LT), constc).named('nearone2')
    def clean2(x): return smap(cleanf, x, nearone2)
    def gEf(v, t):
        if v == 'P': return 'D' if t in ('B', 'W') else 'Z'
        return 'X' if t == 'x' else ('O' if t == 'o' else None)
    gE = smap(gEf, rowv, tok)
    emonly = lambda v, t: v if t == '.' else 'D'
    sg = clean2(smap(emonly, rasp.Aggregate(seedsel, gE), tok)).named('seed_g')
    sr = clean(smap(stonly, rasp.Aggregate(seedsel, rowE), tok)).named('seed_r')""")
s = s.replace("""        sr = clean(rasp.Aggregate(sel, sr)).named('sr%d' % k)""",
"""        sr = clean(rasp.Aggregate(sel, sr)).named('sr%d' % k)
        sg = clean2(rasp.Aggregate(sel, sg)).named('sg%d' % k)""")
s = s.replace("NEAR_N = 30        # keys averaged for the near-one constant (theta = BOS share)",
              "NEAR_N = 30        # keys averaged for the near-one constant (theta = BOS share)\nNEAR_N2 = 15\nEPS_G = 4e-4")
# region class decode + use in positional tail
s = s.replace("""    cutcat = smap(lambda c, cont: CUT_VAL(c, cont), cuts, contested)""",
"""    cutcat = smap(lambda c, cont: CUT_VAL(c, cont), cuts, contested)
    def gbit(col):
        m = nmap(lambda v: 1.0 if v == col else (EPS_G if v == 'Z' else 0.0), sg)
        return cmap(lambda x: int(x > EPS_G / 2), m)
    region = smap(lambda a, b: (a, b), gbit('X'), gbit('O')).named('region')
    regcat = smap(lambda r, p: TERR_VAL(r, p), region, phase)
    cutcat = smap(lambda c, r: c + r, cutcat, regcat)""")
s = s.replace("""    extra = add(nmap(lambda v: v + 6.0, adjcat), nmap(lambda v: v + 3.0, cutcat))""",
              """    extra = add(nmap(lambda v: v + 6.0, adjcat), nmap(lambda v: v + 12.0, cutcat))""")
s = s.replace("""TRIPLE_CLASS, TRIPLE_REP = build_triple_classes()""", """def TERR_VAL(region, phase):
    hx, ho = region
    if phase == 2 and hx and not ho: return -8.0
    if phase == 2 and ho and not hx: return -6.0
    return 0.0
TRIPLE_CLASS, TRIPLE_REP = build_triple_classes()""")
open('/work/go.py','w').write(s)
import sys; sys.path.insert(0,'/work'); sys.setrecursionlimit(10000)
import importlib, go, estimate
importlib.reload(go)
print(estimate.estimate(go.program()))
from tracr.compiler import rasp_to_graph, basis_inference, expr_to_craft_graph, craft_graph_to_model
from tracr.craft import bases, transformers
prog = go.program()
ex = rasp_to_graph.extract_rasp_graph(prog)
graph, sources, sink = ex.graph, ex.sources, ex.sink
basis_inference.infer_bases(graph, sink, {".","x","o","B","W"}, 82)
expr_to_craft_graph.add_craft_components_to_rasp_graph(graph, bos_dir=bases.BasisDirection("tokens","BOS"), mlp_exactness=1000000)
alloc = craft_graph_to_model._allocate_modules_to_layers(graph, list({id(s): s for s in sources}.values()))
by_layer = {}; heads = {}
for nid, layer in alloc.items():
    blk = graph.nodes[nid].get('MODEL_BLOCK')
    if blk is None: continue
    if isinstance(blk, transformers.MLP): by_layer[layer] = by_layer.get(layer, 0) + blk.fst.output_space.num_dims
    elif isinstance(blk, transformers.SeriesWithResiduals):
        for b in blk.blocks:
            if isinstance(b, transformers.MLP): by_layer[layer+1] = by_layer.get(layer+1, 0) + b.fst.output_space.num_dims
        heads[layer] = heads.get(layer, 0) + 1
    else: heads[layer] = heads.get(layer, 0) + 1
print('layers', max(alloc.values())//2 + 1, 'max mlp', max(by_layer.values()), 'max heads', max(heads.values()))
print(sorted(heads.items()))
```