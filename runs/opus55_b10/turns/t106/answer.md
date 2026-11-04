62.5% vs strong (Black dropped to 52%) versus 75% in pass 8 — a ~2σ difference, so removing the cut-pattern feature may have hurt (or it's noise). Pass 8's 100M model measured 51.9 s/1000 on the pass machine, too risky for the 60 s limit, so I'll restore cut detection within the slim budget: fetch right/down tokens and the 4 diagonals in idle attention slots (≤3 heads/layer), and schedule the cut-pattern MLPs after the diffusion (via the exact `dly` constant) so they don't break layer condensation.

```python
s = open('/work/go.py').read()
old = s[s.index("    # ---- positional (token based)"):s.index("    def dens(col):")]
new = r'''    # ---- positional (token based)
    tok_d2 = cmap(lambda t: t, cmap(lambda t: t, tok))                  # delay chain (depth 2)
    tok_d3 = cmap(lambda t: t, tok_d2)
    t2 = rasp.Aggregate(rasp.Select(idx, qB, GEQ), tok_d3)             # soft token mix within distance 2
    tadj = rasp.Aggregate(rasp.Select(idx, qA, GEQ), tok_d3)           # soft token mix of on-board neighbours
    def pres(col):
        return lambda v: 1.0 if v == col else (0.05 if v == 'W' else 0.0)
    thr = lambda x: int(x > 0.025)
    adj = smap(lambda a, b: (a, b), cmap(thr, nmap(pres('x'), tadj)), cmap(thr, nmap(pres('o'), tadj)))
    # cutting points: orthogonal + diagonal tokens (heads placed in idle slots, patterns evaluated late)
    dtok = rasp.Aggregate(rasp.Select(idx, qB, LT), tok)                # depth 2 (with ltok, utok)
    rtok = rasp.Aggregate(rasp.Select(idx, qB, GT), tok_d3)             # depth 4
    utok_d5 = cmap(lambda t: t, cmap(lambda t: t, cmap(lambda t: t, utok)))   # depth 5
    dtok_d5 = cmap(lambda t: t, cmap(lambda t: t, cmap(lambda t: t, dtok)))
    nw = rasp.Aggregate(rasp.Select(idx, qA, GT), utok_d5)              # depth 6: token at (r-1, c-1)
    ne = rasp.Aggregate(rasp.Select(idx, qB, GT), utok_d5)              # (r-1, c+1)
    se = rasp.Aggregate(rasp.Select(idx, qB, GT), dtok_d5)              # (r+1, c+1)
    dtok_d6 = cmap(lambda t: t, dtok_d5)
    sw = rasp.Aggregate(rasp.Select(idx, qA, GT), dtok_d6)              # depth 7: (r+1, c-1)
    def pair(a, b):
        return 'XX' if (a == 'x' and b == 'x') else ('OO' if (a == 'o' and b == 'o') else '-')
    def late(x): return smap(lambda v, z: v, x, dly)
    def quad(p, dg):
        if p == 'XX' and dg == 'o': return 'our'
        if p == 'OO' and dg == 'x': return 'their'
        return '-'
    qne = smap(quad, late(smap(pair, utok, rtok)), ne); qnw = smap(quad, late(smap(pair, utok, ltok)), nw)
    qse = smap(quad, late(smap(pair, dtok, rtok)), se); qsw = smap(quad, late(smap(pair, dtok, ltok)), sw)
    def cmb(a, b):
        sa = set(a) if isinstance(a, tuple) else {a}; sb = set(b) if isinstance(b, tuple) else {b}
        return tuple(sorted((sa | sb) - {'-'}))
    cuts = smap(cmb, smap(cmb, qne, qnw), smap(cmb, qse, qsw)).named('cuts')
'''
s = s.replace(old, new)
s = s.replace("""    cutcat = regcat""", """    cutcat = smap(lambda c, r: c + r, smap(lambda c, cont: CUT_VAL(c, cont), cuts, contested), regcat)""")
open('/work/go.py','w').write(s)
import sys; sys.path.insert(0,'/work'); sys.setrecursionlimit(10000)
import importlib, go, estimate; importlib.reload(go)
from tracr.compiler import rasp_to_graph, basis_inference, expr_to_craft_graph, craft_graph_to_model
from tracr.craft import bases, transformers
prog = go.program()
print(estimate.estimate(prog))
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