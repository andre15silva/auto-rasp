75% vs strong (up from ~67%), no repetition losses, fewer stones lost. However, the pass machine measured 51.9 s/1000 — too close to the 60 s limit. I need a safer margin. Plan: drop the cut-pattern feature (no measurable gain in pass 5; costs 6 heads and ~50 dims), restore the single soft-adjacency head, and split the 4 neighbor fetches across levels (cN/cS, then cW, then cE, matching when the multiset chain needs them) to reach ≤3 heads per layer.

```python
s = open('/work/go.py').read()
start = s.index("    # ---- positional (token based, scheduled into idle attention slots)")
end = s.index("    def dens(col):")
new = '''    # ---- positional (token based)
    tok_d2 = cmap(lambda t: t, cmap(lambda t: t, tok))                  # delay chain (depth 2)
    t2 = rasp.Aggregate(rasp.Select(idx, qB, GEQ), tok_d2)             # soft token mix within distance 2
    tok_d3 = cmap(lambda t: t, tok_d2)
    tadj = rasp.Aggregate(rasp.Select(idx, qA, GEQ), tok_d3)           # soft token mix of on-board neighbours
    def pres(col):
        return lambda v: 1.0 if v == col else (0.05 if v == 'W' else 0.0)
    thr = lambda x: int(x > 0.025)
    adj = smap(lambda a, b: (a, b), cmap(thr, nmap(pres('x'), tadj)), cmap(thr, nmap(pres('o'), tadj)))
'''
s = s[:start] + new + s[end:]
s = s.replace("""    cutcat = smap(lambda c, cont: CUT_VAL(c, cont), cuts, contested)
""", "")
s = s.replace("""    cutcat = smap(lambda c, r: c + r, cutcat, regcat)""", """    cutcat = regcat""")
# split the neighbour fetches over three levels
s = s.replace("""    cW = rasp.Aggregate(rasp.Select(idx, qA, GT), cst).named('cW')
    cE = rasp.Aggregate(rasp.Select(idx, qB, GT), cst).named('cE')""",
"""    cst_d1 = cmap(lambda c: c, cst)
    cst_d2 = cmap(lambda c: c, cst_d1)
    cW = rasp.Aggregate(rasp.Select(idx, qA, GT), cst_d1).named('cW')
    cE = rasp.Aggregate(rasp.Select(idx, qB, GT), cst_d2).named('cE')""")
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
print(sorted(by_layer.items()))
```